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

# Justin O'Neil: commenting code, reimplimenting program logic to use OOP
# Suggestions/TODO:
#  * Make progress bar work
#  * Keyword argument library
#  * Handle missing files gracefully
#  * Extend IOError exception class to MissingJobs and MissingData exception classes
#    so we can handle these problems in the main program
#  * DocStrings!
#  * More comments
#  * IVeryMuchDislikeCamelCase, but_to_each_their_own..
# Changes:
#  * replaced decimal.Decimal(i) with float(i) in loadData()
#  * changed progress bar to ===
#  * started main_new() to give a general idea of what Autoplot() might look like
#  * more comments
#  * Major reimplimentation of program logic
#     - Autoplot class is mostly implemented
#     - Plot logic split from Autoplot
#     - Specifing dataFile by directory is fixed
#  * Moved legacy code to separate file (autoplotlegacy.py)
#  * Renamed main_new() to main()
#  * Refuse to run Plot.plotData() method if data has not been loaded (raises Exception)
#     - Pick a more specific Exception type class
#  Notes:
#   * return values for methods have been retained but are unused
#   * 

# Rene Zeto: 
# * remove decimal implementation
# * remove none filling (was there to support the odd case of missing data, but better to just throw an error)
# * font implementation
# * commit testing system (let's make sure it works before we commit!)
# * would like to move default commands dict to a config file. 

matplotlib.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
# matplotlib.rc('text', usetex=True)

# Autoplot takes a file location pointing to a list of plotting jobs and
# creates a Plot object for each job.
class Autoplot():
    ## Review python documnetation on classes to make sure I get this right..
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
        ## Load defaults from config file here, e.g.,
        # defaultCommands = loadDefaults()
        plots = []
        with open(jobPath) as jobFile:
            numJobs = 0
            for line in jobFile:
                commands = self.setKWArgs(line)
                if commands["data"] is not None:
                    if os.path.isdir(commands['data'])==False:
                        plots.append(Plot(commands))
                        numJobs += 1
                    else:
                        filePath = commands['data']
                        # Handles directory batch plotting (occurs when data kwarg is a directory and not a file)
                        for fileName in glob.iglob("%s/*.%s"%(filePath,commands['data_type'])):
                            commands['data'] = fileName
                            plots.append(Plot(commands))
                            numJobs += 1
                else:
                    # Probably a blank line, or unspecified data (can't make a plot out of this)
                    continue
        self.numJobs = numJobs 
        self.plots = plots
        
    ## Deleted countJobs(), job done by __init__() now (jwo)
        
    def setKWArgs(self, line):
        # Return commands dictionary with entries read from line in jobFile and the defaults
        commands = self.defaultCommands.copy()
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
        commands.update(inputCommands)
        return commands
    
    def processJobs(self):
    # Process each Plot one at a time
    ## This logic should be enhanced later (e.g,. by processing plots in parallel).
        for plot in self.plots:
            plot.loadData()
            plot.plotData()

    # TODO: progress bar needs to be implemented differently
    def progBar(self):
        pass

# a Plot object represents a single plotting job
class Plot():
    def __init__(self, commands):
        self.commands = commands
        self.dataContainer = None
 
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
        if self.dataContainer is None:
            # Somebody fucked up. Refuse to run this.
            raise Exception
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

def main():
    if len(sys.argv) < 2:
        # User did not provide an input file, use default
        jobPath = "autoplotlist.txt"
    else: 
        # Use file provided on command line
        ## TODO: change working directory to location of jobPath
        jobPath = sys.argv[1]
    # give jobPath to autoplot and make it work its magic
    ## TODO: Handle case where jobPath points to a nonexistent file
    ## TODO: Handle case where the data file for the job is missing
    if not os.path.exists(jobPath):
        
    autoplot = Autoplot(jobPath)
    autoplot.processJobs()
    print "\n Finished."
    return 0

# run main()
if __name__ == "__main__":
    main()
