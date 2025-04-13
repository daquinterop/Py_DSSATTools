# DSSATTools package
## v3.0 Updates
Significant changes have been implemented. **Those changes are not backward compatible.** The DSSATTools code for the previous versions are not compatible with the new version. If you have DSSATTools in your current workflows, I recommend you to update your code. If you can't change your code, then install the 2.1.6 version. 

The new version aims to be more intuitive for the users familiar with the model, the DSSAT GUI, and the DSSAT file creation tools. Therefore, **if you are new to DSSAT I highly recommend you to familiarize yourself with the model, the GUI, and the file creation Tools before jumping into using this library.** The changes in this new version are summarized next:

- a new `filex` module is introduced. This module host the classes that represent the different FileX sections. Then, the `management` module is removed.
- The `filex.read_filex` function is introduced. This function reads a FileX and returns all the treatments in that file as DSSATTools objects.
- Each crop now has its own class, which is a child of a generic `Crop` class.
- The `Weather` class is removed and replaced for the `WeatherStation` class.
- The `Weather` and `SoilProfile` classes now have the `from_files` and `from_file` method respectively. These methods allows to directly create the `Weather` or `SoilProfile` instances from a WTH or SOL file.
- The `DSSAT` class still represents the simulation environment. Now, it receives one parameter when intialized: the run_path parameter. This paremeter is the directory where the simulations will be run. The `DSSAT.run` method has been replaced with the `DSSAT.run_treatment` method. 
- Now all the FileX sections are implemented with exception of the Environmental Modifications section.
- When the model is run using the `DSSAT.run_treatment` method, all the output files are stored in the `DSSAT.output_files` attribute. The files are stored as a string.
- The `DSSAT.run_treatment` returns a dictionary with the standard output of the CSM.


## Installation:
You can install the library using Python pip.
```
pip install DSSATTools
```
## Documentation
[https://py-dssattools.readthedocs.io/en/latest/index.html](https://py-dssattools.readthedocs.io/en/latest/index.html)
## Example Notebooks
You'll find example notebooks in this repo:[https://github.com/daquinterop/DSSATTools_notebooks](https://github.com/daquinterop/DSSATTools_notebooks). I'll keep uploading examples as some new feature is introduced.
## Module contents

DSSATTools library allows the user to create low-code scripts to run simulations using the DSSAT modeling framework. DSSATTools version 2.2.0 includes significant changes when compared to previous versions. The newer is more intuitive for the users familiar with the model, the DSSAT GUI, and the DSSAT file creation tools. Therefore, if you are new to DSSAT I highly recommend you to familiarize yourself with the model, the GUI, and the file creation Tools before jumping into using this library.

DSSATTools implements an object-based approach to define DSSAT simulation input. This aims to mimic the process of creating the DSSAT input files (SOL, WTH, FileX) using the DSSAT GUI Tools. Then, the same way that XBuild has one menu for each FileX section (e.g. Cultivar, Soil Analysis, Planting Date, etc.), there is one DSSATTools class for each section of the FileX. Also, there is one class for the WTH file, and one class for the SOL file. 

The filex module contains all the classes that represent each of the FileX sections. All the FileX sections are implemented excepting enviromental modifications. The crop module contains the Crop classes, one per crop. Such classes represent the crop and their cultivar and ecotype parameters. The soil module contains the SoilProfile class, which represents a single soil profile. The weather module hosts the WeatherStation class, which represents the Weather Station file (WTH).

Here is one example on how the package is used to run a simple simulation:

```python
>>> from DSSATTools.crop import Sorghum
>>> from DSSATTools.weather import WeatherStation
>>> from DSSATTools.soil import SoilProfile
>>> from DSSATTools.filex import (
>>>     Planting, SimulationControls, Fertilizer, Field
>>> )
>>> cultivar = Sorghum('IB0026')
>>> weather_station = WeatherStation(
>>>     insi='UNCU', lat=4.34, long=-74.40, elev=1800, 
>>>     table=df_with_data
>>> )
>>> soil = SoilProfile.from_file('IBSG910085', 'SOIL.SOL')
>>> field = Field(
>>>     id_field='ITHY0001', wsta=weather_station, flob=0, 
>>>     fldd=0, flds=0, id_soil=soil, fldt='DR000'
>>> )
>>> planting = Planting(
>>>     pdate=date(1980, 6, 17), ppop=18, ppoe=18,
>>>     plme='S', plds='R', plrs=45, plrd=0, pldp=5
>>> )
>>> fertilizer = Fertilizer(table=[
>>>     FertilizerEvent(
>>>         fdate=date(1980, 7, 4), fmcd='FE005', fdep=5,
>>>         famn=80, facd='AP002'
>>>     )
>>> ])
>>> simulation_controls = SimulationControls(
>>>     general=SCGeneral(sdate=date(1980, 6, 17))
>>> )
>>> dssat = DSSAT()
>>> results = dssat.run_treatment(
>>>     field=field, cultivar=cultivar, planting=planting, 
>>>     fertilizer=fertilizer, simulation_controls=simulation_controls
>>> )
>>> dssat.close() # Terminate the simulation environment
```

The parameters for ecach class are described in their doucmentation. As now, the
`DSSAT.run_treatment` is the only function available to run the model. This 
function runs the CSM in the 'C' mode (one treatment at a time).

All of the parameters and attributes of the four basic clases have the same name you find in the DSSAT files (Take a look at the .CDE files in 
https://github.com/DSSAT/dssat-csm-os/tree/develop/Data).

**At the moment Only the next crops and models are implemented:**
| Crop         | Model               |
|--------------|---------------------|
| Maize        | CERES               |
| Millet       | CERES               |
| Rice         | CERES               |
| Sugarbeet    | CERES               |
| Sorghum      | CERES               |
| Sweetcorn    | CERES               |
| Wheat        | CERES               |
| Alfalfa      | FORAGE-Alfalfa      |
| Bermudagrass | FORAGE-Bermudagrass |
| Soybean      | CROPGRO             |
| Canola       | CROPGRO             |
| Sunflower    | CROPGRO             |
| Tomato       | CROPGRO             |
| Cabbage      | CROPGRO             |
| Potato       | SUBSTOR             |
| Sugarcane    | CANEGRO             |
| Bean (Dry)   | CROPGRO             |
| Cassava      | CSYCA               |

All crops have been validated by comparing the DSSATTools final harvest with that obtained using the DSSAT GUI.

If you're interested in contributing to this project, don't hesitate in sending me an email (daquinterop@gmail.com). 