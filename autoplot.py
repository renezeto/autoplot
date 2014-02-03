#!/usr/bin/python
from __future__ import division
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os
import glob
import re

# DO NOT MERGE THIS FILE!
# The implimentation here is EXPERIMENTAL and INCOMPLETE
# While nothing is expected to break until I make it break, it is safer to
# keep this out of the deployable branch.

# Rene: Merged with my testing branch. If you are reading this, you have successfully pulled from my testing branch.

# Justin O'Neil: commenting code
# Suggestions:
#  * consider an Autoplot class
#     - move functions into Autoplot class methods
#     - make commands, dataContainer internal class data structures
#     - let the hypothetical Autoplot class parse jobFiles on its own (this
#       will simplify the main() program)
#  * consider removing decimal.Decimal() in favor of built-in floats (rounding
#    to binary representations should not pose a problem for plotting [unless
#    this is actually a problem])
#  * DocStrings!
#  * Make progress bar prettier ([===   ] instead of [|||   ])
#  * IVeryMuchDislikeCamelCase, but_to_each_their_own..
# Changes:
#  * replaced decimal.Decimal(i) with float(i) in loadData()
#  * changed progress bar to ===
#  * started main_new() to give a general idea of what Autoplot() might look like
#  * more comments
#  * Major reimplimentation of program logic
#     - Autoplot class is mostly implemented
#     - Specifing dataFile by directory is broken
#

# Rene Zeto: 
# * remove decimal implementation
# * remove none filling (was there to support the odd case of missing data, but better to just throw an error)
# * font implementation
# * commit testing system (let's make sure it works before we commit!)
# * would like to move default commands dict to a config file. 

matplotlib.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
# matplotlib.rc('text', usetex=True)

## Consider renaming this Plot and make Autoplot the class that reads the jobList and generates
## a list of Plot objects. I think this would be more suitable for parrallelization.
class Autoplot():
    # Review python documnetation on classes to make sure I get this right..
    defaultCommands = {         
        "data": None,                   # Path of data file
        "data_type": "CSV",             # Type of data file (Currently must be CSV)
        "plot_type": "line",            # 
        "plot_kwargs": "{'color':'r'}", #
        "x_data": 0,                    #
        "xlabel": "label your x axis!", #
        "ylabel": "label your y axis!", #
        "title": "",                    #
        "aspect": .35,                  #
        "xrange": None,                 #
        "yrange": None,                 #
        "xscale": "linear",             #
        "yscale": "linear",             #
        "xscale_kwargs": "{}",          #
        "yscale_kwargs": "{}",          #
        "theory": None,                 #
        "ticksize":25,                  #
        "labelsize":36,                 #
        "legend": None,
        "legloc": "best"
        }
    
    def __init__(self, jobPath):
        self.commands = Autoplot.defaultCommands
        self.dataContainer = []
        self.countJobs(jobPath)
        self.jobFile = open(jobPath)
        self.dataIsDir = False
        if self.numJobs > 0:
            self.moreJobs = True
        else:
            self.moreJobs = False
        self.readJobs = 0
        
    def countJobs(self, jobPath):
        # Notice that this actually doesn't count anything....
        numJobs = 0
        f = open(jobPath, 'r')
        for lineNum,line in enumerate(f):
            pass
        self.numJobs = numJobs+1
        f.close()
        return numJobs
        
    def setCommands(self):
    # Update object command dictionary with entries read from self.jobFile
        line = self.jobFile.readline()    
        if "#" in line:
            # Handle comments at the end of the line (marked with #)
            line = re.findall("^(.*?)(?=\s#|#)",line)[0]
        # Find all parameter="argument" keywords and -flag flags
        kwargs = re.findall("\w+=\"[()\w\[\],.+'=\s*/{:}-]+\"",line)
        flags = re.findall("\-\w+",line)
        # Update kwargs and add flags commands
        inputCommands = {}                       
        for kwarg in kwargs:
            key, value = tuple(kwarg.split("=",1))
            value = value.replace("\"","") # Handle lines split with \
            inputCommands[key]=value
        for flag in flags:
            key, value = flag.replace("-",""), 1 # Remove '-' prefix, set value to 1 (True)
            inputCommands[key]=value
        self.commands.update(inputCommands)
        self.readJobs += 1
        if self.readJobs == self.numJobs:
            self.moreJobs = False
        return self.commands        

    def loadData(self):
    # loadData(commands_dict) -> [array(column1), array(column2), array(column3), ..., array(columnN)] -> self.
    # RZ: format is [X, Y1, Y2, Y3]... eventually creates a plot with X vs Y_n for each n. usually n=1.
    # this is because the CSV might have multiple columns, not just two. plotData then plots them on the same plot. (might want to change that later)
        dataContainer = []
        numEntries = 0
        fileLoc = self.commands['data']
        with open(fileLoc) as dataFile: ## This will crash on missing fileLoc
            iterNum = 0
            for line in dataFile:
                # Each line represents a data point
                if re.search("[a-zA-Z]",line)!=None:
                    # Discard lines containing text
                    continue
                dataRow = [float(i) for i in re.findall(r"[-+]?\d*\.\d+|\d+",line)]
                # Create a column in dataContainer for each entry in dataRow 
                if iterNum==0:
                    dataContainer = [[] for col in dataRow]
                for i in range(len(dataRow)):
                    try:
                        dataContainer[i] += [dataRow[i]]
                    except IndexError:
                        print "Index error at column %d, row %d"%(i+1,iterNum+1)
                iterNum += 1
        # Convert to numpy arrays
        dataContainer = [np.array(dataColumn) for dataColumn in dataContainer]
        self.dataContainer = dataContainer
        return dataContainer
        
    def plotData(self):
    # TODO: learn how matplotlib works (jwo)
        plotType = self.commands["plot_type"]
        plotCLKwargs = eval(self.commands["plot_kwargs"])
        if plotType=="line":
            w, h = plt.figaspect(self.commands['aspect'])
            fig, axs = plt.subplots(1, 1,figsize=(w,h))
            fname = self.commands['data'][:-4]
            xData = self.dataContainer[self.commands["x_data"]]
            self.dataContainer.pop(self.commands["x_data"])
            for dataSet in self.dataContainer:
                axs.plot(xData,dataSet,**plotCLKwargs)
            if self.commands["theory"] is not None:
                expression=self.commands["theory"]
                x = np.array([float(i) for i in xData])
                curve = eval(expression)
                axs.plot(xData,curve,**plotCLKwargs)
            axs.set_xscale(self.commands['xscale'],**eval(self.commands['xscale_kwargs']))
            axs.set_yscale(self.commands['yscale'],**eval(self.commands['yscale_kwargs']))
            plt.xlabel(self.commands['xlabel'],fontsize=self.commands['labelsize'])
            plt.ylabel(self.commands['ylabel'],fontsize=self.commands['labelsize'])
            axs.tick_params(axis='both', which='major', labelsize=self.commands['ticksize'])
            plt.title(self.commands['title'],fontsize=self.commands['labelsize'])
            if self.commands['legend'] is not None:
                plt.legend(eval(self.commands['legend']),self.commands['legloc'])
            x1, x2 = plt.xlim()
            y1, y2 = plt.ylim()
            axs.grid(True)
            if self.commands['xrange'] is not None:
                x1, x2 = eval(self.commands['xrange'])
            if self.commands['yrange'] is not None:
                y1, y2 = eval(self.commands['yrange'])
            plt.xlim([x1,x2])
            plt.ylim([y1,y2])
            plt.tight_layout()
            plt.savefig("%s"%fname)
        return 0
    
        # TODO: progress bar needs to be implemented differently with this implementation
        def progBar(self):
            pass


##############################################################################
# The following lines are the legacy implementation. They should not run but #
# are retained to make reverting to the old implementation if necessary      #
##############################################################################
######################## # BEGIN LEGACY CODEBASE # ###########################
def setCommands(line):
    # Return a dictionary containing entries parsed from a line with commands
    # of the form "parameter=argument" and "-flag".
    
    # default parameters
    commands = { 
        "data": None,                   # Path of CSV data file
        "data_type": "CSV",             # Type of data file (Currently must be CSV) #rz: as in "character"-sv. other delimiters are fine.
        "plot_type": "line",            # 
        "plot_kwargs": "{'color':'r'}", #
        "x_data": 0,                    #
        "xlabel": "label your x axis!", #
        "ylabel": "label your y axis!", #
        "title": "",                    #
        "aspect": .35,                  #
        "xrange": None,                 #
        "yrange": None,                 #
        "xscale": "linear",             #
        "yscale": "linear",             #
        "xscale_kwargs": "{}",          #
        "yscale_kwargs": "{}",          #
        "theory": None,                 #
        "ticksize":25,                  #
        "labelsize":36,                 #
        "legend": None,
        "legloc":"best"
        }
    if "#" in line:
        # Handle comments at the end of the line (marked with #)
        line = re.findall("^(.*?)(?=\s#|#)",line)[0]
    # Find all parameter="argument" keywords and -flag flags
    kwargs = re.findall("\w+=\"[()\w\[\],.+'=\s*/{:}-]+\"",line)
    flags = re.findall("\-\w+",line)
    
    # Update kwargs and add flags commands
    inputCommands = {}                       
    for kwarg in kwargs:
        key, value = tuple(kwarg.split("=",1))
        value = value.replace("\"","") # Handle lines split with \
        inputCommands[key]=value
    for flag in flags:
        key, value = flag.replace("-",""), 1 # Remove - prefix, set value to 1 (True)
        inputCommands[key]=value
    commands.update(inputCommands)        
    return commands

def loadData(commands):
    # loadData(commands_dict) -> [array(column1), array(column2), array(column3), ..., array(columnN)] 
    # RZ: format is [X, Y1, Y2, Y3]... eventually creates a plot with X vs Y_n for each n. usually n=1.
    # this is because the CSV might have multiple columns, not just two. plotData then plots them on the same plot. (might want to change that later)
    dataContainer = []
    numEntries = 0
    fileLoc = commands['data']
    with open(fileLoc) as dataFile:
        iterNum = 0
        for line in dataFile:
            # Each line represents a data point
            if re.search("[a-zA-Z]",line)!=None:
                # Discard lines containing text
                continue
            dataRow = [float(i) for i in re.findall(r"[-+]?\d*\.\d+|\d+",line)]
            # Create a column in dataContainer for each entry in dataRow 
            if iterNum==0:
                dataContainer = [[] for col in dataRow]
            for i in range(len(dataRow)):
                try:
                    dataContainer[i] += [dataRow[i]]
                except IndexError:
                    print "Index error at column %d, row %d"%(i+1,iterNum+1)
            iterNum += 1
    # Convert to numpy arrays
    dataContainer = [np.array(dataColumn) for dataColumn in dataContainer]
    return dataContainer
    
# TODO: learn how matplotlib works (jwo)
def plotData(commands,dataContainer):
    plotType = commands["plot_type"]
    plotCLKwargs = eval(commands["plot_kwargs"])
    if plotType=="line":
        w, h = plt.figaspect(commands['aspect'])
        fig, axs = plt.subplots(1, 1,figsize=(w,h))
        fname = commands['data'][:-4]
        xData = dataContainer[commands["x_data"]]
        dataContainer.pop(commands["x_data"])
        for dataSet in dataContainer:
            axs.plot(xData,dataSet,**plotCLKwargs)
        if commands["theory"] is not None:
            expression=commands["theory"]
            x = np.array([float(i) for i in xData])
            curve = eval(expression)
            axs.plot(xData,curve,**plotCLKwargs)
        axs.set_xscale(commands['xscale'],**eval(commands['xscale_kwargs']))
        axs.set_yscale(commands['yscale'],**eval(commands['yscale_kwargs']))
        plt.xlabel(commands['xlabel'],fontsize=commands['labelsize'])
        plt.ylabel(commands['ylabel'],fontsize=commands['labelsize'])
        axs.tick_params(axis='both', which='major', labelsize=commands['ticksize'])
        plt.title(commands['title'],fontsize=commands['labelsize'])
        if commands['legend'] is not None:
            plt.legend(eval(commands['legend']),commands['legloc'])
        x1, x2 = plt.xlim()
        y1, y2 = plt.ylim()
        axs.grid(True)
        if commands['xrange'] is not None:
            x1, x2 = eval(commands['xrange'])
        if commands['yrange'] is not None:
            y1, y2 = eval(commands['yrange'])
        plt.xlim([x1,x2])
        plt.ylim([y1,y2])
        plt.tight_layout()
        plt.savefig("%s"%fname)
    return 0

def progBar(percent):
    # Create a progress bar showing percent completion.
    # progBar(int) -> string
    prefix = ' %3d%%'%(percent)
    progress = int(percent/2)
    bar_size = 50
    remain = bar_size - progress
    bar = '=' * progress + ' ' * remain
    return prefix + ' [' + bar + ']'
            
def main():
    # Check for valid file and get number of jobs
    if len(sys.argv) < 2:
        # User did not provide an input file, use default
        jobPath = "autoplotlist.txt"
    else: 
        # Use file provided on command line
        jobPath = sys.argv[1]
    try:
        # Count the number of lines (jobs) in the file, add 1 b/c CS likes to start counting at 0
        with open(jobPath,"r") as jobFile:
            for numJobs, line in enumerate(jobFile):
                pass
        numJobs += 1
    except:
        # Friendly error message for nonexistent file
        print "Error: Unable to open jobs file '%s'."%jobPath
        return 1        
    # Parse jobFile
    with open(jobPath,"r") as jobFile:
        for lineNum,line in enumerate(jobFile):
            commands = setCommands(line)
            if commands["data"] is not None:
                if os.path.isdir(commands['data'])==False:
                    loadedData = loadData(commands)
                    plotData(commands,loadedData)
                else:
                    filePath = commands['data']
                    # Handles directory batch plotting (occurs when data kwarg is a directory and not a file)
                    for fileName in glob.iglob("%s/*.%s"%(filePath,commands['data_type'])):
                        commands['data'] = fileName
                        loadedData = loadData(commands)
                        plotData(commands,loadedData)
                sys.stdout.write(' Working: '+ progBar(((lineNum+1)/numJobs)*100)+' '+ commands['data'] + ' '*25 +'\r')
                sys.stdout.flush()
            #elif commands["data"] is None:     ## No need for another test
            else:
                continue
    print "\n Finished."
    return 0 

######################### # END LEGACY CODEBASE # ############################
##############################################################################

## Need to implement more things before making this main()
## TODO: Implement Autoplot() class    
def main_new():
    if len(sys.argv) < 2:
        # User did not provide an input file, use default
        jobPath = "autoplotlist.txt"
    else: 
        # Use file provided on command line
        ## TODO: change working directory to location of jobPath
        jobPath = sys.argv[1]
    # Open check existence of jobPath and give it to Autoplot()
    try:
        f = open(jobPath, 'r')
    except:
        # Friendly error message for nonexistent file
        print "Error: Unable to open jobs file '%s'."%jobPath
        return 1
    finally:
        f.close()
    autoplot = Autoplot(jobPath)
    # Create plots as long as autoplot has moreJobs
    while autoplot.moreJobs:
        autoplot.setCommands()
        autoplot.loadData()
        autoplot.plotData()
#        autoplot.progBar()
    print "\n Finished."
    autoplot.jobFile.close() ## Find a better way to do this.
    return 0

# run main_new()
if __name__ == "__main__":
    main_new()
