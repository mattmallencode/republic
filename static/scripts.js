/*
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
*/

const options = {
    containers: [".swup"],
    linkSelector: "a:not([data-no-swup])",
};

const swup = new Swup(options);

/* Start of javascript to force page refresh */

swup.on('pageView', function () {

    if (document.getElementById("chat")) {
        var element = document.getElementById("chat");
        element.scrollTop = element.scrollHeight;
        window.setTimeout(function () {
            window.location.reload();
        }, 30000);
    }
});

if (document.getElementById("chat")) {
    document.getElementById("chat").addEventListener("load", refresh_window());
    document.onload = updateScroll()
}
/* End of javascript to force page refresh */

function showColours() {
    document.getElementById("colorform").style.display = "flex";
    document.getElementById("taxform").style.display = "none";
    document.getElementById("limitform").style.display = "none";
    document.getElementById("colourbutton").style.filter = "brightness(75%)";
    document.getElementById("taxbutton").style.filter = "brightness(100%)";
    document.getElementById("limitbutton").style.filter = "brightness(100%)";
};

function showTax() {
    document.getElementById("taxform").style.display = "flex";
    document.getElementById("colorform").style.display = "none";
    document.getElementById("limitform").style.display = "none";
    document.getElementById("colourbutton").style.filter = "brightness(100%)";
    document.getElementById("taxbutton").style.filter = "brightness(75%)";
    document.getElementById("limitbutton").style.filter = "brightness(100%)";

};

function showLimit() {
    document.getElementById("limitform").style.display = "flex";
    document.getElementById("taxform").style.display = "none";
    document.getElementById("colorform").style.display = "none";
    document.getElementById("colourbutton").style.filter = "brightness(100%)";
    document.getElementById("taxbutton").style.filter = "brightness(100%)";
    document.getElementById("limitbutton").style.filter = "brightness(75%)";
};

/* start of javascript to update scrolling */

function updateScroll() {
    var element = document.getElementById("chat");
    element.scrollTop = element.scrollHeight;
};

/* end of javascript to update scrolling */

/* Start of javascript to force page refresh */


function refresh_window() {
    window.setTimeout(function () {
        window.location.reload();
    }, 30000);
}
/* End of javascript to force page refresh */