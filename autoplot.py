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

#setCommands() handles commands.
#main() handles files.
#loadData() handles data.
#plotData() handles plots.

#to do:
#subplot management
#xrange, yrange
#prettier default plots

def setCommands(line):
    commands = { 
        "data": None,
        "data_type": "CSV",
        "dpi": 100,
        "plot_type": "line",
        "plot_kwargs": "{}",
        "x_data": 0,
        "xlabel": "label your x axis!",
        "ylabel": "label your y axis!",
        "title": "",
        "scope": 0,
        "animate": 0,
        "aspect": .35
        }
    if "#" in line:
        line = re.findall("^(.*?)(?=\s#|#)",line)[0]
    kwargs = re.findall("\w+=\"[()\w,.'=\s/{:}-]+\"",line)
    flags = re.findall("\-\w+",line)
    inputCommands = {}
    for kwarg in kwargs:
        key, value = tuple(kwarg.split("=",1))
        value = value.replace("\"","")
        inputCommands[key]=value
    for flag in flags:
        key, value = flag.replace("-",""), 1
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
                continue
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
        fig, axs = plt.subplots(1, 1)
        fname = commands['data'][:-4]
        xData = dataContainer[commands["x_data"]]
        dataContainer.pop(commands["x_data"])
        for dataSet in dataContainer:
            axs.plot(xData,dataSet,**plotCLKwargs)
            plt.xlabel(commands['xlabel'])
            plt.ylabel(commands['ylabel'])
            plt.title(commands['title'])
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
    if len(sys.argv) < 2:
        jobPath = "autoplotlist.txt"
    else: 
        jobPath = sys.argv[1]
    try:
        with open(jobPath,"r") as jobFile:
            for numJobs, line in enumerate(jobFile):
                pass
        numJobs += 1
    except:
        print "Error: Unable to open jobs file '%s'."%jobPath
        return 1
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
                sys.stdout.write(' Working: '+ progBar(((lineNum+1)/numJobs)*100)+' '+ commands['data'] + ' '*15 +'\r')
                sys.stdout.flush()
            elif commands["data"] is None:
                continue
    print "\n Finished."
    return 0

if __name__ == "__main__":
    main()
