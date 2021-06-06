import markdown
from  lru import lru_cache

@lru_cache(maxsize=32, expires=60)
def to_html(file):
    f = open(file,'r')
    md = f.read()
    return markdown.markdown(md, extensions=['codehilite', 'extra', 'smarty'], extension_configs={
        'codehilite':{
            'linenums':True,
            'guess_lang':False
        }
    })

@lru_cache(maxsize=32, expires=60)
def to_html_toc(file):
    f = open(file,'r')
    md = f.read()
    convert = markdown.Markdown(extensions=['toc', 'codehilite', 'extra', 'smarty'], extension_configs={
        'codehilite':{
            'linenums':True,
            'guess_lang':False
        }
    })
    html = convert.convert(md)
    toc = convert.toc
    return html, toc

def to_html_noclass(file):
    f = open(file,'r')
    md = f.read()
    return markdown.markdown(md, extensions=['codehilite', 'extra', 'smarty'], extension_configs={
        'codehilite':{
            'linenums':True,
            'guess_lang':False,
            'noclasses':True
        }
    })