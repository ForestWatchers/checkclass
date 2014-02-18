#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Citizen Cyberscience Centre
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

import osr
import math
import urllib2
import json
import os
import datetime
import gdal
from gdalconst import *
from optparse import OptionParser

def frange(x, y, step):
    """Float Range Generator function"""
    while x < y:
        yield x
        x += step

def delete_app(api_url, api_key, id):
    """
    Deletes the application.

    :arg integer id: The ID of the application
    :returns: True if the application has been deleted
    :rtype: boolean
    """
    request = urllib2.Request(api_url + '/api/app/' + str(id) + '?api_key=' + api_key)
    request.get_method = lambda: 'DELETE'

    if (urllib2.urlopen(request).getcode() == 204): 
        return True
    else:
        return False

def update_app(api_url , api_key, id, name = None):
    """
    Updates the name of the application
    
    :arg integer id: The ID of the application
    :arg string name: The new name for the application
    :returns: True if the application has been updated
    :rtype: boolean
    """
    data = dict(id = id, name = name)
    data = json.dumps(data)
    request = urllib2.Request(api_url + '/api/app/' + str(id) + '?api_key=' + api_key)
    request.add_data(data)
    request.add_header('Content-type', 'application/json')
    request.get_method = lambda: 'PUT'

    if (urllib2.urlopen(request).getcode() == 200): 
        return True
    else:
        return False

def update_template(api_url, api_key, app='checkClassAwa'):
    """
    Update tasks template and long description for the application

    :arg string app: Application short_name in PyBossa.
    :returns: True when the template has been updated.
    :rtype: boolean
    """
    request = urllib2.Request('%s/api/app?short_name=%s' %
                              (api_url, app))
    request.add_header('Content-type', 'application/json')

    res = urllib2.urlopen(request).read()
    res = json.loads(res)
    res = res[0]
    if res.get('short_name'):
        # Re-read the template
        file = open('template.html')
        text = file.read()
        file.close()
        # Re-read the long_description
        file = open('long_description.html')
        long_desc = file.read()
        file.close()
        # Re-read the tutorial
        file = open('tutorial.html')
        tutorial = file.read()
        file.close()
        info = dict(thumbnail=res['info']['thumbnail'], 
                task_presenter=text,
                tutorial=tutorial)
        data = dict(id=res['id'], name=res['name'],
                    short_name=res['short_name'],
                    description=res['description'], hidden=res['hidden'],
                    long_description=long_desc,
                    info=info)
        data = json.dumps(data)
        request = urllib2.Request(api_url + '/api/app/' + str(res['id']) + \
                                  '?api_key=' + api_key)
        request.add_data(data)
        request.add_header('Content-type', 'application/json')
        request.get_method = lambda: 'PUT'

        if (urllib2.urlopen(request).getcode() == 200):
            return True
        else:
            return False

    else:
        return False

def update_tasks(api_url, api_key, app='checkClassAwa'):
    """
    Update tasks question 

    :arg string app: Application short_name in PyBossa.
    :returns: True when the template has been updated.
    :rtype: boolean
    """
    request = urllib2.Request('%s/api/app?short_name=%s' %
                              (api_url, app))
    request.add_header('Content-type', 'application/json')

    res = urllib2.urlopen(request).read()
    res = json.loads(res)
    app = res[0]
    if app.get('short_name'):
        request = urllib2.Request('%s/api/task?app_id=%s&limit=%s' %
                                  (api_url, app['id'],'1000'))
        request.add_header('Content-type', 'application/json')

        res = urllib2.urlopen(request).read()
        tasks = json.loads(res)

        for t in tasks:
            t['info']['question']=u'Should the selected area be classified as Forest or Non-Forest?'
            data = dict(info=t['info'],app_id=t['app_id'])
            data = json.dumps(data)
            request = urllib2.Request(api_url + '/api/task/' + str(t['id']) + \
                                      '?api_key=' + api_key)
            request.add_data(data)
            request.add_header('Content-type', 'application/json')
            request.get_method = lambda: 'PUT'

            if (urllib2.urlopen(request).getcode() != 200):
                return False
            else:
                print "TASK %s updated" % (t['id'])

    else:
        return False

def create_app(api_url , api_key, name=None, short_name=None, description=None,\
        template="template.html", tut="tutorial.html", long_desc="long_description.html"):
    """
    Creates the application. 

    :arg string name: The application name.
    :arg string short_name: The slug application name.
    :arg string description: A short description of the application. 

    :returns: Application ID or 0 in case of error.
    :rtype: integer
    """
    print('Creating app')
    name = u'Correct classification - Awá-Guajá- 2014'
    short_name = u'checkClassAwa'
    description = u'Help us to correct the automatic classification for the Awá-Guajá area'
    # JSON Blob to present the tasks for this app to the users
    # First we read the template:
    file = open(template)
    text = file.read()
    file.close()
    file = open(tut)
    text_tutorial = file.read()
    file.close()
    file = open(long_desc)
    long_description = file.read()
    file.close()
    info = dict (thumbnail="http://imageshack.com/a/img600/9343/sjwh.jpg",
                 task_presenter = text, tutorial = text_tutorial)
    data = dict(name = name, short_name = short_name, description = description,
               hidden = 0, info = info, long_description = long_description,
               category_id = 1)
    data = json.dumps(data)

    # Checking which apps have been already registered in the DB
    apps = json.loads(urllib2.urlopen(api_url + '/api/app' + '?api_key=' + api_key\
            + '&short_name=' + short_name).read())
    for app in apps:
        print app['short_name']
        if app['short_name'] == short_name: 
            print('{app_name} app is already registered in the DB'.format(app_name = name))
            print('Deleting it!')
            if (delete_app(api_url, api_key, app['id'])): print "Application deleted!"
    print("The application is not registered in PyBOSSA. Creating it...")
    # Setting the POST action
    request = urllib2.Request(api_url + '/api/app?api_key=' + api_key )
    request.add_data(data)
    request.add_header('Content-type', 'application/json')

    # Create the app in PyBOSSA
    output = json.loads(urllib2.urlopen(request).read())
    if (output['id'] != None):
        print("Done!")
        return output['id']
    else:
        print("Error creating the application")
        return 0

def getLatLon (nameFile):
    """
    Get Upper Left and Lower Right Latitude/Longitude from image

    :arg string nameFile: Name of the file to be analysed
    :returns: The width, height of the image and the lat/long position of the upper left and lower right corners
    :rtype float:
    """
    imageData = gdal.Open(nameFile)
    geoTransf = imageData.GetGeoTransform()
    width = imageData.RasterXSize
    height = imageData.RasterYSize
    minX = geoTransf[0]
    minY = geoTransf[3] + width*geoTransf[4] + height*geoTransf[5]
    maxX = geoTransf[0] + width*geoTransf[1] + height*geoTransf[2]
    maxY = geoTransf[3]
    return width, height, minX, maxX, minY, maxY

def create_task(api_url , api_key, app_id, fileSatellite, fileClass, fileProb):
    """
    Creates tasks for the application

    :arg integer app_id: Application ID in PyBossa.
    :returns: Task ID in PyBossa.
    :rtype: integer
    """
    ##################
    # Classification
    ##################
    
    #Opening file
    dataClass = gdal.Open(fileClass, GA_ReadOnly)
    if dataClass is None:
        print 'Error opening file!'
        exit

    #Info on file
    classXsize = dataClass.RasterXSize
    classYsize = dataClass.RasterYSize
    classNbands = dataClass.RasterCount

    #Read values in band
    valueClass = []
    for item in range(classNbands):
        bandClass = dataClass.GetRasterBand(item+1)
        valueClass.append(bandClass.ReadAsArray())

    #Closing file
    dataClass = None

    ###############
    # Probability
    ###############
    
    #Opening file
    dataProb = gdal.Open(fileProb, GA_ReadOnly)
    if dataProb is None:
        print 'Error opening file!'
        exit

    #Info on file
    probXsize = dataProb.RasterXSize
    probYsize = dataProb.RasterYSize
    probNbands = dataProb.RasterCount

    #Read values in band
    valueProb = []
    for item in range(probNbands):
        bandProb = dataProb.GetRasterBand(item+1)
        valueProb.append(bandProb.ReadAsArray())

    ###########################################
    # Geographic information for XY transform
    ###########################################
    # Read geotransform matrix
    # Example: http://svn.osgeo.org/gdal/trunk/gdal/swig/python/samples/tolatlong.py
    geomatrix = dataProb.GetGeoTransform()

    # Build Spatial Reference object based on coordinate system, fetched from the opened dataset
    srs = osr.SpatialReference()
    srs.ImportFromWkt(dataProb.GetProjection())
    srsLatLong = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srs, srsLatLong)

    #Closing file
    dataProb = None

    ####################################
    # Mask application and task creation
    ####################################
    newTask = []
    maskSize = 3
    maskBorder = int(math.floor(maskSize/2))
    uncertainty = 230.0
    counterTasks = 0
    for j in range(0+maskBorder,probXsize-maskBorder,maskSize):
        for i in range(0+maskBorder,probYsize-maskBorder,maskSize):
            singleClass = [valueClass[0][i][j],valueClass[1][i][j],valueClass[2][i][j]]
            if (singleClass != [0,0,0]):
                singleProb = valueProb[0][i][j]
                sumProbMask = (float(valueProb[0][i-1][j-1]) + float(valueProb[0][i][j-1]) + float(valueProb[0][i+1][j-1]) +
                               float(valueProb[0][i-1][j])   + float(valueProb[0][i][j])   + float(valueProb[0][i+1][j]) +
                               float(valueProb[0][i-1][j+1]) + float(valueProb[0][i][j+1]) + float(valueProb[0][i+1][j+1]))
                if (sumProbMask < uncertainty):
                    # Counter the number of tasks
                    counterTasks = counterTasks + 1
                    # Calculate ground coordinates
                    X = geomatrix[0] + geomatrix[1] * j + geomatrix[2] * i
                    Y = geomatrix[3] + geomatrix[4] * j + geomatrix[5] * i
                    # Shift to the center of the pixel
                    X += geomatrix[1] / 2.0
                    Y += geomatrix[5] / 2.0
                    # Transform!!!
                    (lon, lat, height) = ct.TransformPoint(X, Y)
                    # Inform
                    print i, j, lat, lon
                    # Add in the structure
                    newTask.append([i, j, lat, lon])

    # Create a task per extent
    for e in newTask:
        # Data for the tasks
        t    = dict (x = e[0],
                     y = e[1],
                     lat = e[2],
                     lon = e[3]
                )
        info = dict (tile=t, question=u'Should the selected area be classified as Forest or Non-Forest?')
        data = dict (app_id = app_id, state = 0, info = info, calibration = 0, priority_0 = 0, n_answers = 30)
        data = json.dumps(data)

        # Setting the POST action
        request = urllib2.Request(api_url + '/api/task' + '?api_key=' + api_key)
        request.add_data(data)
        request.add_header('Content-type', 'application/json')

        # Create the task
        output = json.loads(urllib2.urlopen(request).read())
        if (output['id'] == None):
            return False


import sys
if __name__ == "__main__":
    # Arguments for the application
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    
    parser.add_option("-s", "--server", dest="api_url", help="PyBossa URL http://domain.com/", metavar="URL")
    parser.add_option("-k", "--api-key", dest="api_key", help="PyBossa User API-KEY to interact with PyBossa", metavar="API-KEY")
    parser.add_option("-t", "--template", dest="template", help="PyBossa HTML+JS template for application presenter", metavar="TEMPLATE")
    parser.add_option("-b", "--tutorial", dest="tutorial", help="App tutorial template for application presenter", metavar="TUTORIAL")
    parser.add_option("-g", "--long-description", dest="long_desc", help="Long description for the application", metavar="LONG")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    # Create App
    parser.add_option("-a", "--create-app", action="store_true",
                      dest="create_app",
                      help="Create the application",
                      metavar="CREATE-APP")

    # Update template for tasks and long_description for app
    parser.add_option("-u", "--update-template", action="store_true",
                      dest="update_template",
                      help="Update Tasks template",
                      metavar="UPDATE-TEMPLATE"
                     )
    # Update tasks question
    parser.add_option("-q", "--update-tasks", action="store_true",
                      dest="update_tasks",
                      help="Update Tasks question",
                      metavar="UPDATE-TASKS"
                     )

    # Files
    parser.add_option("-i", "--file-satellite",
                  dest="fileSatellite",
                  help="Satellite image",
                  metavar="FILE-SAT"
                 )
    parser.add_option("-c", "--file-classification",
                  dest="fileClass",
                  help="ANN classification image",
                  metavar="FILE-CLASS"
                 )
    parser.add_option("-p", "--file-probability",
                  dest="fileProb",
                  help="ANN probability image",
                  metavar="FILE-PROB"
                 )

    (options, args) = parser.parse_args()

    if not options.api_url:
        options.api_url = 'http://localhost:5000'

    if not options.api_key:
        parser.error("You must supply an API-KEY to create an applicationa and tasks in PyBossa")

    if not options.template:
        print("Using default template: template.html")
        options.template = "template.html"

    if not options.tutorial:
        print("Using default tutorial template: tutorial.html")
        options.tutorial = "tutorial.html"

    if not options.long_desc:
        print("Using default long description template: long_description.html")
        options.long_desc = "long_description.html"

    if not options.fileSatellite:
        parser.error("You must supply a satellite image")
    else:
        fileSatellite = options.fileSatellite

    if not options.fileClass:
        parser.error("You must supply a ANN classification image")
    else:
        fileClass = options.fileClass

    if not options.fileProb:
        parser.error("You must supply a ANN probability image")
    else:
        fileProb = options.fileProb

    if (options.verbose):
       print('Running against PyBosssa instance at: %s' % options.api_url)
       print('Using API-KEY: %s' % options.api_key)

    if options.update_template:
        print "Updating app template"
        update_template(options.api_url, options.api_key)

    if options.update_tasks:
        print "Updating task question"
        update_tasks(options.api_url, options.api_key)

    if options.create_app:
        app_id = create_app(options.api_url, options.api_key,\
                 short_name="checkClassAwa",
                 template = options.template, tut = options.tutorial,
                 long_desc = options.long_desc)
        create_task(options.api_url, options.api_key, app_id, fileSatellite, fileClass, fileProb)
    if not options.create_app and not options.update_template:
        parser.error("Please check --help or -h for the available options")
