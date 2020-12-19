#!/usr/bin/python3
from flask import Flask, request, render_template, redirect, url_for
import markdown
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact/')
def contact():
    return render_template('contact.html')

@app.route('/projects/')
def projects():
    return render_template('projects.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/timeline/')
def timeline():
    return render_template('timeline.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run()
