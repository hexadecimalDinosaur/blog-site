#!/usr/bin/python3
from flask import Flask, request, render_template, redirect, url_for, abort
import os
from blog_render import to_html
import json

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

@app.route('/blog/')
def blog_home():
    articles = list()
    for f in os.listdir('content'):
        if f.endswith('.json'):
            articles.append(f)
    for f in range(len(articles)):
        data = json.load(open('content/'+articles[f], 'r'))
        articles[f] = (data['title'], data['date'], data['slug'])
    articles.sort(key=lambda f:f[1])
    return render_template('blog.html', articles=articles)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run()
