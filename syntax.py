import re

# Simple, one line at a time parser for autoplot.
#
    # Contains the syntax information for job lines.
    # kwargs
    # * key="value"
    # flags
    # * -flagkey
    # specific function kwargs
    # * fn.key="value"
    # groups
    # * all values could be groups, and at the very least, should have support for iteration
    # * this would be useful for e.g. multiple theory plots. 
    # * theory=[x^2, x^3, x^4]...

# Breaks apart the line into expressions which can be evaluated.
def scanner(line):
    # Parse out EOL comments
    if ("#" in line): line = re.findall("^(.*?)(?=\s#|#)",line)[0]
    # Find flags
    flag_container = re.findall("-[\w]+",line)
    # Find string valued kwargs
    quote_kwarg_container = re.findall("([\w.]+=\"[^\"]*\")",line)
    # Find list valued kwargs
    group_kwarg_container = re.findall("\w+=\[[\w,\^*+-/! ()]+\]",line)
    # Find alphanumeric valued kwargs
    kwarg_container = re.findall("\w+=\w+",line)
    # Append to list for evaluater.
    return flag_container + quote_kwarg_container + group_kwarg_container + kwarg_container

def translator(line):
    # Evaluates the expressions from scanner and returns the necessary information
    # to autoplot.
    pass

if __name__ == "__main__":
    print scanner("This is a theory=[x^2, sin(x)] -flag -dog cat-yellow contourf.linecolor=yellow pcolor.marker=\"o -\" dog=blue 5=6 dang=\"sho ot\". \"hello sir\"")
