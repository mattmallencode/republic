"""
    Attribution: 
        1. Fire SVG made by made by Deepak K Vijayan (2xsamurai). Available from: https://codepen.io/2xsamurai/pen/EKpYM". Logo animation and form animation were made by me.
        2. "round_up" function wirtten by Priyankur Sarkar. AVailable from: https://www.knowledgehut.com/blog/programming/python-rounding-numbers
        3. Icons used in navbar are free even without attribution. Available from: https://uxwing.com/
        4. Favicon is from the open source project Twemoji. 
           Licensed under CC-BY 4.0. 
           Twemoji: https://twemoji.twitter.com/ 
           CC-BY 4.0 License: https://creativecommons.org/licenses/by/4.0/
        5. Borrowed some CSS from Stack Overflow to center placeholder text in form fields. Available from: https://stackoverflow.com/questions/7381446/center-html-input-text-field-placeholder
        6. Borrowed some CSS from Stack Overflow to brighten anchor tags on hover. Available from: https://stackoverflow.com/questions/16178382/css-lighten-an-element-on-hover
        7. Borrowed some CSS to make form labels accessible to screen readers. Available from: https://webaim.org/techniques/css/invisiblecontent/
        8. Borrowed some CSS to fix issues with safari mobile. Available from: https://stackoverflow.com/questions/50475114/when-rotating-an-iphone-x-to-landscape-white-space-appears-to-the-left-and-belox
        9. Borrowed some CSS to fix scrolling issues on mobile. Available from: https://css-tricks.com/css-fix-for-100vh-in-mobile-webkit/
        10. Borrowed some JavaScript from Stack Overflow to fix HTML validation issues due to blank action attribute. Available from: https://stackoverflow.com/questions/32491347/bad-value-for-attribute-action-on-element-form-must-be-non-empty/32491636
        11. Borrowed some JavaScript from Stack Overflow to keep scroll at the buttom on the forum. Available from:  https://stackoverflow.com/questions/3842614/how-do-i-call-a-javascript-function-on-page-load
        12. Borrowed some Javascript from Stack Overflow to force refresh on the chat page. Available from: https://stackoverflow.com/questions/32913226/auto-refresh-page-every-30-seconds
        13. All page transition animations were made using the swup page transition library. Available from: https://swup.js.org/
        14. Font used is Roboto Mono. Available from: https://fonts.google.com/specimen/Roboto+Mono?preview.text_type=custom

    Admin access:
        1. Admin user_id is "admin".
        2. Admin password is "keen/nimble_SALSA".
        3. The admin portal can be accessed at the route "/admin".

    Test acocunts (Feel free to make your own.):
        1. user_id: "cartwheelkitten", password: "supercsecret" (User is banned).
        2. user_id: "floralpelicanfly", password: "superfsecret".
        3. user_id: "unforgivenbeans", password: "superusecret".
        4. user_id: "spinachstandby", password: "superssecret".
        5. user_id: "fitnessjuice", password: "superfsecret".
        6. user_id: "departed", password: "superdsecret".
        7. user_id: "notorious", password: "supernsecret".
        8. user_id: "doughnutwalrus", password: "superdsecret".
        9. user_id: "snake", password: "superssecret".
        10. user_id: "birthdaycake", password: "superbsecret". 
"""

from flask import Flask, render_template, session, g, redirect, url_for, request
from database import get_db, close_db
from forms import SignInForm, RegistrationForm, ChatForm, SellForm, ColorForm, TaxForm, LimitForm, AdminForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import math

app = Flask(__name__)
app.config["SECRET_KEY"] = "demistifyeasypetenimblesauce"


@app.teardown_appcontext
def close_db_at_end_of_request(e=None):
    """
    Closes the connection to the database at the end of a user request
    """
    close_db(e)


@app.before_request
def load_logged_in_user():
    """
    Creates a global variable called user that was stored in the user's session once they logged in.
    ALso creates global variables for the site's colour pallete.
    """
    g.user = session.get("user_id", None)
    db = get_db()
    # Creates a global colour variables so they can be inserted into CSS variables in the Jinja2 templates.
    colors = db.execute("SELECT proposal_value FROM policies WHERE proposal_type = 'color'").fetchone()[
        "proposal_value"]
    # Since a color code in hex is 7 characters (including the #), index slicing is used to parse the color data.
    g.maincolor = colors[0:7]
    g.secondcolor = colors[7:14]
    g.textcolor = colors[14:21]


def login_required(view):
    """
    Redirects the user to the login page if they aren't logged in.
    Also saves what page the user was tyring to access so they can be redirected there once they've been authenticated.
    If the user is banned they are returned to the login page.
    """
    @ wraps(view)
    def wrapped_view(**kwargs):
        db = get_db()
        if g.user is None:

            return redirect(url_for("login", next=request.url))
        if db.execute("""SELECT isBanned FROM users WHERE user_id = ? """, (g.user,)).fetchone()["isBanned"] == 1:
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view


@ app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user authentication.
    The hash of the password the user entered is compared to the hash in the database.
    Also saves the user_id in the user's session.
    """
    form = SignInForm()
    banned = None
    reason = None
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        user = db.execute("""SELECT * FROM users
                    where user_id = ?;""", (user_id,)).fetchone()
        if user is None:
            form.user_id.errors.append("Unkown user id")
        elif not check_password_hash(user["password"], password):
            form.password.errors.append("Incorrect password!")
        elif user["isBanned"] == 1:
            banned = "You have been banned"
            reason = user["bannedReason"]
        else:
            session.clear()
            session["user_id"] = user_id
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("chat")
            return redirect(next_page)
    return render_template("login.html", form=form, maincolor=g.maincolor, secondcolor=g.secondcolor, textcolor=g.textcolor, banned=banned, reason=reason)


@ app.route("/", methods=["GET", "POST"])
@ login_required
def chat():
    """
    This is the route for the chat room / public forum.
    Since it doesn't make use of web sockets it isn't an instant messaging room.
    Javascript is used to refresh the page every 30 seconds.
    Jinja2 logic is used to distinguish the user's messages from the messages of others using CSS.
    """
    db = get_db()
    form = ChatForm()
    # Fetches what the chat limit currently is from the database.
    chat_limit = int(db.execute(
        """SELECT proposal_value FROM policies WHERE proposal_type = 'limit'""").fetchone()["proposal_value"])
    messages = db.execute(""" SELECT * FROM chats """).fetchall()
    if form.validate_on_submit():
        message = form.message.data
        db.execute(
            """INSERT INTO chats(user_id, message) VALUES(?, ?)""", (g.user, message))
        db.commit()
        messages = db.execute("""SELECT * FROM chats """).fetchall()
        # Checks to see if the number of chats in the database has exceeded the given limit once the user submits their message.
        # The oldest message is culled by ordering the messages by descending order of ID and limiting the query to the chat's limit.
        if len(messages) >= chat_limit:
            db.execute(
                """DELETE from chats WHERE message_id NOT IN (SELECT message_id FROM chats ORDER BY message_id DESC LIMIT ?)""", (chat_limit,))
            db.commit()
        return redirect(url_for("chat"))
    return render_template("index.html", form=form, messages=messages, user_id=g.user, maincolor=g.maincolor, secondcolor=g.secondcolor, textcolor=g.textcolor, chat_limit=chat_limit)


@app.route("/shop", methods=["GET", "POST"])
@login_required
def shop():
    """
    This is the route for the shop area.
    This is where users can buy hyperlinks that are being sold by other users.
    The hyperlink for each listing is stored in the database but is hidden from users as it is ommitted from the Jinja2 template.
    """
    db = get_db()
    boughtlinks = db.execute(
        """SELECT listing_id FROM boughtlinks WHERE user_id= ?""", (g.user,)).fetchall()
    boughtlinksList = []
    # Checks to see what links this user has bought in the past. Then use Jinja2 logic to display "bought" rather than buy for that user.
    # Also uses Jinja2 logic to display "your listing" if the seller_id is the user_id
    for boughtlink in boughtlinks:
        boughtlinksList.append(boughtlink["listing_id"])
    listings = db.execute(
        """SELECT * FROM listings ORDER BY listing_id DESC; """).fetchall()
    balance = db.execute(
        """SELECT tulips FROM users WHERE user_id= ?""", (g.user,)).fetchone()["tulips"]
    return render_template("shop.html", listings=listings, balance=balance, boughtlinksList=boughtlinksList, user_id=g.user, maincolor=g.maincolor, secondcolor=g.secondcolor, textcolor=g.textcolor)


@app.route("/buy/<int:listing_id>", methods=["GET", "POST"])
@login_required
def buy(listing_id):
    """
    This is the route that a user can use to buy a hyperlink and store it in their cart.
    """
    db = get_db()
    # Creates a list of the links the user has already bought
    boughtlinks = db.execute(
        """SELECT listing_id FROM boughtlinks WHERE user_id= ?""", (g.user,)).fetchall()
    boughtlinksList = []
    for boughtlink in boughtlinks:
        boughtlinksList.append(boughtlink["listing_id"])
    # Works out the price, the id of the user selling the link, the seller's balance and how much tax will be owed on this sale if any.
    price = db.execute(
        """SELECT price FROM listings WHERE listing_id= ?""", (listing_id,)).fetchone()["price"]
    seller_id = db.execute(
        """SELECT seller_id FROM listings WHERE listing_id= ?""", (listing_id,)).fetchone()["seller_id"]
    seller_balance = db.execute(
        """SELECT tulips FROM users WHERE user_id= ?""", (seller_id,)).fetchone()["tulips"]
    tax = int(db.execute(
        """SELECT proposal_value FROM policies WHERE proposal_type = 'tax'""").fetchone()["proposal_value"])
    tax = price * (tax/100)
    db.execute("""UPDATE treasury SET tulips=tulips + ?""", (tax,))
    db.commit()
    # Increase the sellers balance by the price of the link less the tax owed.
    seller_balance += (price - tax)
    balance = db.execute(
        """SELECT tulips FROM users WHERE user_id= ?""", (g.user,)).fetchone()["tulips"]
    # If the link the user is trying to buy is one they themselves are selling or if they can't afford the link or if they have already bought it then redirect them to the shop.
    if seller_id == g.user or price > balance or listing_id in boughtlinksList:
        return redirect(url_for("shop"))
    # If the user hasn't been redirected because none of the above is true then update the user's bought links, the seller's balance and the treasury.
    db.execute(
        """INSERT INTO boughtlinks(user_id, listing_id) VALUES(?, ?)""", (g.user, listing_id))
    balance -= price
    db.execute("""UPDATE users SET tulips= ? WHERE user_id= ?""",
               (seller_balance, seller_id))
    db.execute("""UPDATE users SET tulips= ? WHERE user_id= ?""",
               (balance, g.user))
    db.commit()
    return redirect(url_for("shop"))


@ app.route("/boughtlinks", methods=["GET", "POST"])
@ login_required
def boughtlinks():
    """
    This is the route to display the user's cart / the links they have bought.
    Unlike the shop route the hyperlink of any listing the user has bought is not ommitted using Jinja2 logic so they can visit the links they have bought.
    """
    db = get_db()
    balance = db.execute(
        """SELECT tulips FROM users WHERE user_id= ?""", (g.user,)).fetchone()["tulips"]
    boughtlinks = db.execute(
        """SELECT * FROM listings WHERE listing_id IN(SELECT listing_id FROM boughtlinks WHERE user_id= ?)""", (g.user,)).fetchall()
    return render_template("boughtlinks.html", boughtlinks=boughtlinks, balance=balance, maincolor=g.maincolor, secondcolor=g.secondcolor, textcolor=g.textcolor)


@ app.route("/sell", methods=["GET", "POST"])
@ login_required
def sell():
    """
    This is the route a user can use to post a listing on the market.
    """
    form = SellForm()
    db = get_db()
    tax = db.execute(
        """SELECT proposal_value FROM policies WHERE proposal_type = 'tax'""").fetchone()["proposal_value"]
    balance = db.execute(
        """SELECT tulips FROM users WHERE user_id= ?""", (g.user,)).fetchone()["tulips"]
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        price = float(round(form.price.data, 2))
        link = form.link.data
        db.execute(
            """INSERT INTO listings(title, description, price, link, seller_id) VALUES(?, ?, ?, ?, ?); """, (title, description, price, link, g.user))
        db.commit()
        return redirect(url_for("shop"))
    return render_template("postlink.html", form=form, balance=balance, maincolor=g.maincolor, secondcolor=g.secondcolor, textcolor=g.textcolor, tax=tax)


@ app.route("/register", methods=["GET", "POST"])
def register():
    """
    This is the route where users can register.
    Each user starts off with a balance of 1000 students and a blank "votes" string.
    Users are not an admin  or banned by default.s
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        password2 = form.password2.data
        password2 = password2
        db = get_db()
        # Extra if statement to check to see if it's a duplicate user
        if db.execute("""SELECT * FROM users WHERE user_id= ?""", (user_id,)).fetchone() is not None:
            form.user_id.errors.append("User id already exists!")
        else:
            db.execute(
                """INSERT INTO users(user_id, password, tulips, isAdmin, isBanned, bannedReason) VALUES(?, ?, ?, ?, ?, ?); """, (
                    user_id, generate_password_hash(password), 1000.0, 0, 0, ""))
            db.execute(
                """INSERT INTO votes(user_id, votes) VALUES(?, ?); """, (user_id, ""))
            db.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=form, maincolor=g.maincolor, secondcolor=g.secondcolor, textcolor=g.textcolor)


@ app.route("/about", methods=["GET", "POST"])
def about():
    """
    This is the route that displays the website's "about page"
    """
    return render_template("about.html", maincolor=g.maincolor, secondcolor=g.secondcolor, textcolor=g.textcolor)

# Start of function written by Priyankur Sarkar


def round_up(n, decimals=0):
    """
    This function rounds up rather than down.
    This is to avoid Python's default behaviour of rounding down when a number is x.5 when voting thresholds are calculated.
    """
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

# End of function written by Priyankur Sarkar


@ app.route("/voting", methods=["GET", "POST"])
@ login_required
def voting():
    """
    This route displays the policies that are currently in place and allows users to upvote or downvote proposals.
    """
    db = get_db()
    treasury = db.execute(
        """SELECT tulips FROM treasury""").fetchone()["tulips"]
    chat_limit = int(db.execute(
        """SELECT proposal_value FROM policies WHERE proposal_type = 'limit'""").fetchone()["proposal_value"])
    tax = db.execute(
        """SELECT proposal_value FROM policies WHERE proposal_type = 'tax'""").fetchone()["proposal_value"]
    # Banned users are excluded from the user count.
    user_count = db.execute(
        """SELECT COUNT(user_id) FROM users WHERE isBanned = 0""").fetchone()["COUNT(user_id)"]
    threshold = user_count / 2
    # If there's an event number of users then a majority is half the users + 1, else it's half the users rounded up to the nearest number.
    if user_count % 2 == 0:
        threshold += 1
    else:
        # The round_up function is used rather than round() to avoid Python rounding down. The threshold is the number of users divided by 2 rounding to the next largest number if the number is a decimal.
        threshold = int(round_up(threshold))
    # Parsing the user's votes using the split method. Voting is explained in comments in the "vote" route.
    user_votes = db.execute(
        """SELECT votes FROM votes WHERE user_id= ?""", (g.user,)).fetchone()["votes"].split(",")
    proposals = db.execute(
        """SELECT * FROM proposals ORDER BY votes DESC""").fetchall()
    return render_template("voting.html", proposals=proposals, maincolor=g.maincolor, secondcolor=g.secondcolor, textcolor=g.textcolor, user_votes=user_votes, threshold=threshold, treasury=treasury, tax=tax, chat_limit=chat_limit)


@ app.route("/propose", methods=["GET", "POST"])
@ login_required
def propose():
    """
    This is the route where a user can propose a policy change.
    All forms are displayed at once and can be toggled to display by the user using Javascript.
    To avoid validation errors from having multiple forms displayed at once, error handling is used.
    All "proposal_value"s are stored as SQL TEXT data types. This works fine for the tax and chat limit figures as they can be cast as integers by Python.
    The color form is different however as the form is handling 3 values at once. The 3 colors are all concatonated onto one string which can then be parsed to extract the individual colors later using index slicing.
    The maincolor goes first, then the secondcolor, and finally the textcolor. Each hex color code is 7 characters long (including the #).
    """
    color_form = ColorForm()
    tax_form = TaxForm()
    limit_form = LimitForm()
    if color_form.validate_on_submit():
        try:
            maincolor = request.form["maincolor"]
            secondcolor = request.form["secondcolor"]
            textcolor = request.form["textcolor"]
            proposal_value = maincolor + secondcolor + textcolor
            proposal_type = "color"
            db = get_db()
            db.execute("""INSERT INTO proposals(proposal_type, proposal_value, votes) VALUES(?, ?, ?)""",
                       (proposal_type, proposal_value, 0))
            db.commit()
            return redirect(url_for("voting"))
        except:
            pass
    if tax_form.validate_on_submit():
        try:
            proposal_value = str(tax_form.salestax.data)
            proposal_type = "tax"
            db = get_db()
            db.execute("""INSERT INTO proposals(proposal_type, proposal_value, votes) VALUES(?, ?, ?)""",
                       (proposal_type, proposal_value, 0))
            db.commit()
            return redirect(url_for("voting"))
        except:
            pass
    if limit_form.validate_on_submit():
        try:
            proposal_value = str(limit_form.limit.data)
            proposal_type = "limit"
            db = get_db()
            db.execute("""INSERT INTO proposals(proposal_type, proposal_value, votes) VALUES(?, ?, ?)""",
                       (proposal_type, proposal_value, 0))
            db.commit()
            return redirect(url_for("voting"))
        except:
            pass
    return render_template("makeproposal.html", color_form=color_form, tax_form=tax_form, limit_form=limit_form, maincolor=g.maincolor, secondcolor=g.secondcolor, textcolor=g.textcolor)


@ app.route("/vote/<string:proposal_id>", methods=["GET", "POST"])
@ login_required
def vote(proposal_id):
    """
    This is the route that handles user votes. Votes work on an upvote and downvote system.
    Users can also withdraw having any input on a given proposal by clicking the given vote button again.

    Voting works as follows:

    Each proposal has a given id, when a user votes their vote is recorded with their id in the following format [proposal_id] + [y/n], y = an upvote n = a downvote.
    Each user therefor as a string consisting of all of the votes they have issued on the platform which we can then iterate over to parse.
    Each vote in the string is seperated by a "," which then makes it easy to parse all of the user's voting data using a for loop.

    Users can change the colour scheme of the website, how much sales tax is charged in the market and what the chat limit should be on the forum.
    Any proposal that gets a majority vote is implemented automatically without need for admin inteference as these variables are fetched from the database.
    The voting system is a sort of smart contract that is self executing. The only pitfall in this regard is that since the website is centralised then admins can make executive decisions and rollback democractic choices.
    """
    db = get_db()
    # Banned users are excluded from the user count
    user_count = db.execute(
        """SELECT COUNT(user_id) FROM users WHERE isBanned = 0""").fetchone()["COUNT(user_id)"]
    # If there's an event number of users then a majority is half the users + 1, else it's half the users rounded up to the nearest number.
    threshold = user_count / 2
    if user_count % 2 == 0:
        threshold += 1
    else:
        # The round_up function is used rather than round() to avoid Python rounding down. The threshold is the number of users divided by 2 rounding to the next largest number if the number is a decimal.
        threshold = round_up(threshold)
    user_votes = db.execute(
        """SELECT votes FROM votes WHERE user_id= ?""", (g.user,)).fetchone()["votes"].split(",")
    proposal_id_sql = proposal_id[0:-1]
    user_votes = db.execute(
        """SELECT votes FROM votes WHERE user_id= ?""", (g.user,)).fetchone()["votes"].split(",")
    choice = proposal_id[-1]
    # Check to see if the user has already voted this way on this given proposal before
    if proposal_id not in user_votes:
        # User has not voted this way on this given proposal before.
        if choice == "y":
            # User wants to vote yes on this proposal.
            # If they have voted no on this proposal before but now want to vote yes then remove their no vote from their votes string and increase the vote tally by 1 to cancel out that downvote.
            if proposal_id_sql + "n" in user_votes:
                db.execute(
                    """UPDATE votes SET votes=REPLACE(votes, ? || "n,", "") WHERE user_id= ?""", (proposal_id_sql, g.user))
                db.execute(
                    """UPDATE proposals SET votes=votes + 1 WHERE proposal_id= ?""", (proposal_id_sql,))
                db.commit()
            # Increase the vote tally by 1, irrespective of whether the user had originally voted no on this proposal.
            db.execute("""UPDATE votes SET votes=votes || ? WHERE user_id= ?""",
                       (proposal_id + ",", g.user))
            db.execute(
                """UPDATE proposals SET votes=votes + 1 WHERE proposal_id= ?""", (proposal_id_sql,))
            db.commit()
        else:
            # User wants to vote no on this proposal.
            # If they have voted yes on this proposal before but now want to vote no then remove their yes vote from their votes string and decrease the vote tally by 1 to cancel out that upvote.
            if proposal_id_sql + "y" in user_votes:
                db.execute(
                    """UPDATE votes SET votes=REPLACE(votes, ? || "y,", "") WHERE user_id= ?""", (proposal_id_sql, g.user))
                db.execute(
                    """UPDATE proposals SET votes=votes - 1 WHERE proposal_id= ?""", (proposal_id_sql,))
                db.commit()
            # Decrease the vote tally by 1, irrespective of whether the user had originally voted no on this proposal.
            db.execute("""UPDATE votes SET votes=votes || ? WHERE user_id= ?""",
                       (proposal_id + ",", g.user))
            db.execute(
                """UPDATE proposals SET votes=votes - 1 WHERE proposal_id= ?""", (proposal_id_sql,))
            db.commit()
    else:
        # User has voted this way on the proposal before i.e. they want to cancel out their vote and withdraw their opinion from this proposal.
        if choice == "y":
            # If the user wants to cancel out a yes vote then remove the yes vote from the user's votes string and decrease the proposal's votes by 1.
            db.execute(
                """UPDATE votes SET votes=REPLACE(votes, ? || "y,", "") WHERE user_id= ?""", (proposal_id_sql, g.user))
            db.execute(
                """UPDATE proposals SET votes=votes - 1 WHERE proposal_id= ?""", (proposal_id_sql,))
            db.commit()
        else:
            # If the user wants to cancel out a no vote then remove the no vote from the user's votes string and increase the proposal's votes by 1.
            db.execute(
                """UPDATE votes SET votes=REPLACE(votes, ? || "n,", "") WHERE user_id= ?""", (proposal_id_sql, g.user))
            db.execute(
                """UPDATE proposals SET votes=votes + 1 WHERE proposal_id= ?""", (proposal_id_sql,))
            db.commit()
    proposal = db.execute(
        """SELECT * FROM proposals WHERE proposal_id= ?""", (proposal_id_sql,)).fetchone()
    # If the proposal has passed the majority threshold then implement it as a policy.
    if threshold <= proposal["votes"]:
        db.execute("""UPDATE policies SET proposal_value= ? WHERE proposal_type= ?""",
                   (proposal["proposal_value"], proposal["proposal_type"]))
        db.execute("""DELETE FROM proposals WHERE proposal_id= ?""",
                   (proposal["proposal_id"],))
        db.commit()
    # If the majority of users have voted no on a proposal then remove it from the database.
    if proposal["votes"] <= threshold * -1:
        db.execute("""DELETE FROM proposals WHERE proposal_id= ?""",
                   (proposal["proposal_id"],))
        db.commit()
    return redirect(url_for('voting'))


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    """
    This is the route for the admin portal.
    Admin status is stored in session but the user must also enter in the admin password to submit a command.
    The admin can ban any user but must give a reason for doing so.
    The ban/unban commands work as follows "[ban/unban] [user_id] [reason].
    If the admin fails to start the command with ban or unban, fails to provide a valid user_id or a reason then the command is not submmitted.
    Users who have already beenn banned/unbanned will not be banned/unbanned again.
    If the user has been successfully banned then their chats and market listings are also purged.
    Other data isn't deleted because:
        A) Users even if they've violated rules should be able to retrieve the links they bought if they request it.
        B) Unlike other data such as policy votes, chats and listings can be malicious in nature e.g. scam listings and/or abusive messages.
    """
    db = get_db()
    outcome = None
    if db.execute("""SELECT * FROM users WHERE user_id = ? AND isAdmin = 1""", (g.user,)).fetchone() is None:
        return redirect(url_for("chat"))
    form = AdminForm()
    if form.validate_on_submit():
        password = form.password.data
        admin = db.execute(
            """SELECT * FROM users WHERE user_id = 'admin';""").fetchone()["password"]
        if not check_password_hash(admin, password):
            outcome = "That's not the admin password!"
            return render_template("portal.html", form=form, outcome=outcome)
        command = form.command.data.split(" ")
        reason = ""
        try:
            if command[0] != "ban" or command[0] != "unban":
                outcome = "Command must begin with 'ban' or 'unban'!"
            if db.execute("""SELECT user_id FROM users WHERE user_id = ?""", (command[1],)).fetchone() is None:
                outcome = "User does not exist!"
            else:
                if command[0] == "ban":
                    try:
                        if db.execute("""SELECT isBanned FROM users where user_id = ?""", (command[1],)).fetchone()["isBanned"] == 1:
                            outcome = "User is already banned!"
                        else:
                            if command[2] == "":
                                outcome = "Can't leave ban reason blank!"
                            else:
                                for word in command[2::]:
                                    reason = reason + " " + word
                                    db.execute(
                                        """UPDATE users SET isBanned = 1, bannedReason = ? WHERE user_id = ?""", (reason.lower(), command[1]))
                                    db.commit()
                                    db.execute(
                                        """DELETE FROM chats WHERE user_id = ?""", (command[1],))
                                    db.execute(
                                        """DELETE FROM listings WHERE seller_id = ?""", (command[1],))
                                    db.commit()
                                    outcome = "User has been banned!"
                    except:
                        outcome = "Invalid command!"
                if command[0] == "unban":
                    try:
                        if db.execute("""SELECT isBanned FROM users where user_id = ?""", (command[1],)).fetchone()["isBanned"] == 0:
                            outcome = "User already isn't banned!"
                        else:
                            db.execute(
                                """UPDATE users SET isBanned = 0, bannedReason = "" WHERE user_id = ?""", (command[1],))
                            db.commit()
                            outcome = "User has been unbanned!"
                    except:
                        outcome = "Invalid command!"
        except:
            outcome = "Invalid command!"
    return render_template("portal.html", form=form, outcome=outcome, maincolor=g.maincolor, secondcolor=g.secondcolor, textcolor=g.textcolor)
