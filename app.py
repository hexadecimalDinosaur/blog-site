#!/usr/bin/python3
from flask import Flask, request, render_template, redirect, url_for, abort
import os
from blog_render import to_html, to_html_noclass
import json
from feedgen.feed import FeedGenerator
import datetime
import pytz

url = 'http://127.0.0.1:5000'
owner = 'YourNameHere'

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
    articles = articles[::-1]
    return render_template('blog.html', articles=articles)

@app.route('/blog/<slug>/')
def article(slug):
    if (not os.path.isfile('content/'+slug+'.json')) or (not os.path.isfile('content/'+slug+'.mkd')):
        abort(404)
    html = to_html('content/'+slug+'.mkd')
    data = json.load(open('content/'+slug+'.json', 'r'))
    return render_template('article.html', title=data['title'], date=data['date'], content=html)

@app.route('/rss.xml')
def rss():
    articles = []
    for f in os.listdir('content'):
        if f.endswith('.json'):
            articles.append(f)
    for f in range(len(articles)):
        data = json.load(open('content/'+articles[f], 'r'))
        articles[f] = (data['title'], data['date'], data['slug'])
    feed = FeedGenerator()
    feed.title("YourNameHere's Blog")
    feed.author({'name':owner,'email':'user@domain.com'})
    feed.link(href=url, rel='self')
    feed.language('en-CA')
    feed.updated(pytz.timezone("America/Toronto").localize(datetime.datetime.now()))
    feed.subtitle(subtitle="Some description of the blog")
    for f in articles:
        entry = feed.add_entry()
        entry.id(url+'/blog/'+f[2])
        entry.title(f[0])
        entry.link(href=url+'/blog/'+f[2])
        entry.description(description=to_html_noclass('content/'+f[2]+'.mkd'))
        entry.author({'name':owner,'email':'user@domain.com'})
        date = pytz.timezone("America/Toronto").localize(datetime.datetime.strptime(f[1],'%Y/%m/%d'))
        entry.pubDate(date)
    return feed.rss_str(pretty=True)



@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run()
