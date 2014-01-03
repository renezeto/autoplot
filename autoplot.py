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

def parseCL(str_type):
    kwargs = re.findall("\w+=\"[()\w,.'=\s/{:}-]+\"",str_type)
    flags = re.findall("\-\w+",str_type)
    kwargDict = {}
    for kwarg in kwargs:
        key, value = tuple(kwarg.split("=",1))
        value = value.replace("\"","")
        kwargDict[key]=value
    for flag in flags:
        key, value = flag.replace("-",""), 1
        kwargDict[key]=value
    return kwargDict

def loadData(commands):
    columnContainer = []
    numEntries = 0
    fileLoc = commands['data']
    if os.path.isdir(fileLoc)==False:
        with open(fileLoc) as dataFile:
            iterNum = 0
            for line in dataFile:
                if re.search("[a-zA-Z]",line)!=None:
                    continue
                dataRow = [decimal.Decimal(i) for i in re.findall(r"[-+]?\d*\.\d+|\d+",line)]
                if len(dataRow) > len(columnContainer):
                    columnContainer += [[None for i in range(iterNum)] for j in range(len(dataRow))]
                    numEntries = len(dataRow)
                for i in range(numEntries):
                    try:
                        columnContainer[i] += [dataRow[i]]
                    except IndexError:
                        columnContainer[i] += [None]
                        print "Warning: Missing data in column %d, data row %d. None placed at missing entry position."%(i+1,iterNum+1)
                iterNum += 1
        singleDataContainer = [[np.array(dataColumn) for dataColumn in columnContainer]]
        return singleDataContainer
    else:
        filePath = commands['data']
        multipleDataContainer = []
        for fileName in glob.iglob("%s/*.%s"%(filePath,commands['data_type'])):
            commands['data'] = fileName
            multipleDataContainer += loadData(commands)
        return multipleDataContainer

def plotData(commands,dataContainer):
    plotType = commands["plot_type"]
    plotCLKwargs = eval(commands["plot_kwargs"])
    if plotType=="line":
        for j, dataFile in enumerate(dataContainer):
            filePath = "./"
            if "/" in commands['data']:
                filePath = re.findall("^(.*[\\\/])",commands['data'])[0]
            fname = "%sfile%d_fig"%(filePath,j)
            xData = dataFile[commands["x_data"]]
            dataFile.pop(commands["x_data"])
            for i,dataSet in enumerate(dataFile):
                multiIndex=""
                if len(dataFile) > 2:
                    multiIndex = "_%02d"%i
                w, h = plt.figaspect(commands['aspect'])
                fig = plt.figure(figsize=(w,h))
                plt.plot(xData,dataSet,**plotCLKwargs)
                plt.xlabel(commands['xlabel'])
                plt.ylabel(commands['ylabel'])
                plt.title(commands['title'])
                plt.savefig("%s%s"%(fname,multiIndex))
    return 0

def progBar(percent):
    prefix = ' %3d%%'%(percent)
    progress = int(percent/2)
    bar_size = 50
    remain = bar_size - progress
    bar = '|' * progress + ' ' * remain
    return prefix + ' [' + bar + ']'

def main():
    global commands
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
            inputCommands = parseCL(line)
            commands.update(inputCommands)
            if commands["data"] is not None:
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
