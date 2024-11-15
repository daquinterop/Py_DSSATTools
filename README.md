# DSSATTools package
## Installation:
You can install the library using Python pip.
```
pip install DSSATTools
```
## v2.1 Updates
For the latest version the next changes were implemented:
- The library simultes only one treatment. Therefore, only one option for cultivars, irrigation, fertilizer, field, etc. can be defined. 
- Every set of defined crop or management parameters is a section. Each section is an attribute of the `Crop` or `Management` class. Sections won't be created by the user. The user can only modify the value of the parameters of the section, they can't create or add new parameters.
- The weather is now managed by a single `Weather` class.
- A `__repr__` method was implemented for the four basic classes (`Crop`, `Management`, `Weather` and `SoilProfile`), and the `Section` class. 
- The cultivar is selected when initializing the crop instance. Thus, the crop instance contains parameters only for that cultivar.

## Documentation
[https://py-dssattools.readthedocs.io/en/latest/index.html](https://py-dssattools.readthedocs.io/en/latest/index.html)
## Example Notebooks
You'll find example notebooks in this repo:[https://github.com/daquinterop/DSSATTools_notebooks](https://github.com/daquinterop/DSSATTools_notebooks). I'll keep uploading examples as some new feature is introduced.
## Module contents

DSSATTools library allows the user to create low-code scripts to run simulations using the DSSAT modeling framework. The library structure allows to executes DSSAT based on four input classes: `Crop`, `SoilProfile`, `Weather` and `Management`.The simulation environment is managed by the `DSSAT` Class. There are three stages for the simulation to be performed: 

1. Initialize a `DSSAT` instance. 
2. setup the simulation environment by using the `DSSAT.setup` method. When that method is called a new directory is created in the provided location (a tmp directory is default) and all the files that are necessary to run the model are copied in that folder.
3. run the simulation using the `DSSAT.run` method. That method needs three parameters to be pased, each one indicating the crop, soil, weather, and management. This step can be performed as many times as one wants.
4. close the environment using `DSSAT.close`. This removes the directory and the files created during the environment setup.

The next simple example illustrates how to run a simulation using the five aforementioned classes:

```python
>>> crop = Crop('maize')
>>> weather = Weather(
        df, # Weather data with a datetime index
        {"tn": "TMIN", "rad": "SRAD", "prec": "RAIN", "rh": "RHUM", "TMAX": "TMAX"},
        4.54, -75.1, 1800
    )
>>> soil = SoilProfile(default_class='SIL')
>>> man = Management(planting_date=datetime(12, 3, 2020))
>>> dssat = DSSAT()
>>> dssat.setup()
>>> dssat.run(soil, wth, crop, man)
>>> growth = dssat.output["PlantGro"] 
>>> dssat.close() # Terminate the simulation environment
```

The parameters for ecach class are described later. It is very important to note that this library will allow the user to run one treatment at a time. If the user is familiar with DSSAT, they must know that DSSAT allows to define multiple treatments in the same experimental file.

All of the parameters and attributes of the four basic clases have the same name you find in the DSSAT files (Take a look at the .CDE files in 
https://github.com/DSSAT/dssat-csm-os/tree/develop/Data).

**At the moment Only the next crops and models are implemented:**
| Crop         | Model               |
|--------------|---------------------|
| Maize*       | CERES               |
| Millet       | CERES               |
| Rice         | CERES               |
| Sugarbeet    | CERES               |
| Sorghum*     | CERES               |
| Sweetcorn    | CERES               |
| Wheat*       | CERES               |
| Alfalfa      | FORAGE-Alfalfa      |
| Bermudagrass | FORAGE-Bermudagrass |
| Soybean*     | CROPGRO             |
| Canola       | CROPGRO             |
| Sunflower    | CROPGRO             |
| Tomato*      | CROPGRO             |
| Cabbage      | CROPGRO             |
| Potato       | SUBSTOR             |
| Sugarcane    | CANEGRO             |

(*) Only a those crops have been validated. During the validation one DSSAT experiment was run using DSSATTools and the results were compared with those obtained using DSSAT desktop. I'll be validating more crops as long as a I have time to do it.

If you're interested in contributing to this project, don't hesitate in sending me an email (daquinterop@gmail.com). 

All the Classes can be imported as:
```python
from DSSATTools import (Crop, SoilProfile, Weather, Management, DSSAT)
```
or 
```python
from DSSATTools import *
```
## DSSATTools.crop module

`Crop` is the only implemented class in the crop module. DSSAT's crop parameters
are grouped in three different files: ecotype (.ECO), cultivar (.CUL) and 
species (.SPE). Not all crops have the ecotype file though. DSSATTools uses the 
default .SPE, .ECO, and .CUL files. The ecotype and cultivar parameters are
defined as attributes of the `Crop` instance. Each parameter is accessible and can
be modified using the key, value syntax, e.g.
`crop.cultivar["PARAMETER"] = VALUE`. 

It is well known that for a species there can be multiple cultivars. Therefore, 
when initializing a `Crop` instance, two parameters must be provided: the crop 
name (species), and the cultivar code. The cultivar codes are defined in the .CUL
file. If an unknown cultivar is passed, then the last cultivar in the .CUL file is
used and a warning is shown. To get a list of the available cultivars for a crop
the user can use the `DSSATTools.crop.available_cultivars` function passing the 
crop name as only argument.

If the user wants to modify the cultivar or ecotype parameters they can be through
the `Crop.cultivar` and `Crop.ecotype` attributes respectively. In these two
attributes both the cultivar and ecotype parameters are defined as a `Section`
class (DSSATTools.sections.Section). `Section` class simply maps the parameter's
name to a value; it can be treated as a python dictionary. Each of the different
sections of the `Management` class are defined in the same way.

The next example shows how to define the crop and modify one cultivar and ecotype
parameter.
```python
>>> crop = Crop('maize')
>>> crop.cultivar["P1"] = 240
>>> crop.ecotype["P20"] = 13.
```

## DSSATTools.management module

This module hosts the `Management` class, which includes all the information 
related to management. There are multiple arguments to initialize a `Management`
instance, however, the only  mandatory argument is planting_date. If not provided, 
simulation start is calculated as the day before the planting date, emergence date
is assumed to 5 days after planting, and the initial soil water content is assumed
to be 50% of the total available water (PWP + 0.5(FC-PWP)).

`Management` class has one attribute per management section. Up to date not all
of the sections have been implemented and the next sections are available for the
user to modify: field, initial conditions, planting details, irrigation, fertilizers, 
harvest details, simulation controls, automatic management. All the sections are a
`DSSATTools.section.Sections` object. The options that are not defined when
initializing the `Management` instance can be defined by modifying the value of
the parameters in each of the sections. An example will be set. If the user is
not familiar to the different sections of the DSSAT experimental file then
reviewing the DSSAT documentation is suggested.

`DSSATTools.section.TabularSubsection` class is intended to represent tabular
information like irrigation schedules, fertilizer applications, or initial
condition through the different soil's layers. The `TabularSubsection` can be
initialized the same way a pandas.DataFrame. It's important to mention that the
columns must have the same names as the DSSAT variables the are representing
(See example).

In the next example a `Management` object is created, defining the irrigation
method option as non-irrigated; then the location of the field is defined in the
field section. 

```python
>>> man = Management( # Initialize instance
        planting_date=datetime(2020, 1, 1),
        irrigation="N",
    )
>>> # Modify the location of the field
>>> man.field["...........XCRD"] = 35.32
>>> man.field["...........YCRD"] = -3.21
```
Even though the irrigation method was defined when the object was created, it can
still be modified:

```python
>>> man.simulation_controls["IRRIG"] = "R"
>>> # Create a irrigation schedule as a pandas.DataFrame
>>> schedule = pd.DataFrame([
        (datetime(2000,1,15), 80),
        (datetime(2000,1,30), 60),
        (datetime(2000,2,15), 40),
        (datetime(2000,3,1),  20)
    ], columns = ['date', 'IRVAL'])
>>> schedule['IDATE'] = schedule.date.dt.strftime('%y%j')
>>> schedule['IROP'] = 'IR001' # irrigation operation code
>>> man.irrigation['table'] = TabularSubsection(
        schedule[['IDATE', 'IROP', 'IRVAL']]
    )
```

## DSSATTools.run module

This module hosts the DSSAT class. That class is the simulation environment, 
so per each DSSAT instance there's a directory where all the necesary files to 
run the model are allocated. To run the model there are 3 basic steps:

1. Create a new Dscsm instance.
2. Initialize the environment by calling the setup() method.
3. Run the model by calling the run() method.
You can close the simulation environment by calling the close() method.

The model outputs are storage in the `output` attribute. Up to date the next output
are available: PlantGro, Weather, SoilWat, SoilOrg.

## DSSATTools.soil module

soil module includes the basic soil class SoilProfile. This class contains
all the soil information necessary to run the DSSAT model. Each of the layers
of the soil profile is a SoilLayer instance. After a SoilProfile instance
is created, a new layer can added by calling the SoilProfile.add_layer method
passing a SoilLayer object as argument. You can also use the 
SoilProfile.drop_layer to drop the layer at the specified depth.

SoilLayer class represents each layer in the soil profile. The layer is 
initialized by passing the layer base depth and a dict with the parameteters as 
argument. Clay fraction (SLCL) and Silt fraction (SLSI) are the only mandatory
parameters when creating a layer, the rest of the parameters are estimated.

There are three basic ways of creating a SoilProfile object:

1. Specify a .SOL file and Soil id. Of course, the soil id must match one 
of the profiles in the .SOL file.

```python
>>> soilprofile = SoilProfile(
    file='SOIL.SOL',
    profile='IBBN910030'
)
```

2. Passing a string code of one the available default soils.

```python
>>> soilprofile = SoilProfile(
    default_class='SCL', # Silty Clay Loam
)
```

3. Pasing a dict with the profile parameters (different from the layer 
pars). DSSAT.soil.list_profile_parameters function prints a detailed list 
of the layer parameters. And empty dict can be pased as none of the 
parameters is mandatory.

```python
>>> soilprofile = SoilProfile(
    pars={
        'SALB': 0.25, # Albedo
        'SLU1': 6, # Stage 1 Evaporation (mm)
        'SLPF': 0.8 # Soil fertility factor
    }
)
>>> layers = [
    soil.SoilLayer(20, {'SLCL': 50, 'SLSI': 45}),
    soil.SoilLayer(50, {'SLCL': 30, 'SLSI': 30}),
    soil.SoilLayer(100, {'SLCL': 30, 'SLSI': 35}),
    soil.SoilLayer(180, {'SLCL': 20, 'SLSI': 30})
]
>>> for layer in layers: soilprofile.add_layer(layer)
```

That layer must be initialized with the texture information (‘SLCL’ and ‘SLSI’ 
parameters), or the hydraulic soil parameters (‘SLLL’, ‘SDUL’, ‘SSAT’, ‘SRGF’, 
‘SSKS’, ‘SBDM’, ‘SLOC’). If a soil hydraulic parameter is not defined, then it’s
estimated from soil texture using Pedo-transfer Functions. The previous
parameters are the mandatory ones, but all the available parameters can be 
includedin the pars dict.

If you want to save your soil profile in .SOL a file, you can use the 
SoilProfile.write method. The only argument of this method is the filename.

For both classes any of the parameters can be modified after the initialization
as each parameter is also an attribute of the instance.

```python
>>> soilprofile = SoilProfile(
    pars={
        'SALB': 0.25, # Albedo
        'SLU1': 6, # Stage 1 Evaporation (mm)
        'SLPF': 0.8 # Soil fertility factor
    }
>>> # Modify the albedo of the created instance
>>> soilprofile.SALB = 0.36
```

## DSSATTools.weather module

This module hosts the `Weather` class. It also contains the
`list_station_parameters` and `list_weather_variables` which return a list of the
parameters that define the weather station where the data was collected, and the
weather variables that can be included in the dataset. A `Weather` instance is
initialized by passing five mandatory parameters: a pandas dataframe including
the weather data, a dict mapping each dataframe column to one of the DSSAT
weather varaibles, latitude, longitude, and elevation.

The next example illustrates how to define a Weather instance from syntetic data:

```python
>>> DATES = pd.date_range('2000-01-01', '2010-12-31'); N=len(DATES)
>>> df = pd.DataFrame(
        {
        'tn': np.random.gamma(10, 1, N),
        'rad': np.random.gamma(10, 1.5, N),
        'prec': np.round(np.random.gamma(.4, 10, N), 1),
        'rh': 100 * np.random.beta(1.5, 1.15, N),
        },
        index=DATES,
    )
>>> df['TMAX'] = df.tn + np.random.gamma(5., .5, N)
>>> weather = Weather(
        df, 
        {"tn": "TMIN", "rad": "SRAD", "prec": "RAIN", 
        "rh": "RHUM", "TMAX": "TMAX"},
        4.54, -75.1, 1800
    )
```

The parameters of the weather station are defined as attributes of the `Weather`
class. Those parameters can be listed by calling the `list_station_parameters`.
In the next example the reference height for windspeed measurements is defined
for the weather instance created in the previous example:

```python
>>> weather.WNDHT = 2
```