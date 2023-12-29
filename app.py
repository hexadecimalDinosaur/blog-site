#!/usr/bin/python3
from flask import Flask, request, render_template, redirect, url_for, abort, Response, send_file
import os
from blog_render import cached_to_html, PrerenderThread
import json
import datetime
import pytz
from flask_caching import Cache
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

url = 'https://ivyfanchiang.ca'
owner = 'Ivy Fan-Chiang'

config = {
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

global content_index_cache
content_index_cache = {}
content_cache = {}
content_noclass_cache = {}
content_toc_cache = {}


@app.route('/')
def index():
    return render_template('index.html', title="Home")


@app.route('/contact/')
@app.route('/contact')
def contact():
    return render_template('contact.html', title="Contact")


@app.route('/projects/')
@app.route('/projects')
def projects():
    data = json.load(open('projects.json', 'r'))
    return render_template('projects.html', projects=data['projects'], title="Projects")


@app.route('/about/')
@app.route('/about')
def about():
    return render_template('about.html', title="About Me")


@app.route('/achievements/')
@app.route('/achievements')
def timeline():
    return render_template('timeline.html', title="Achievements")


@app.route('/misc/')
@app.route('/misc')
def misc():
    return render_template('misc.html', content=cached_to_html('content/misc.md', content_cache), title="Misc")


@app.route('/blog/')
@app.route('/blog')
def blog_home():
    content = content_index_cache
    articles = []
    for f in content.keys():
        articles.append((content[f]['title'], content[f]['date'], f))
    articles.sort(key=lambda f:f[1])
    articles = articles[::-1]
    return render_template('blog.html', articles=articles, title="Blog")


@app.route('/blog/<slug>/')
@app.route('/blog/<slug>')
def article(slug):
    articles = content_index_cache
    if slug not in articles.keys():
        abort(404)
    try:
        html = cached_to_html('content/'+articles[slug]['file'], content_cache)
    except FileNotFoundError:
        abort(404)
    data = articles[slug]
    return render_template('article.html', title=data['title'], date=data['date'], content=html, slug=slug, description=data.get("description"))


@app.route('/reference/<slug>/')
@app.route('/reference/<slug>')
def cheatsheet(slug):
    sheets = json.load(open('content/reference.json', 'r'))
    if slug not in sheets.keys():
        abort(404)
    try:
        html, toc = cached_to_html('content/'+sheets[slug]['file'], content_toc_cache, toc=True)
    except FileNotFoundError:
        abort(404)
    return render_template('reference.html', title=sheets[slug]['title'], content=html, toc=toc, slug=slug)


@app.route('/rss.xml')
@cache.cached(timeout=60)
def rss():
    content = content_index_cache
    articles = []
    for f in content.keys():
        articles.append((content[f]['title'], content[f]['date'], f))
    title = "Ivy Fan-Chiang's Blog"
    description = "Sometimes I may write some stuff here"
    copyright = "@ 2022 Ivy Fan-Chiang"
    for i in range(len(articles)):
        articles[i] = {
            'title': articles[i][0],
            'date': pytz.timezone("America/Toronto").localize(datetime.datetime.strptime(articles[i][1],'%Y/%m/%d')),
            'link': url+'/blog/'+articles[i][2],
            'content': cached_to_html('content/'+content[articles[i][2]]['file'], content_noclass_cache, noclass=True)
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
    return render_template('404.html', title="404"), 404


class RerenderHandler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event: FileSystemEvent):
        if (event.event_type == 'modified' or event.event_type == 'created') and not event.is_directory:
            if event.src_path.endswith(".md") or event.src_path.endswith(".mkd"):
                is_post = False
                global content_index_cache
                for article in content_index_cache.keys():
                    if content_index_cache[article]['file'] == event.src_path[len('content/'):]:
                        is_post = True
                        break
                if not is_post:
                    return
                PrerenderThread(event.src_path, content_cache).start()
                PrerenderThread(event.src_path, content_noclass_cache, noclass=True).start()
            if event.src_path == 'content/content.json':
                content_index_cache = json.load(open('content/content.json', 'r', encoding='utf-8'))



with app.app_context():
    content_index_cache = json.load(open('content/content.json', 'r', encoding='utf-8'))
    for article in content_index_cache.keys():
        PrerenderThread('content/'+content_index_cache[article]['file'], content_cache).start()
        PrerenderThread('content/'+content_index_cache[article]['file'], content_noclass_cache, noclass=True).start()
    observer = Observer()
    observer.schedule(RerenderHandler(), 'content/', recursive=False)
    observer.start()


if __name__ == '__main__':
    app.run()
