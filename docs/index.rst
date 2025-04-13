Welcome to DSSATTools documentation!
====================================

DSSATTools library allows the user to create low-code scripts to run simulations using the DSSAT modeling framework. DSSATTools version 3 includes significant changes when compared to previous versions. The newer is more intuitive for the users familiar with the model, the DSSAT GUI, and the DSSAT file creation tools. Therefore, if you are new to DSSAT I highly recommend you to familiarize yourself with the model, the GUI, and the file creation Tools before jumping into using this library.

DSSATTools implements an object-based approach to define DSSAT simulation input. This aims to mimic the process of creating the DSSAT input files (SOL, WTH, FileX) using the DSSAT GUI Tools. Then, the same way that XBuild has one menu for each FileX section (e.g. Cultivar, Soil Analysis, Planting Date, etc.), there is one DSSATTools class for each section of the FileX. Also, there is one class for the WTH file, and one class for the SOL file. 

The `filex`` module contains all the classes that represent each of the FileX sections. All the FileX sections are implemented excepting enviromental modifications. The `crop`` module contains the Crop classes, one per crop. Such classes represent the crop and their cultivar and ecotype parameters. The `soil` module contains the SoilProfile class, which represents a single soil profile. The `weather`` module hosts the WeatherStation class, which represents the Weather Station file (WTH).

Contents
--------

.. toctree::
   Home <self>
   api