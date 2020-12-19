import markdown

def to_html(file):
    f = open(file,'r')
    md = f.read()
    return markdown.markdown(md, extensions=['codehilite', 'extra', 'smarty'], extension_configs={
        'codehilite':{
            'linenums':True,
            'guess_lang':True,
            'nobackground':True
        }
    })
