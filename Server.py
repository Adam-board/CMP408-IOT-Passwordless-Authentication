from flask import Flask, render_template, request, redirect, send_file
import boto3
import re

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")