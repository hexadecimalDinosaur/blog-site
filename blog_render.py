import asyncio
import hashlib
import markdown
from lru import lru_cache
from bs4 import BeautifulSoup
from threading import Thread


# @lru_cache(maxsize=32, expires=300)
def to_html(md: str, md5: bytes, content_cache: dict):
    content_cache[md5] = markdown.markdown(md, extensions=['codehilite', 'extra', 'smarty', 'mdx_truly_sane_lists', 'footnotes', 'markdown_katex'], extension_configs={
        'codehilite': {
            'linenums': True,
            'guess_lang': False
        },
        'markdown_katex': {
            'insert_fonts_css': False
        },
        'mdx_truly_sane_lists': {
            'nested_indent': 2,
            'truly_sane': True,
        },
    })


# @lru_cache(maxsize=32, expires=300)
def to_html_toc(md: str, md5: bytes, content_cache: dict):
    convert = markdown.Markdown(extensions=['toc', 'codehilite', 'extra', 'smarty', 'mdx_truly_sane_lists', 'footnotes', 'markdown_katex'], extension_configs={
        'codehilite': {
            'linenums': True,
            'guess_lang': False
        },
        'markdown_katex': {
            'insert_fonts_css': False
        },
        'mdx_truly_sane_lists': {
            'nested_indent': 2,
            'truly_sane': True,
        },
    })
    html = convert.convert(md)
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    for table in tables:
        table.wrap(soup.new_tag('div', attrs={'class': 'responsive-table'}))
    html = soup.prettify()
    toc = convert.toc
    content_cache[md5] = (html, toc)


# @lru_cache(maxsize=32, expires=300)
def to_html_noclass(md: str, md5: bytes, content_cache: dict):
    content_cache[md5] = markdown.markdown(md, extensions=['codehilite', 'extra', 'smarty', 'mdx_truly_sane_lists', 'footnotes', 'markdown_katex'], extension_configs={
        'codehilite': {
            'linenums': True,
            'guess_lang': False,
            'noclasses': True
        },
        'mdx_truly_sane_lists': {
            'nested_indent': 2,
            'truly_sane': True,
        },
    })


def cached_to_html(file: str, content_cache: dict, noclass=False, toc=False) -> str:
    f = open(file, 'r', encoding='utf-8')
    data = f.read()
    f.close()
    md5 = hashlib.md5(data.encode('utf-8')).digest()
    if md5 in content_cache:
        return content_cache[md5]
    else:
        if not (noclass or toc):
            to_html(data, md5, content_cache)
        elif toc:
            to_html_toc(data, md5, content_cache)
        else:
            to_html_noclass(data, md5, content_cache)
        return content_cache[md5]


class PrerenderThread(Thread):
    def __init__(self, file: str, content_cache: dict, noclass=False, toc=False):
        self.file = file
        self.content_cache = content_cache
        self.noclass = noclass
        self.toc = toc
        super(PrerenderThread, self).__init__()

    def run(self):
        try:
            print(f"prerendering {self.file}")
            cached_to_html(self.file, self.content_cache, self.noclass, self.toc)
            print(f"prerender of {self.file} completed")
        except Exception as e:
            print(e)
