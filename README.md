#TODO: Update readme
# Py_DSSATTools
A set of Tools to ease the crop simulation ussing DSSAT

You can install it via pip:

`pip install DSSATTools`

## Introduction
It will be conformed for different modules that will allow the user to sort the data needed to run the model, create the required files to run the model. To run the model you have to have the DSSAT Executable file (Ussually located in DSSAT47/DSCSM047.EXE). The library is a collection of modules to so far allows:
 - Run the model with custom weather, soil, management and crop files. 
 - Read, modify and write crop files (.SPE, .CUL, .ECO)
Some future featrues may include:
 - Read, modify and write Soil, Management, Mowing and Weather Files

 So far to handle DSSAT Files (Except crop files) I recommend to use [tradssat library](https://github.com/julienmalard/traDSSAT).

## Modules
The library contains three modules:
- run: contains the `CSM_EXE` class. That class is used to initialize the model by passing the DSSAT executable path. The model can be run by the method `runDSSAT`. After running the model the results will be available at the `results` attribute, and any output file can be accessed by using the `getOutput` method on that attribute. 
- dssatUtils: Contains some functions and classes to read, parse and write Python Files. It contains the class `CropParser`. That class allows to read the crop files by passing the crop file path as a parameter. The parameters can be modified by using the `set_parameter` or `set_parameters` methods.
- MCMC: Contains the `MCMC` class. That class allows the user to perform a Bayesian calibration of the model by especifying the prior distributions of the parameters. It also contains the `setup_paralell_env` function. That function sets the environment for parallel simulation by creating new directories with the DSSAT Executable and the required files to run a simulation.

All the classes, functions and methods include their docstring, which can be consulted by using the `help` function.  If you are not an experienced Python progammer: the `help` function allows you to see the information of any Class or Function, e.g., if you want to know how to run the model you just have to type `help(DSSATClass.runDSSAT)` where `DSSATClass` is an already initialized `CSM_EXE` instance.