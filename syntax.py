import re

"""  VOCAB (list of expressions)
 terminal: a terminating expression that is not a string (e.g. x^2).
 stringblock: a string.
 listblock: a list of values.
 assignment: the thing being changed (like linecolor=red, linecolor is the "assignment").

 HEIRARCHY: 

 assignment
 * terminal
 * stringblock
 * listblock 
 * * terminal
 * * stringblock
 * * listblock
 * * * terminal
 * * * stringblock
 * * * listblock
 ...

 Get the idea? 

 Scanner outline:

 1. Take string, place in "container" list.
 2. Regex on string looking for stringblocks. Replace those with stringblock objects.
 3. Regex on string looking for terminals. Replace those with terminal objects. At this point,
    we will have captured everything that is not a listblock. 
 4. Regex on string looking for all listblocks (in order of most deeply nested first).
    Replace those with listblock objects (which contain references to the nested values inside).

 Assignments are the topmost level. Flags are assignments with the terminal value of one.
"""


class Token():
    self.assignment = None
    self.listblock = None
    self.terminal = None
    self.strblock = None
    def __init__(self, token_type):
        

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

def main():
    line = "data=\"foo.txt\" theory=\"[x^2, x^3]\" legend=[\"scientific foo data\", \"parabola!\", \"cube-ol-a?\"] labelsize=20 ticksize=10 numticks=5 colors=[\"r\", \"b\", \"g\"]"
    scanner(line)

if __name__ == "__main__":
    main()


# look for things in quotes. find the first quote, find the second, capture that object.
# # replace object with more parseable "pointer" to real object.
# look for things in brackets. find the first bracket, find the second. capture that object.
# # replace the object with the pointer to the bracket object, which could contain pointers to other objects.
# look for key=value pairs. store those as pointers too.
