import re

def strip_eval(x):
    x = re.sub("\{.*?\}","",x)
    x = re.sub(".\.\.\.", "",x)
    x = re.sub("\$.", "",x)
    x = ' '.join(x.split())
    return x

def cap(x):
    return x.capitalize()

def attempt(dictionary, x):
    try:
        dictionary[x]
        return True
    except:
        return False
