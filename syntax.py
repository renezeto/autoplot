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


class Job():
    command_list = None #list of assignment=value

    assignment = None
    listblock = None
    terminal = None
    strblock = []

    token_counter = 0

    def __init__(self, line):
        self.original_string = line
        self.working_string = [line]
        self.list_index = list(enumerate(line))

    def token(value,token_type):
        identifier = "@!APID:%05d!@"%token_counter
        token_counter += 1
        return identifier

def scanner(line):
    job = Job(line)
    #find all stringblocks
    stringblocks = re.findall("\"(.*?)\"",line)
    for stringblock in stringblocks:
        for substring in working_string:
            substring = substring.replace(stringblock,job.token(stringblock))

def translator(line):
    pass

def main():
    line = "data=\"foo.txt\" theory=[x^2, x^3] legend=[\"scientific foo data\", \"parabola!\", \"cube-ol-a?\"] labelsize=20 ticksize=10 numticks=5 colors=[\"r\", \"b\", \"g\"]"
    scanner(line)

if __name__ == "__main__":
    main()

# First draft idea, keeping for regex reference:
# # Breaks apart the line into expressions which can be evaluated.
# def scanner(line):
#     # Parse out EOL comments
#     if ("#" in line): line = re.findall("^(.*?)(?=\s#|#)",line)[0]
#     # Find flags
#     flag_container = re.findall("-[\w]+",line)
#     # Find string valued kwargs
#     quote_kwarg_container = re.findall("([\w.]+=\"[^\"]*\")",line)
#     # Find list valued kwargs
#     group_kwarg_container = re.findall("\w+=\[[\w,\^*+-/! ()]+\]",line)
#     # Find alphanumeric valued kwargs
#     kwarg_container = re.findall("\w+=\w+",line)
#     # Append to list for evaluater.
#     return flag_container + quote_kwarg_container + group_kwarg_container + kwarg_container
