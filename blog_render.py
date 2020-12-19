import markdown
from markdown.extensions.codehilite import CodeHiliteExtension

def to_html(file):
    f = open(file,'r')
    md = f.read()
    return markdown.markdown(md, extensions=[CodeHiliteExtension(linenume=True)])
