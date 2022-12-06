import re

def strip_eval(x):
    x = re.sub("\{.*?\}","",x)
    x = re.sub(".\.\.\.", "",x)
    x = re.sub("\$.", "",x)
    x = ' '.join(x.split())
    return x

def cap(x):
    return x.capitalize()
