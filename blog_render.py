import markdown
from lru import lru_cache
from bs4 import BeautifulSoup

@lru_cache(maxsize=32, expires=300)
def to_html(file):
    f = open(file,'r')
    md = f.read()
    return markdown.markdown(md, extensions=['codehilite', 'extra', 'smarty', 'mdx_truly_sane_lists', 'footnotes', 'markdown_katex'], extension_configs={
        'codehilite':{
            'linenums':True,
            'guess_lang':False
        }
    })

@lru_cache(maxsize=32, expires=300)
def to_html_toc(file):
    f = open(file,'r')
    md = f.read()
    convert = markdown.Markdown(extensions=['toc', 'codehilite', 'extra', 'smarty', 'mdx_truly_sane_lists', 'footnotes', 'markdown_katex'], extension_configs={
        'codehilite':{
            'linenums':True,
            'guess_lang':False
        }
    })
    html = convert.convert(md)
    soup = BeautifulSoup(html)
    tables = soup.find_all('table')
    for table in tables:
        table.wrap(soup.new_tag('div', attrs={'class': 'responsive-table'}))
    html = soup.prettify()
    toc = convert.toc
    return html, toc

@lru_cache(maxsize=32, expires=300)
def to_html_noclass(file):
    f = open(file,'r')
    md = f.read()
    return markdown.markdown(md, extensions=['codehilite', 'extra', 'smarty', 'mdx_truly_sane_lists', 'footnotes', 'markdown_katex'], extension_configs={
        'codehilite':{
            'linenums':True,
            'guess_lang':False,
            'noclasses':True
        }
    })
