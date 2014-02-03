import re

# Simple, one line at a time parser for autoplot.

class Token():
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
    pass

def scanner():
    # Breaks apart the line into expressions which can be evaluated.
    pass

def evaluater():
    # Evaluates the expressions from scanner and returns the necessary information
    # to autoplot.
    pass

def main():
    # Debug function when running the module directly.
    pass

if __name__ == "__main__":
    main()
