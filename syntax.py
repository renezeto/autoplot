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


class Token():
    # [,]
    # =
    # . =
    # " "
    # -
    pass

def scanner(line):
    # Breaks apart the line into expressions which can be evaluated.
    line = line.split(" ")
    arg_container = [word for word in line]
    for arg in arg_container:
        # Quote groups
        re.findall("\w+",arg)
    return arg_container

def evaluater():
    # Evaluates the expressions from scanner and returns the necessary information
    # to autoplot.
    pass

def main():
    # Debug function when running the module directly.
    pass

if __name__ == "__main__":
    scanner("This is a dog.")
