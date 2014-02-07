import sys
import re

"""  
 Important! Run with -debug to see helpful messages. Code is much easier to learn with those on.

 VOCAB (list of expressions):

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

    def __init__(self, line):
        self.command_list = None #list of assignment=value

        self.assignment = None

        # Hash tables for stringblock, terminal, and listblock token types.
        self.stringblock_catalog = {}
        self.terminal_catalog = {}
        self.listblock_catalog = {}

        # If we are ever unsure of what type an identifier is, check its first index
        # value in type_container.
        self.type_container = [self.stringblock_catalog, self.terminal_catalog, self.listblock_catalog]

        self.original_string = line
        self.working_string = line

        # This value increments each time a token is recorded.
        self.token_counter = 0

    def add_token(self,value,token_type):
        identifier = "@!APID:%08d!@"%self.token_counter
        if token_type == 0:
            self.stringblock_catalog[identifier] = value
        if token_type == 1:
            self.terminal_catalog[identifier] = value
        if token_type == 2:
            self.listblock_catalog[identifier] = value
        self.token_counter += 1
        return identifier

def debug(msg):
    if "-debug" in sys.argv:
        print msg
    return 0

def scanner(line):
    job = Job(line)



    debug("Debugging messages! Read these if you want to understand how scanner processes job strings.")
    debug("Initial string, hot off the jobfile...:")
    debug(job.working_string)
    debug("Now, we find all of the stringblocks, catalog them, and replace the stringblock in the job string with a token:")

    # Identify stringblocks
    while re.search("\"(.*?)\"",job.working_string) is not None:
        stringblock = re.search("\"(.*?)\"",job.working_string)
        token = job.add_token(stringblock.group(0), 0)
        matchstart = stringblock.start()
        matchend = stringblock.end()
        job.working_string = job.working_string[:matchstart] + token + job.working_string[matchend:]
    debug(job.working_string)
    debug("Next, we find all of the terminal expressions, which can be found by looking for things that aren't tokens or listblocks:")

    # regex brainstorm
    # Identify terminal expressions (everything left that isn't a listblock)
    #print (re.search("(?<==)(?!@!APID:[0-9]{8}!@).+",job.working_string)).group(0)

    #print (re.search("(?<==)[\[\]()*+-=!@#.;\w]+(?= )",job.working_string)).group(0)
    #print (re.search("[^\[]*(\[.*\])[^\]]*",job.working_string)).group(0)
    # (?<==)

def translator(line):
    pass

def main():
    line = "data=\"foo.txt\" listoflists=[sin(x), [cos(x), \"red\", 5]] \"yes\" \"yes\" theory=[x^2, x^3] legend=[\"scientific foo data\", \"parabola!\", \"cube-ol-a?\"] labelsize=20 ticksize=10 numticks=5 colors=[\"r\", \"b\", \"g\"]"
    scanner(line)

if __name__ == "__main__":
    main()

# useful regex
# a = "fjdsklajsearchfdajk"
# for i in re.finditer("search",a):
#     print i.start(), i.end()

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
