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
        multipleDataContainer = []
        for fileName in glob.iglob("testdata/*.%s"%(commands['data_type'])):
            commands['data'] = fileName
            multipleDataContainer += loadData(commands)
        return multipleDataContainer

def plotData(commands, dataContainer):
    plotType = commands["plot_type"]
    plotCLKwargs = eval(commands["plot_kwargs"])
    if plotType=="line":
        for i,dataFile in enumerate(dataContainer):
            xData = dataFile[commands["x_data"]]
            dataFile.pop(commands["x_data"])
            for j,dataSet in enumerate(dataFile):
                plt.figure()
                plt.plot(xData,dataSet,**plotCLKwargs)
                plt.xlabel(commands['xlabel'])
                plt.ylabel(commands['ylabel'])
                plt.title(commands['title'])
                plt.savefig("%03d_%03d_%s"%(i,j,commands["fname"]))
    return 0

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
            commands = { 
                "fname": "unnamed_fig_%d.png"%lineNum,
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
                "animate": 0
                }
            if "#" in line:
                line = re.findall("^(.*?)(?=\s#|#)",line)[0]
            inputCommands = parseCL(line)
            commands.update(inputCommands)
            if commands["data"] is not None:
                loadedData = loadData(commands)
                plotData(commands,loadedData)
                print "Finished figure %d/%d."%(lineNum+1,numJobs)
            elif commands["data"] is None:
                print "Error: Data missing from %s on line %d; failed to generate figure."%(jobPath,lineNum+1)

if __name__ == "__main__":
    main()
