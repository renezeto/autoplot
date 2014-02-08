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
import subprocess

# RZ: Justin; update this? not sure what comments are current. Also, I have merged into branch master, since this code works,
# and I have created a new release branch called v0.1 for the old one. For each big update, I'll just create a new branch point and 
# freeze it.

# Justin O'Neil: commenting code, reimplimenting program logic to use OOP
# Suggestions/TODO:
#  * matplotlib complains about unclosed figures for larger sets of data. Fix this
#  * Make progress bar work
#  * Keyword argument library
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
#  * Handle case of missing files
#  * Fixed bug resulting in only one plot to be generated per directory of data
#  * Added DocStrings to Autoplot and Plot methods
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
        """Take a path to an autoplot job file and create a list of Plot objects for each job. Returns None."""
        ## Load defaults from config file here, e.g.,
        # defaultCommands = loadDefaults()
        plots = []
        with open(jobPath) as jobFile:
            numJobs = 0
            for line in jobFile:
                commands = self._setKWArgs(line)
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
                    # RZ: There are cases where we wouldn't specify data. e.g. plotting mathematical functions. 
                    continue
        self.numJobs = numJobs 
        self.plots = plots
        
    ## Deleted countJobs(), job done by __init__() now (jwo)

    # RZ: Soon to be obsolete.
    def _setKWArgs(self, line):
        """Private method. Given a line from an autoplot job file, return a dictionary containing its parameters."""
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
        """Process the plots created when the Autoplot object was initialized."""
    # Process each Plot one at a time
    ## This logic should be enhanced later (e.g,. by processing plots in parallel).
    # RZ: Handle parallel processing here.
        for plot in self.plots:
            plot.loadData()
            plot.plotData()

    # TODO: progress bar needs to be implemented differently
    def progBar(self):
        """No-op. Will display a progress bar."""
        pass

# a Plot object represents a single plotting job
class Plot():
    def __init__(self, commands):
        """Given a dictionary of commands, copy commands to the new Plot object and initialize the dataContainer to None"""
        self.commands = commands.copy()
        self.dataContainer = None
 
    def loadData(self):
        """Load the data file specified in the objects command dictionary"""
        # loadData(commands_dict) -> [array(column1), array(column2), array(column3), ..., array(columnN)] -> self.
        # RZ: format is [X, Y1, Y2, Y3]... eventually creates a plot with X vs Y_n for each n. usually n=1.
        # this is because the CSV might have multiple columns, not just two. plotData then plots them on the same plot. (might want to change that later)
        dataContainer = []
        numEntries = 0
        # RZ: Will modify this for plots with no data import later.
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

    # So this function will need a big rewrite. It's not very modular and we can do better now.
    def plotData(self):
        """Generate plot of data loaded from a datafile. Output to PNG image with the same name."""
        if self.dataContainer is None:
            # Somebody fucked up. Refuse to run this.
            raise Exception
        # Always line. This will be handled better in the new function. 
        plotType = self.commands["plot_type"]
        # Basically code injection from the autoplotlist file, to customize the look of the figure
        # this is read into the plot function as **plotCLKwargs
        plotCLKwargs = eval(self.commands["plot_kwargs"])
        # Check if we are doing a line plot. spoiler: we are
        if plotType=="line":
            # Get figure aspect ratio
            w, h = plt.figaspect(self.commands['aspect'])
            # Creates figure, puts 1x1 subplot on it. Never got around to making it support more. 
            # figsize is about the aspect ratio
            fig, axs = plt.subplots(1, 1,figsize=(w,h))
            # Get the file name (remove the extension)
            fname = self.commands['data'][:-4]
            # xData tells us which dataset is the horizontal axis (1st column of csv, 2nd column, 3rd column? etc)
            # all the others are plotted on the vertical axis together
            xData = self.dataContainer[self.commands["x_data"]]
            self.dataContainer.pop(self.commands["x_data"])
            for dataSet in self.dataContainer:
                axs.plot(xData,dataSet,**plotCLKwargs)
            # Plot one theory curve if specified, with the same resolution as the data set. Not ideal.
            if self.commands["theory"] is not None:
                expression=self.commands["theory"]
                x = np.array([float(i) for i in xData])
                curve = eval(expression)
                axs.plot(xData,curve,**plotCLKwargs)
            # Set axis scale. linear, logarithmic, etc. the **eval stuff is for scale-specific kwargs
            # (e.g. ok, you want a log plot. what base?) these are documented in matplotlib and 
            # again not ideal, since we are injecting code
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
            # plot range limits
            plt.xlim([x1,x2])
            plt.ylim([y1,y2])
            # trim whitespace
            plt.tight_layout()
            plt.savefig("%s"%fname)
        return 0

def main():
    """Generate an Autoplot object with default or command-line specified job file. Process it's jobs."""
    if len(sys.argv) < 2:
        # User did not provide an input file, use default
        jobPath = "autoplotlist.txt"
    else: 
        # Use file provided on command line
        ## TODO: change working directory to location of jobPath
        jobPath = sys.argv[1]
    # give jobPath to autoplot and make it work its magic
    try:
        autoplot = Autoplot(jobPath)
    except IOError:
        print "Missing job file. %s does not exist!"%jobPath
        return 1
    try:
        autoplot.processJobs()
    except IOError:
        # Make this error message more descriptive
        print "One or more data files are missing."
        return 1
    print "\n Finished."
    return 0

# run main()
if __name__ == "__main__":
    main()
