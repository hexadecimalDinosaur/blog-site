#!/usr/bin/python3
from flask import Flask, request, render_template, redirect, url_for, abort, Response, send_file
import os
from blog_render import to_html, to_html_noclass, to_html_toc
import json
import datetime
import pytz
from flask_mobility import Mobility
from flask_caching import Cache

url = 'https://ivyfanchiang.dev'
owner = 'Ivy Fan-Chiang'

config = {
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
Mobility(app)
cache = Cache(app)

@app.route('/')
def index():
    if request.MOBILE:
        return render_template('mobile/index.html')
    return render_template('index.html')

@app.route('/contact/')
def contact():
    if request.MOBILE:
        return render_template('mobile/contact.html')
    return render_template('contact.html')

@app.route('/projects/')
def projects():
    data = json.load(open('projects.json', 'r'))
    if request.MOBILE:
        return render_template('mobile/projects.html', projects=data['projects'])
    return render_template('projects.html', projects=data['projects'])

@app.route('/about/')
def about():
    if request.MOBILE:
        return render_template('mobile/index.html')
    return render_template('index.html')

@app.route('/achievements/')
def timeline():
    if request.MOBILE:
        return render_template('mobile/timeline.html')
    return render_template('timeline.html')

@app.route('/blog/')
def blog_home():
    content = json.load(open('content/content.json', 'r'))
    articles = []
    for f in content.keys():
        articles.append((content[f]['title'], content[f]['date'], f))
    articles.sort(key=lambda f:f[1])
    articles = articles[::-1]
    if request.MOBILE:
        return render_template('mobile/blog.html', articles=articles)
    return render_template('blog.html', articles=articles)

@app.route('/blog/<slug>/')
def article(slug):
    articles = json.load(open('content/content.json', 'r'))
    if slug not in articles.keys():
        abort(404)
    try:
        html = to_html('content/'+articles[slug]['file'])
    except FileNotFoundError:
        abort(404)
    data = articles[slug]
    if request.MOBILE:
        return render_template('mobile/article.html', title=data['title'], date=data['date'], content=html)
    return render_template('article.html', title=data['title'], date=data['date'], content=html)

@app.route('/reference/<slug>/')
def cheatsheet(slug):
    sheets = json.load(open('content/reference.json', 'r'))
    if slug not in sheets.keys():
        abort(404)
    try:
        html, toc = to_html_toc('content/'+sheets[slug]['file'])
    except FileNotFoundError:
        abort(404)
    if request.MOBILE:
        return render_template('mobile/reference.html', title=sheets[slug]['title'], content=html, toc=toc)
    return render_template('reference.html', title=sheets[slug]['title'], content=html, toc=toc)

@app.route('/rss.xml')
@cache.cached(timeout=60)
def rss():
    content = json.load(open('content/content.json', 'r'))
    articles = []
    for f in content.keys():
        articles.append((content[f]['title'], content[f]['date'], f))
    title = "Ivy Fan-Chiang's Blog"
    description = "Sometimes I may write some stuff here"
    copyright = "@ 2021 Ivy Fan-Chiang"
    for i in range(len(articles)):
        articles[i] = {
            'title': articles[i][0],
            'date': pytz.timezone("America/Toronto").localize(datetime.datetime.strptime(articles[i][1],'%Y/%m/%d')),
            'link': url+'/blog/'+articles[i][2],
            'content': to_html_noclass('content/'+content[articles[i][2]]['file'])
        }
    return Response(render_template('rss.xml', url=url, posts=articles, title=title, description=description, copyright=copyright), mimetype='application/rss+xml')

@app.route('/keybase.txt')
def keybase():
    return render_template('keybase.txt')

@app.route('/robots.txt')
def robots():
    return send_file('templates/robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_file('templates/sitemap.xml')

@app.errorhandler(404)
def not_found(e):
    if request.MOBILE:
        return render_template('mobile/404.html')
    return render_template('404.html')

if __name__ == '__main__':
    app.run()
