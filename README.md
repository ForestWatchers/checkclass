Best Tile for this area
=======================

Satellite images are not perfect: the day will be covered with clouds and you
will not be able to see anything, of area was not covered and you will see
a white strip.

In order to solve this problem, experts analyze several images of the same area
and pick the best "sections" to join them in the best possible image: minimum
number of clouds, and broken areas.

This ForestWatchers application tries to replicate this procedure presenting
a set of images for the same area and asking the volunteers to pick the best
ones. Once all the area is covered, the selected sections will be merged into
one final image to procedure with the next steps of deforestation assesment.

Creating Tasks in PyBossa
=========================

This web application uses the [PyBossa framework](http://pybossa.com) in order
to manage the tasks and distribute them among the volunteers. 

The application has three main items:

 * **createTask.py** script to create the tasks for the application,
 * **template.html**: the web application (it requests a task and loads it for
   the user),
 * **tutorial.html**: a tutorial about the application (for the moment only one
   video, we will finish this soon!).

If you want to create your own application you will need the following
structure for the application:

 * A folder with several raster images of the same area:
     * demo/2012-01-01.tif
     * demo/2012-02-02.tif
     * demo/...

The folder name is the area that you want to analyze, and the raster images
should be named according to the following format: **%Y-%M-%D.tif**.

The script will read the firs raster image, compute sub-areas or sub-tiles to
show to the volunteers and create the tasks in PyBossa. The structure of the
tasks is the following:

```
 {
    "info": {
      "tile": {
        "tiles": [
          "2012-01-01.tif",
          "2012-01-02.tif",
          "2012-01-03.tif"
        ],
        "projection": "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0],UNIT[\"degree\",0.0174532925199433],AUTHORITY[\"EPSG\",\"4326\"]]",
        "restrictedExtent": [
          -55.908811789016355,
          -10.105939376000004,
          -55.77804053901635,
          -9.989690469750004
        ],
        "bounds": [
          -57.739609289016386,
          -12.430917501000005,
          -53.554929289016385,
          -8.710952501000005
        ],
        "height": 1657,
        "width": 1864,
        "name": "demo"
      },
      "question": "Which is the best tile for this area?"
    },
    ....
  },
```


The script creates the info section.

Requirements
============

If you want to use this application you will need a map server serving the
tiles. Then, you will have to install PyBossa and follow the documentation to
run the software and create the application.
