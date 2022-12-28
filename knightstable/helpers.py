import re


# Removing eval lines
def strip_eval(x):
    # remove curly braces and number in them
    x = re.sub("\{.*?\}", "", x)
    # Remove random eval numbers
    x = re.sub(".\.\.\.", "", x)
    # Remove random periods
    x = re.sub("\$.", "", x)
    # Join together to get rid of whitespace
    x = " ".join(x.split())
    return x


# Capitalizing
def cap(x):
    return x.capitalize()
