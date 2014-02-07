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

 No listblock nesting! it's unnecessary and regex can't handle it.

 Assignments are the topmost level. Flags are assignments with the terminal value of one.
"""


class Job():

    def __init__(self, line):
        self.command_list = None #list of assignment=value

        self.assignment = {}

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


# parse stringblocks -> parse the contents of listblocks -> parse listblocks -> parse everything else
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
        match_start = stringblock.start()
        match_end = stringblock.end()
        job.working_string = job.working_string[:match_start] + token + job.working_string[match_end:]
    debug(job.working_string)
    debug("Next, we find all of the listblocks, and their contents.")

    # Identify listblocks
    while re.search("\[[^\[\]]*\]",job.working_string) is not None:
        listblock = re.search("\[[^\[\]]*\]",job.working_string)
        lb_match_start = listblock.start()
        lb_match_end = listblock.end()

        working_listblock = listblock.group(0)

        # Identify listblock elements that aren't already parsed (these must be terminal expressions)
        debug("Remove element at start of listblock.")
        while re.search("(?<=\[)[^\[\]\s@]+(?=,)",working_listblock) is not None:
            terminal = re.search("(?<=\[)[^\[\]\s@]+(?=,)",working_listblock)
            token = job.add_token(terminal.group(0), 1)
            match_start = terminal.start()
            match_end = terminal.end()
            working_listblock = working_listblock[:match_start] + token + working_listblock[match_end:]
        debug(working_listblock)

        debug("Remove elements in middle of listblock.")
        while re.search("(?<=, )[^\[\]\s@]+(?=,)",working_listblock) is not None:
            terminal = re.search("(?<=, )[^\[\]\s@]+(?=,)",working_listblock)
            token = job.add_token(terminal.group(0), 1)
            match_start = terminal.start()
            match_end = terminal.end()
            working_listblock = working_listblock[:match_start] + token + working_listblock[match_end:]
        debug(working_listblock)

        debug("Remove element at end of listblock.")
        while re.search("(?<=, )[^\[\]\s@]+(?=\])",working_listblock) is not None:
            terminal = re.search("(?<=, )[^\[\]\s@]+(?=\])",working_listblock)
            token = job.add_token(terminal.group(0), 1)
            match_start = terminal.start()
            match_end = terminal.end()
            working_listblock = working_listblock[:match_start] + token + working_listblock[match_end:]
        debug(working_listblock)

        debug("Remove listblock (which now contains references to other tokens.)")
        lb_token = job.add_token(working_listblock, 2)
        job.working_string = job.working_string[:lb_match_start] + lb_token + job.working_string[lb_match_end:]
        debug(job.working_string)

    debug("Parse flags into assignment form.")
    while re.search("-\w+(?!=)",job.working_string) is not None:
        flag = re.search("-\w+(?!=)",job.working_string)
        match_start = flag.start()
        match_end = flag.end()
        replacement = flag.group(0)[1:] + "=1"
        job.working_string = job.working_string[:match_start] + replacement + job.working_string[match_end:]
    debug(job.working_string)

    debug("Remove terminal expressions that aren't in listblocks.")
    while re.search("(?<==)(?<!@)\w+(?!@)",job.working_string) is not None:
        terminal = re.search("(?<==)(?<!@)\w+(?!@)",job.working_string)
        token = job.add_token(terminal.group(0), 1)
        match_start = terminal.start()
        match_end = terminal.end()
        job.working_string = job.working_string[:match_start] + token + job.working_string[match_end:]
    debug(job.working_string)

    debug("At this point, everything on the job line should be parsed into assignment=@!APID!@ form.")
    debug("If not, the syntax is invalid. (there are only flags and assignments, and those were taken care of.)")

    debug("Finally, split up the kwargs and stick em in a dictionary.")
    kwargs = job.working_string.split(" ")
    for key_value_pair in kwargs:
        key, value = (key_value_pair.split("=")[0], key_value_pair.split("=")[1])
        debug("%s, %s"%(key, value))
        job.assignment[key]=value
    debug("Returns:")
    debug(job.assignment)

    return job.assignment

def translator(line):
    pass

def main():
    line = "data=\"foo.txt\" listoflists=[sin(x), cos(x)] -flag theory=[x^2, x^3] legend=[\"scientific foo data\", \"parabola!\", \"cube-ol-a?\"] labelsize=20 ticksize=10 numticks=5 colors=[\"r\", \"b\", \"g\"] -animate -dog_flag"
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
