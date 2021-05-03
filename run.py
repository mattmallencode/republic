#!/usr/local/bin/python3.8
from app import app
from wsgiref.handlers import CGIHandler
import cgitb
print("Content-Type: text/html\n\r\n")
cgitb.enable(display=1, format="html")
CGIHandler().run(app)
