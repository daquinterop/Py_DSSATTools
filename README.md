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
You can install the library using Python pip. **The library has only been tested for a Linux environment. It is not guaranteed that it will work in Windows.** If you have a Windows machine I recommend you to use WSL, or Google Colab.
```
pip install DSSATTools
```
## Documentation
The documentation is found here: https://py-dssattools.readthedocs.io/en/latest/. However, this readme and the Example Notebooks contain all the information you need to use the library.
## Example Notebooks
You'll find example notebooks in this repo:[https://github.com/daquinterop/DSSATTools_notebooks](https://github.com/daquinterop/DSSATTools_notebooks). I'll keep uploading examples as some new feature is introduced.
## Module contents

DSSATTools library allows the user to create low-code scripts to run simulations using the DSSAT modeling framework. DSSATTools version 3 includes significant changes when compared to previous versions. The newer is more intuitive for the users familiar with the model, the DSSAT GUI, and the DSSAT file creation tools. Therefore, if you are new to DSSAT I highly recommend you to familiarize yourself with the model, the GUI, and the file creation Tools before jumping into using this library.

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

### DSSATTools.filex
This module implement the sections of the DSSAT FileX as python objects. All sections are implemented, excepting the enviromental modifications section. Environmental modifications can be easily implemented by modifying the Weather component of each experiment. One section object represents a single factor level in the experiment.

Each section is defined using the same parameter names (lowercase) of the DSSAT FileX. For example, planting date is defined as follow:  
```python
>>> planting = Planting(
>>>     pdate=date(1980, 6, 17), ppop=18, ppoe=18,
>>>     plme='S', plds='R', plrs=45, plrd=0, pldp=5
>>> )
```
Sections that include a schedule or soil profile (i.e. Initial conditions), are defined as a list of individual events or soil layers. For example, a fertilizer section with two fertilizer events is defined as follows:
```python
>>> fertilizer = Fertilizer(table=[
>>>     FertilizerEvent(
>>>         fdate=date(1980, 7, 4), fmcd='FE005', fdep=5,
>>>         famn=80, facd='AP002'
>>>     ),
>>>     FertilizerEvent(
>>>         fdate=date(1980, 8, 7), fmcd='FE005', fdep=5,
>>>         famn=80, facd='AP002'
>>>     )
>>> ])
```
Other sections based on events are irrigation, residue, chemical, and tillage.

Note that the Fertilizer object is initialized by passing a list of FertilizerEvent objects in the 'table' parameter. The table parameter also accepts DataFrames, only if the column names of that DataFrame match the parameters for the individual event or layer object. Next is an example of this for the initial conditions section:
```python
>>> initial_conditions = InitialConditions(
>>>    pcr='SG', icdat=date(1980, 6, 1), icrt=500, icnd=0,
>>>    icrn=1, icre=1, icres=1300, icren=.5, icrep=0, icrip=100, icrid=10,
>>>    table=pd.DataFrame([
>>>        (10, .06, 2.5, 1.8),
>>>        (22, .06, 2.5, 1.8),
>>>        (52, .195, 3., 4.5),
>>>        (82, .21, 3.5, 5.0),
>>>        (112, 0.2, 2., 2.0),
>>>        (142, 0.2, 1., 0.7),
>>>        (172, 0.2, 1., 0.6),
>>>    ], columns=['icbl', 'sh2o', 'snh4', 'sno3'])
>>> )
```
Note that InitialConditions have more parameters besides the table parameter. The column names of the passed DataFrame are the same as the parameters for the InitialConditionsLayer class. The soil analysis section is the other section based on soil layers.

The field and cultivar sections are the only sections that need other DSSATTools objects as input parameters. In this section, the 'wsta' must be a WeatherStation object, and the 'id_soil' must be a SoilProfile object.
```python
>>> field = Field(
>>>    id_field='ITHY0001', wsta=weather_station, flob=0, fldt='DR000', 
>>>    fldd=0, flds=0, id_soil=soil
>>> )
```
'wsta' and 'id_soil' also receives weather station and soil profile ids as strings. However, this wouldn't make sense in the context of running DSSAT using this package.

The cultivar can be defined either using the Cultivar class, or by directly using the one of the classes defined in DSSATTools.crop. 
```python
>>> cultivar = Sorghum('IB0026')
>>> cultivar = Cultivar(cr='SG', ingeno='IB0026', cname='CSH-1')
```
These two definitions will yield the same result. However, when the cultivar is defined using the crop class it is posible to modify the cultivar and ecotype coefficients. More information is found at the DSSATTools.crop module documentation.
    
Finally, the simulations controls is created by using the SimulationsControls class. Each sub-section of the simulation controls sections is created using its own class. Next example shows how to create the simulations controls defining only the general options.
```python
>>> simulation_controls = SimulationControls(
>>>     general=SCGeneral(sdate=date(1980, 6, 1))
>>> )
```
The sections can be created from an existing FileX using the `read_filex` function. That function will return a dictionary, mapping each treatment to its correspondent section definitions. The next example reads an existing FileX, and then assigns the first treatment to the treatment variable. In this case, treatment is a dictionary mapping each section name to its python object. 
```python
>>> treatments = read_filex("Maize/BRPI0202.MZX")
>>> treatment = treatments[1]
```
The `create_filex` function returns the string of the FileX for for the passed sections defined as their python objects. 

### DSSATTools.weather
This module contains the classes that handle the weather definition. The WeatherStation class represents the DSSAT weather station. The weather station object can be created by reading the data from existing DSSAT wheater files:
```python
>>> weather = WeatherStation.from_files(["UAFD9001.WTH", "UAFD9101.WTH",])
```
Note that the input parameter is a list of files, as DSSAT can have multiple files for the same station. The list of files must correspond to the same station. The weather station can also be created using the data from a DataFrame:
```python
>>> weather_station = WeatherStation(
>>>     insi='UNCU', lat=4.34, long=-74.40, elev=1800, 
>>>     table=df_with_data
>>> )
```    
where the df_with_data contains the weather data and its column names match the DSSAT weather parameters' names. As with the event-based sections of the FileX, the table is a list of events (daily weather records). In this case the WeatherRecord class is the class representing each daily weather record.

## DSSATTools.crop
This module hosts the classes that represent each crop. Not all crops are implemented. Each crop class is child of a generic Crop class. A crop is instantiated by passing the cultivar code:
```python
>>> crop = Sorghum('IB0026')
```
This will create a dictionary-like object with keys as the cultivar parameters' names. Then, the cultivar parameters can be modified by assigning values:
```python
>>> crop['p1'] = 450.
>>> crop['g1'] = 0.1
```
The ecotype parameter is itself a dictionary-like object with the ecotype parameters' names as keys. Then, the ecotype parameters are modified in the same way as the cultivar parameters:
```python
>>> crop['eco#']['topt'] = 35.5
```
The `cultivar_list` class function will return a list of all the cultivars availble for a crop:
```python
>>> available_cultivars = Sorghum.cultivar_list()
```

## DSSATTools.soil
This module contains the classes and functions that handle the soil definition. The soil profile object is created using the SoilProfile class. One way of doing that is just loading soil profile from an existing DSSAT Soil file. For that, the `SoilProfile.from_file` class function is used:
```python
>>> soil = SoilProfile.from_file("IBMZ910214", "SOIL.SOL")
```
The soil profile can also be created from scratch using the SoilProfile and SoilLayer classes similar to the layer-based sections of the FileX:
```python
>>> soil = SoilProfile(
>>>     name='IBMZ910214', soil_series_name='Millhopper Fine Sand', 
>>>     site='Gainesville', country='USA', lat=29.6, long=-82.37, 
>>>     soil_data_source='Gainesville', soil_clasification='S',
>>>     scs_family='Loamy,silic,hyperth Arnic Paleudult', scom='', salb=0.18, 
>>>     slu1=2.0, sldr=0.65, slro=60.0, slnf=1.0, slpf=0.92, smhb='IB001',
>>>     smpx='IB001', smke='IB001',
>>>     table = [
>>>         SoilLayer(
>>>             slb=5.0, slmh='', slll=0.026, sdul=0.096, ssat=0.345, srgf=1.0, 
>>>             ssks=7.4, sbdm=1.66, sloc=0.67, slcl=1.7, slsi=0.9, slcf=0.0, 
>>>             slhw=7.0, scec=20.0
>>>         ),
>>>         SoilLayer(
>>>             slb=15.0, slmh='', slll=0.025, sdul=0.105, ssat=0.345, srgf=1.0, 
>>>             ssks=7.4, sbdm=1.66, sloc=0.67, slcl=1.7, slsi=0.9, slcf=0.0, 
>>>             slhw=7.0
>>>         ),
>>>         SoilLayer(
>>>             slb=30.0, slmh='', slll=0.075, sdul=0.12, ssat=0.345, srgf=0.7, 
>>>             ssks=14.8, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
>>>             slhw=7.0
>>>         ),
>>>         SoilLayer(
>>>             slb=45.0, slmh='', slll=0.025, sdul=0.086, ssat=0.345, srgf=0.3, 
>>>             ssks=3.7, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
>>>             slhw=7.0
>>>         ),
>>>         SoilLayer(
>>>             slb=60.0, slmh='', slll=0.025, sdul=0.072, ssat=0.345, srgf=0.3, 
>>>             ssks=3.7, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
>>>             slhw=7.0
>>>         ),
>>>         SoilLayer(
>>>             slb=90.0, slmh='', slll=0.028, sdul=0.072, ssat=0.345, srgf=0.1, 
>>>             ssks=3.7, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
>>>             slhw=7.0
>>>         ),
>>>         SoilLayer(
>>>             slb=120.0, slmh='', slll=0.028, sdul=0.08, ssat=0.345, srgf=0.1, 
>>>             ssks=0.1, sbdm=1.66, sloc=0.18, slcl=7.7, slsi=3.1, slcf=0.0, 
>>>             slhw=7.0,
>>>         ),
>>>         SoilLayer(
>>>             slb=150.0, slmh='', slll=0.029, sdul=0.09, ssat=0.345, srgf=0.05, 
>>>             ssks=0.1, sbdm=1.66, sloc=0.15, slcl=7.7, slsi=3.1, slcf=0.0, 
>>>             slhw=7.0
>>>         ),
>>>         SoilLayer(
>>>             slb=180.0, slmh='', slll=0.029, sdul=0.09, ssat=0.345, srgf=0.05, 
>>>             ssks=0.1, sbdm=1.66, sloc=0.1, slcl=7.7, slsi=3.1, slcf=0.0, 
>>>             slhw=7.0
>>>         )
>>>     ]
>>> )
````

This module also contains some functions to estimate missing soil properties. The `estimate_from_texture` function estimates the soil hydro-dynamic properties based on soil texture. The `sloc_from_color` estimates the soil organic carbon based on the soil color.

## DSSATTools.run

This module hosts the DSSAT class. This class represents the simulation environment, so per each DSSAT instance there's a directory where all the necesary files to run the model are allocated. To run the model there are 2 basic steps:

1. Create a new DSSAT instance. When DSSAT is instantiated, a simulation environment is set. That enviroment is set at the path passed during the call:
   ```python
    >>> dssat = DSSAT("/tmp/dssat_test")
   ```
3. Run the model by calling the run_treatment() method. This method receives as parameters the FileX sections' objects:
   ```python
    >>> results = dssat.run_treatment(
    >>>     field=field, cultivar=crop, planting=planting,
    >>>     initial_conditions=initial_conditions, fertilizer=fertilizer,
    >>>     simulation_controls=simulation_controls
    >>> )
   ```
   This call returns a dictionary that contains the values of the standard output of the model: FLO, MAT, TOPWT, HARWT, RAIN, etc. After running, the DSSAT instance will have all the output files as strings in the output_files attribute, and the output timeseries tables in the output_tables attribute:
   ```python
    >>> overview = dssat.output_files['OVERVIEW'] # Gets the overview file as a str
    >>> plantgro = dssat.output_tables['PlantGro'] # Gets the plant growth table
   ```
5. You can close the simulation environment by calling the close() method.
   ```python
    >>> dssat.close()
   ```
