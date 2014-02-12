#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Instituto Nacional de Pesquisas Espaciais (INPE)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
import gdal
import json
import time
import shutil
import urllib2
import requests
import datetime
from gdalconst import *
from optparse import OptionParser

def getAppId(server, appName):
    """
    Get the application id given the short name

    :arg string server: Address of the server
    :arg string appName: Short name of the application
    :returns: Numerical id of the application
    :rtype: integer
    """
    JSONdata = urllib2.urlopen(url=server+"/api/app?short_name="+ \
        appName).read()
    data = json.loads(JSONdata)
    appId = data[0]['id']
    return appId

def getTasks(server, appId, maxNumberTasks, completedOnly):
    """
    Get the tasks of a particular application from the server.

    :arg string server: Address of the server
    :arg string appId: ID of the application to be analysed
    :arg integer maxNumberTasks: Maximum number of tasks to be downloaded
    :arg int completedOnly: If we'll get only completed tasks
    :returns: Tasks info for the application
    :rtype: dictionary
    """
    if completedOnly == 1:
        JSONdata = urllib2.urlopen(url=server+"/api/task?app_id="+ \
            str(appId)+"&state=completed&limit="+ \
            str(maxNumberTasks)).read()
    else:
        JSONdata = urllib2.urlopen(url=server+"/api/task?app_id="+ \
            str(appId)+"&limit="+str(maxNumberTasks)).read()
    data = json.loads(JSONdata)
    numberTasks = len(data)
    tasksInfo = []
    for item in range(numberTasks):
        tasksInfo.append({'taskId':data[item]['id'], \
            'area':data[item]['info']['tile']})
    return tasksInfo

def getResults(server, tasksInfo, maxNumberAnswers):
    """
    Get the results of a particular application from the server.

    :arg string server: Address of the server
    :arg integer maxNumberAnswers: Maximum number of answers per task to be downloaded
    :arg list tasksInfo: List of tasks
    :returns: Results for the application
    :rtype: dictionary
    """
    answersApp = []
    numberTasks = len(tasksInfo)
    for item in range(numberTasks):
        answersApp.append([])
        JSONdata = urllib2.urlopen(url=server+"/api/taskrun?task_id="+ \
            str(tasksInfo[item]['taskId'])+"&limit="+ \
            str(maxNumberAnswers)).read()
        data = json.loads(JSONdata)
        lenData = len(data)
        for ans in range(lenData):
            #print data[ans]['info'].values()
            #print data[ans]['info'].values()[0]
            answersApp[item].append({'taskId':data[ans]['task_id'], \
            'id':data[ans]['id'], 'answer':data[ans]['info'].values()[0]})
    return answersApp

def genStats(data, printStats = 0):
    """
    Calculate statistics about the results

    :arg list dict data: Dictionary list with all the results.

    :returns: Matrix with answers count for each task
    :rtype: list
    """
    tileCount = []
    numberTasks = len(data)
    for task in range(numberTasks):
        tileCount.append([0] * 2)
        numberResults = len(data[task])
        for result in range(numberResults):
            if data[task][result]['answer'] == 1:
                tileCount[task][0] += 1
            elif data[task][result]['answer'] == 2:
                tileCount[task][1] += 1
        #Print info for debug
        if printStats == 1:
            print "Stats for task " + str(task)
            print "Vote 1 = " + str(tileCount[task][0])
            print "Vote 2 = " + str(tileCount[task][1])
            print "Maximum value = " + str(max(tileCount[task]))
            print "Position = " + str(tileCount[task].index(max(tileCount[task])))
            print ""
    return tileCount

def cutBestTiles(tasksInfo, results, origLocation, destLocation, \
    completedOnly, nAnswers = 0):
    """
    Cut the best tiles based on the results obtained by genStats

    :arg list dict tasks: Dictionary list with the tasks info.
    :arg list dict results: Dictionary list with the processed results.
    :arg string origLocation: Directory with orginal images.
    :arg string origLocation: Directory for the results.
    :arg int completedOnly: If we are processing only completed tasks
    :arg int nAnswers: Mininum number of answers to be considered

    :returns: Nothing
    :rtype: None
    """
    #~ tmpMosaic = destLocation+"/tmpMosaic_n"+str(nAnswers)+"/"
    #~ createDir(tmpMosaic)
    #~ tmpIntensity = destLocation+"/tmpIntensity_n"+str(nAnswers)+"/"
    #~ createDir(tmpIntensity)
    #~ tmpHeat = destLocation+"/tmpHeat_n"+str(nAnswers)+"/"
    #~ createDir(tmpHeat)

    #~ intensity = 1
    #~ heat = 1
    #~ formatFile = "GTiff"
    #~ driver = gdal.GetDriverByName(formatFile)

    #Open file containing geoinfo on best result
    if completedOnly == 1:
        f = open(destLocation+'/bestInfo.txt','w')

    numberTasks = len(tasksInfo)
    for task in range(numberTasks):
        #Checking if the task has the mininum number of answers
        if (sum(results[task]) < nAnswers):
            #If it has not, lets go to the next task
            continue
        #Geting the selected day for each task
        taskId = tasksInfo[task]['taskId']
        definedArea = tasksInfo[task]['area']
        selectedTile = results[task].index(max(results[task]))
        if selectedTile == 0:
            selectedFile = 'Forest'
        elif selectedTile == 1:
            selectedFile = 'Non-Forest'
        print taskId
        print selectedFile
        print definedArea
        
        #~ #Printing bestInfo
        #~ if completedOnly == 1:
            #~ f.write(str(definedArea[0])+" "+ str(definedArea[1])+" "+\
            #~ str(definedArea[2])+" "+str(definedArea[3])+"\n")
        #~ cmd = "gdal_translate -projwin "+str(definedArea[0])+" "+ \
            #~ str(definedArea[3])+" "+str(definedArea[2])+" "+ \
            #~ str(definedArea[1])+" "+origLocation+selectedFile+".tif "+ \
            #~ tmpMosaic+str(taskId)+".tif"
        #~ os.system(cmd)
        #~ #Creating intensity map
        #~ if intensity == 1:
            #~ origCut = tmpMosaic+str(taskId)+".tif"
            #~ colourCut = tmpIntensity+str(taskId)+".tif"
            #~ if os.path.isfile(origCut):
                #~ shutil.copy(origCut, colourCut)
                #~ pointFile = gdal.Open(colourCut, 2)
                #~ votes = max(results[task])
                #~ for item in range(pointFile.RasterCount):
                    #~ data = pointFile.GetRasterBand(item+1).ReadAsArray()
                    #~ if item == 1:
                        #~ newData = (data * 0) + int(votes * 8)
                    #~ else:
                        #~ newData = (data * 0)
                    #~ pointFile.GetRasterBand(item+1).WriteArray(newData)
                #~ pointFile = None
        #~ #Creating heat map
        #~ if heat == 1:
            #~ origCut = tmpMosaic+str(taskId)+".tif"
            #~ heatCut = tmpHeat+str(taskId)+".tif"
            #~ if os.path.isfile(origCut):
                #~ shutil.copy(origCut, heatCut)
                #~ pointFile = gdal.Open(heatCut, 2)
                #~ #Calculating level of agreement
                #~ votes = max(results[task])
                #~ totalVotes = sum(results[task])
                #~ agree = float(votes)/float(totalVotes)
                #~ print 'Task ', task, ' -> ', votes, totalVotes, agree
                #~ #Getting bands
                #~ data1 = pointFile.GetRasterBand(1).ReadAsArray()
                #~ data2 = pointFile.GetRasterBand(2).ReadAsArray()
                #~ data3 = pointFile.GetRasterBand(3).ReadAsArray()
                #~ #Seting colours based on agreement
                #~ if agree == 0.0:
                    #~ newData1 = (data1 * 0) + int(255)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(0)
                #~ elif agree > 0.0 and agree < 0.1:
                    #~ newData1 = (data1 * 0) + int(229)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(0)
                #~ elif agree >= 0.1 and agree < 0.2:
                    #~ newData1 = (data1 * 0) + int(204)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(0)
                #~ elif agree >= 0.2 and agree < 0.3:
                    #~ newData1 = (data1 * 0) + int(178)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(0)
                #~ elif agree >= 0.3 and agree < 0.4:
                    #~ newData1 = (data1 * 0) + int(153)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(0)
                #~ elif agree >= 0.4 and agree < 0.5:
                    #~ newData1 = (data1 * 0) + int(127)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(0)
                #~ elif agree >= 0.5 and agree < 0.6:
                    #~ newData1 = (data1 * 0) + int(0)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(127)
                #~ elif agree >= 0.6 and agree < 0.7:
                    #~ newData1 = (data1 * 0) + int(0)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(153)
                #~ elif agree >= 0.7 and agree < 0.8:
                    #~ newData1 = (data1 * 0) + int(0)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(178)
                #~ elif agree >= 0.8 and agree < 0.9:
                    #~ newData1 = (data1 * 0) + int(0)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(204)
                #~ elif agree >= 0.9 and agree < 1.0:
                    #~ newData1 = (data1 * 0) + int(0)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(229)
                #~ elif agree == 1.0:
                    #~ newData1 = (data1 * 0) + int(0)
                    #~ newData2 = (data1 * 0) + int(0)
                    #~ newData3 = (data1 * 0) + int(225)
                #~ #Writing each band of new values
                #~ pointFile.GetRasterBand(1).WriteArray(newData1)
                #~ pointFile.GetRasterBand(2).WriteArray(newData2)
                #~ pointFile.GetRasterBand(3).WriteArray(newData3)
                #~ #Close and save file
                #~ pointFile = None
    #~ #Changing filename based on the type of result (if all results or
    #~ #completed only.
    #~ if completedOnly == 0:
        #~ if nAnswers == 0:
            #~ fileMosaic = "mosaicall"
            #~ fileIntensity = "intensityall"
            #~ fileHeat = "heatall"
        #~ else:
            #~ fileMosaic = "mosaicall"+"_n"+str(nAnswers)
            #~ fileIntensity = "intensityall"+"_n"+str(nAnswers)
            #~ fileHeat = "heatall"+"_n"+str(nAnswers)
    #~ elif completedOnly == 1:
        #~ if nAnswers == 0:
            #~ fileMosaic = "mosaiccompleted"
            #~ fileIntensity = "intensitycompleted"
            #~ fileHeat = "heatcompleted"
        #~ else:
            #~ fileMosaic = "mosaiccompleted"+"_n"+str(nAnswers)
            #~ fileIntensity = "intensitycompleted"+"_n"+str(nAnswers)
            #~ fileHeat = "heatcompleted"+"_n"+str(nAnswers)
    #~ #Checking if the temporary tile folder is not empty
    #~ if os.listdir(tmpMosaic) == []:
        #~ print "No output detected for desired parameter N = " + str(nAnswers)
        #~ #Removing temporary directories
        #~ removeDir(tmpMosaic)
        #~ removeDir(tmpIntensity)
        #~ removeDir(tmpHeat)
        #~ #Returning error code
        #~ resultCut = 1
        #~ return resultCut
    #~ #Merging the tiles into one mosaic
    #~ cmd = "gdal_merge.py -init '200 200 200' -o "+destLocation+fileMosaic+".tif "+tmpMosaic+ \
        #~ "*.tif"
    #~ os.system(cmd)
    #~ cmd = "gdal_merge.py -o "+destLocation+fileIntensity+".tif "+tmpIntensity+ \
        #~ "*.tif"
    #~ os.system(cmd)
    #~ cmd = "gdal_merge.py -o "+destLocation+fileHeat+".tif "+tmpHeat+ \
        #~ "*.tif"
    #~ os.system(cmd)
    #~ #Copying file with timestamp
    #~ now = datetime.datetime.now()
    #~ timeCreation = now.strftime("%Y-%m-%d_%Hh%M")
    #~ shutil.copyfile(destLocation+fileMosaic+".tif", destLocation+ \
        #~ fileMosaic+"_"+timeCreation+".tif")
    #~ shutil.copyfile(destLocation+fileIntensity+".tif", destLocation+ \
        #~ fileIntensity+"_"+timeCreation+".tif")
    #~ shutil.copyfile(destLocation+fileHeat+".tif", destLocation+ \
        #~ fileHeat+"_"+timeCreation+".tif")
    #~ #Close file containing geoinfo on best result
    #~ if completedOnly == 1:
        #~ f.close()
    #~ #Removing temporary directories
    #~ removeDir(tmpMosaic)
    #~ removeDir(tmpIntensity)
    #~ removeDir(tmpHeat)
    #Final state
    resultCut = 0
    return resultCut

def createDir(directory):
    """
    Creates a directory if it doesn't exists

    :arg string directory: Directory to be created.

    :returns: statusCreation
    :rtype: int
    """
    if not os.path.exists(directory):
        statusCreation = os.makedirs(directory)
    else:
        statusCreation = 2
    return statusCreation

def removeDir(directory):
    """
    Removes a directory and all its contents

    :arg string directory: Directory to be created.

    :returns: statusDeletion
    :rtype: int
    """
    if os.path.exists(directory):
        statusDeletion = shutil.rmtree(directory)
    else:
        statusDeletion = 2
    return statusDeletion

def removeOldFiles(directory,daysLimit):
    """
    Removes old files from a directory older than a given limit
    Example from: http://www.jigcode.com/2009/06/07/python-list-files-older-than-or-newer-than-a-specific-date-and-time/

    :arg string directory: Directory to be analysed
    :arg int daysLimit: Limit to remove files

    :returns: statusRemoval
    :rtype: int
    """
    files = os.listdir(directory)
    files = [ f for f in files if re.search('.tif$', f, re.I)]
    now = time.time()
    for file in files:
        if os.stat(directory+file).st_mtime < now - daysLimit * 86400:
            if os.path.isfile(directory+file):
                os.remove(os.path.join(directory, file))
                print "Old file deleted: ", file
    statusRemoval = 0
    return statusRemoval

#######################
# Begin of the script #
#######################

if __name__ == "__main__":

    # Arguments for the application
    usage = "usage: %prog arg1 arg2 ..."
    parser = OptionParser(usage)

    parser.add_option("-s", "--server", dest="server", \
        help="Address to the server", metavar="SERVER")
    parser.add_option("-n", "--app-name", dest="appName", \
        help="Short name of the application", metavar="APPNAME")
    parser.add_option("-t", "--max-number-tasks", type="int", dest="maxNumberTasks", \
        help="Maximum number of tasks to be downloaded", \
        metavar="MAXNUMBERTASKS")
    parser.add_option("-a", "--max-number-answers", type="int", dest="maxNumberAnswers", \
        help="Maximum number of answers to be downloaded", \
        metavar="MAXNUMBERANSWERS")
    parser.add_option("-c", "--completed-only", type="int", dest="completedOnly", \
        help="Get only completed tasks", metavar="COMPLETEDONLY")
    parser.add_option("-i", "--images-directory", dest="imagesDir", \
        help="Directory containing the images", metavar="IMAGESDIR")
    parser.add_option("-d", "--destination-directory", dest="destDir", \
        help="Directory for results", metavar="DESTDIR")
    parser.add_option("-f", "--full-build", type="int", dest="fullBuild", \
        help="Build the full set of results", metavar="FULLBUILD")
    parser.add_option("-r", "--remove-files", type="int", dest="removeFiles", \
        help="Remove files older than D days", metavar="REMOVEFILES")

    (options, args) = parser.parse_args()

    if options.server:
        server = options.server
    else:
        #server = "http://forestwatchers.net/pybossa"
        server = "http://localhost:5000"
    if options.appName:
        appName = options.appName
    else:
        appName = "checkClassRO"
    if options.maxNumberTasks:
        maxNumberTasks = options.maxNumberTasks
    else:
        maxNumberTasks = 72
    if options.maxNumberAnswers:
        maxNumberAnswers = options.maxNumberAnswers
    else:
        maxNumberAnswers = 15
    if options.completedOnly:
        completedOnly = options.completedOnly
    else:
        completedOnly = 1
    if options.imagesDir:
        imagesDir = options.imagesDir
    else:
        imagesDir = "/home/eduardo/ForestWatchers/nextUI/"
    if options.destDir:
        destDir = options.destDir
    else:
        destDir = "/home/eduardo/Testes/fw_img/resultsClass/"
    if options.fullBuild:
        fullBuild = options.fullBuild
    else:
        fullBuild = 0
    if options.removeFiles:
        removeFiles = options.removeFiles
    else:
        removeFiles = 9999

    #Check if we have enought rate to work
    res = requests.get(server+'/api/app')
    remainRate = int(res.headers['x-ratelimit-remaining'])
    if remainRate < 10:
        print 'Now I have to sleep!!!'
        print 'My remaining rate is: ', remainRate
        print ''
        time.sleep(300)
    else:
        print 'I can work.'
        print 'My remaining rate is: ', remainRate
        print ''

    #Get the data and start analysing it
    appId = getAppId(server, appName)
    print 'App ID: ', appId

    #For complete tasks only
    completedOnly = 0
    tasksInfo = getTasks(server, appId, maxNumberTasks, completedOnly)
    results = getResults(server, tasksInfo, maxNumberAnswers)
    stats = genStats(results, 1)
    finalResult = cutBestTiles(tasksInfo, stats, imagesDir, destDir, \
        completedOnly)

    #~ #Clear data
    #~ tasksInfo = None
    #~ results = None
    #~ stats = None
    #~ finalResult = None
#~ 
    #~ #For all tasks
    #~ completedOnly = 0
    #~ tasksInfo = getTasks(server, appId, maxNumberTasks, completedOnly)
    #~ results = getResults(server, tasksInfo, maxNumberAnswers)
    #~ stats = genStats(results, 0)
    #~ #Building for any number of answers
    #~ finalResult = cutBestTiles(tasksInfo, stats, imagesDir, destDir, \
        #~ completedOnly)
#~ 
    #~ #To build the full set of results to ForestWatchers
    #~ if fullBuild == 1:
        #~ #Building for 5 answers at least
        #~ finalResult = cutBestTiles(tasksInfo, stats, imagesDir, destDir, \
            #~ completedOnly, 5)
        #~ #Building for 10 answers at least
        #~ finalResult = cutBestTiles(tasksInfo, stats, imagesDir, destDir, \
            #~ completedOnly, 10)
        #~ #Building for 15 answers at least
        #~ finalResult = cutBestTiles(tasksInfo, stats, imagesDir, destDir, \
            #~ completedOnly, 15)
        #~ #Building for 20 answers at least
        #~ finalResult = cutBestTiles(tasksInfo, stats, imagesDir, destDir, \
            #~ completedOnly, 20)
        #~ #Building for 25 answers at least
        #~ finalResult = cutBestTiles(tasksInfo, stats, imagesDir, destDir, \
            #~ completedOnly, 25)
#~ 
    #~ #To remove files older than D days
    #~ statusRemoval = removeOldFiles(destDir,removeFiles)
