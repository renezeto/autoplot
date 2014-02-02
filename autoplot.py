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
import decimal

# Justin O'Neil: commenting code

matplotlib.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
# matplotlib.rc('text', usetex=True)

def setCommands(line):
    # Return a dictionary containing commands parsed from a line with entries of the form "parameter=argument" and "-flag".
    
    # default parameters
    commands = { 
        "data": None,                   # Path of CSV data file
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
        "labelsize":36                  #
        }
    # Handle comments at the end of the line (marked with #)
    if "#" in line:
        line = re.findall("^(.*?)(?=\s#|#)",line)[0]

    # Find all parameter="argument" keywords and -flag flags
    kwargs = re.findall("\w+=\"[\\\\()\w,.'=\s*/{:}-]+\"",line)
    flags = re.findall("\-\w+",line)
    
    # Update kwargs and add flags commands
    inputCommands = {}                       
    for kwarg in kwargs:
        key, value = tuple(kwarg.split("=",1))
        value = value.replace("\"","") # Handle lines split with \
        inputCommands[key]=value
    for flag in flags:
        key, value = flag.replace("-",""), 1 # Remove - prefix, set value to 1  ## Why not use the handy boolean data type??
        inputCommands[key]=value
    commands.update(inputCommands)        
    return commands

def loadData(commands):
    dataContainer = []
    numEntries = 0
    fileLoc = commands['data']
    with open(fileLoc) as dataFile:
        iterNum = 0
        for line in dataFile:
            if re.search("[a-zA-Z]",line)!=None:
                # Discard lines containing text
                continue
            ## Why is it necessary to deviate from built in python floats here? I'm not sure I understand what's going on here.
            ## It seems like you are checking the number of entries in the row against the length of the dataContainer list and
            ## filling it out with Nones.
            dataRow = [decimal.Decimal(i) for i in re.findall(r"[-+]?\d*\.\d+|\d+",line)]
            if len(dataRow) > len(dataContainer):
                dataContainer += [[None for i in range(iterNum)] for j in range(len(dataRow))]
                numEntries = len(dataRow)
            for i in range(numEntries):
                try:
                    dataContainer[i] += [dataRow[i]]
                except IndexError:
                    dataContainer[i] += [None]
                    print "Warning: Missing data in column %d, data row %d. None placed at missing entry position."%(i+1,iterNum+1)
                iterNum += 1
    dataContainer = [np.array(dataColumn) for dataColumn in dataContainer]
    return dataContainer
    
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
        plt.title(commands['title'])
        x1, x2 = plt.xlim()
        y1, y2 = plt.ylim()
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
    prefix = ' %3d%%'%(percent)
    progress = int(percent/2)
    bar_size = 50
    remain = bar_size - progress
    bar = '|' * progress + ' ' * remain
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
                    for fileName in glob.iglob("%s/*.%s"%(filePath,commands['data_type'])):
                        commands['data'] = fileName
                        loadedData = loadData(commands)
                        plotData(commands,loadedData)
                sys.stdout.write(' Working: '+ progBar(((lineNum+1)/numJobs)*100)+' '+ commands['data'] + ' '*25 +'\r')
                sys.stdout.flush()
            #elif commands["data"] is None: # No need for another test
            else:
                continue
    print "\n Finished."
    return 0 

if __name__ == "__main__":
    main()
