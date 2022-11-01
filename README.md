# DSSATTools package
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

DSSAT library is a collection of classes that allows the user to create low-code scripts to run simulations with DSSAT model. The library structure allows to execute DSSAT model based on four input classes: Crop, SoilProfile, WeatherStation and Management.

The simulation environment is represented by the DSSAT Class. There are three stages for the simulation to be excecuted: 1. Initialize a DSSAT instance; 2. setup the simulation environment by using the DSSAT.setup method; 3. run the simulation using the DSSAT.run method.

During the environment setup (DSSAT.setup) a directory is created and all the static files required to run DSSAT are copied in that directory. This directory will be removed when the DSSAT.close method is called. After the environment has been set up, the DSSAT.run method can be called as many times as you want.

All of the parameters and attributes of the four basic clases have the same name you find in the DSSAT files (Take a look at the .CDE files in [https://github.com/DSSAT/dssat-csm-os/tree/develop/Data](https://github.com/DSSAT/dssat-csm-os/tree/develop/Data)).

**At the moment Only the next crops and models are implemented:**
| Crop         | Model               |
|--------------|---------------------|
| Maize        | CERES               |
| Millet       | CERES               |
| Rice         | CERES               |
| Sugarbeet    | CERES               |
| Sorghum      | CERES               |
| Sweetcorn    | CERES               |
| Alfalfa      | FORAGE-Alfalfa      |
| Bermudagrass | FORAGE-Bermudagrass |
| Soybean      | CROPGRO             |
| Canola       | CROPGRO             |
| Sunflower    | CROPGRO             |
| Tomato       | CROPGRO             |
| Cabbage      | CROPGRO             |
| Potato       | SUBSTOR             |

More crops and models will be added later.

If you're interested in contributing to this project, don't hesitate in sending me an email (daquinterop@gmail.com). Of course, if you want to contribute then I'll have to create a Developer's guide to the project.

All the Classes can be imported as:
```python
from DSSATTools import (
    Crop, SoilProfile, WeatherData, WeatherStation,
    Management, DSSAT
)
```
or 
```python
from DSSATTools import *
```
## DSSATTools.crop module

Basic crop class. It initializes a crop instances based on the crop name and
crop file if provided.

Crop class is the only needed class to initialize a Crop instance. You need
to specify the crop name (Those can be checked at DSSATTools.crop.CROPS_MODULES
object), and you can also specify a .SPE file to initialize the instance. If no
.SPE file is passed as argument, then default .SPE, .ECO and .CUL are used.

Please, take into account that if you initialize the instance with a custom
Species file the three files (.SPE, .ECO, .CUL) must be in the same directory 
as the passed Species file.

The only method implemented is set_parameter, that of course is used to set
the value of any crop parameter. Crop class inherits from the BaseCrop class
of the specified crop. BaseCrop is composed by sections, each of the included
in the Species file, and one section for Cultivar and Ecotype respectively.

The usage of the Crop class is explaied by this example. In here we initialize
a Crop instance, modify a parameter and write the cropfile (All of them).

```python
>>> crop = Crop('maize')
>>> crop.set_parameter(
        par_name = 'TBASE',
        par_value = 30.,
        row_loc = 'IB0002'
    )
>>> crop.write('crop_test')
```


### _class_ DSSATTools.crop.Crop(crop_name: str = 'Maize', spe_file: Optional[str] = None)
Initializes a crop instance based on the default DSSAT Crop files, or 
on a custom crop file provided as a cultivar.

##### Arguments
```
crop: str
    Crop name, available at the moment:  Maize, Millet, Sugarbeet, Rice, Sorghum, Sweetcorn, Alfalfa and Bermudagrass

spe_file: str
    Optional. Path to the species file to initialize the instance.

```
#### set_parameter(par_name: str, par_value, row_loc=0)
Set the value of one parameter in the Crop class.
##### Arguments
```
par_name: str
    name of the parameter. Parameter’s names are in the Crop.parameters 
    attribute.

par_value: str, int, float
    Value of the parameter to set.

row_loc: int, str
    id for the element to modify. This applies to parameters defined in 
    cols, such as cultivar or ecotype parameters. For example:

    @ECO#  ECONAME………  TBASE  TOPT ROPT   P20  
    IB0001 GENERIC MIDWEST1    8.0 34.0  34.0  12.5 
    IB0002 GENERIC MIDWEST2    8.0 34.0  34.0  12.5

    for this set of parameters (ecotype), the column ECO# is the id to
    be passed as row_loc argument.
```

## DSSATTools.management module

Management class includes all the information related to management. There are
multiple arguments to initialize a Management instance, however, the only 
mandatory arguments are cultivar (cultivar id, of course it has to be included
in the cultivars list of the Crop object you’ll be passing to DSSAT.run) and
planting_date. Simulation start is calculated as the day before the planting 
date, emergence_date is assumed to 5 days after planting, and the initial soil
water content is assumed to be 50% of the total available water 
(PWP + 0.5(FC-PWP))

Management class has one attribute per management section. Up to date not all
of the sections have been implemented and the next sections are available: 
fields, cultivars, initial conditions, planting details, irrigation, 
fertilizers, harvest details, simulation controls, automatic management. All of
the sections have dict object as base, so you can modify the parameters by
just reassigning the value as you would do it on a dict. Some of the sections
are defined as tables, so you can modify the values of those tabular sections
the same as you would modify a pandas.Dataframe.

In the next example a Management object is created, and two of its sections
are modified.

```python
>>> man = Management(
        cultivar='IB0001',
        planting_date=datetime(2020, 1, 1),
    )
>>> man.harvest_details['table'].loc[0, ['HDATE', 'HPC']] = \
        [datetime(2020, 7, 1).strftime('%y%j'), 100]
>>> man.simulation_controls['IRRIG'] = 'A'
```

### _class_ DSSATTools.management.Management(cultivar: str, planting_date: datetime, sim_start: Optional[datetime] = None, emergence_date: Optional[datetime] = None, initial_swc: float = 0.5, irrigation='R', fertilization='R', harvest='M')
Initializes a management instance.

##### Arguments
```
cultivar: str
    Code of the cultivar. That code must match one of the codes in the
    Crop instance used when runing the model.

planting_date: datetime
    Planting date.

sim_start: datetime
    Date for start of the simulation. If None, it’ll be calculated as
    the previous day to the planting date.

emergence_date: datetime
    Emergence date. If None, I’ll be calculated as 5 days after 
    planting.

initial_swc: int
    Fraction of the total available water (FC - PWP) at the start of the 
    simulation. .5(50%) is the default value.

irrigation: str
    Default ‘R’. Irrigation management option, options available are:

        A        Automatic when required
        N        Not irrigated
        F        Fixed amount automatic
        R        On reported dates
        D        Days after planting
        P        As reported through last day, then automatic to re-fill (A)
        W        As reported through last day, then automatic with fixed amount (F)

harvest: str
    Default ‘M’. Harvest management options. available options are:
        A        Automatic      
        M        At maturity
        R        On reported date(s)
        D        Days after planting

fertilization: str
    Default ‘R’. Fertilization management options. available options are:
        N        Not fertilized
        R        On reported dates
        D        Days after planting
```

## DSSATTools.run module

This module hosts the DSSAT class. That class is the simulation environment, so per each
Dscsm instance there’s a directory where all the necesary files to run the model
are allocated. To run the model there are 3 basic steps:

> 
> 1. Create a new Dscsm instance.


> 2. Initialize the environment by running the setup() method.


> 3. Run the model by running the run() method.

You can close the simulation environment by running the close() method.

The model outputs are storage in the outputs attribute. Up to date the only
model output parsed into outputs is ‘PlantGro’.

In the next example all the 4 required objects to run the DSSAT model are
created, an a simulation is run.

```python
>>> # Create random weather data
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
>>> # Create a WeatherData instance
>>> WTH_DATA = WeatherData(
    df,
    variables={
        'tn': 'TMIN', 'TMAX': 'TMAX',
        'prec': 'RAIN', 'rad': 'SRAD',
        'rh': 'RHUM'
    }
)
>>> # Create a WheaterStation instance
>>> wth = WeatherStation(
    WTH_DATA, 
    {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
)
>>> # Initialize soil, crop and management instances.
>>> soil = SoilProfile(default_class='SIL')
>>> crop = Crop('maize')
>>> man = Management(
    cultivar='IB0001',
    planting_date=DATES[10],
)
>>> man.harvest_details['table'].loc[0, ['HDATE', 'HPC']] =         [DATES[190].strftime('%y%j'), 100]
>>> # Initialize Dscsm instance and run.
>>> dssat = Dscsm()
>>> dssat.setup(cwd='/tmp/dssattest')
>>> dssat.run(
    soil=soil, weather=wth, crop=crop, management=man,
)
>>> # Get output
>>> PlantGro = dssat.outputs['PlantGro']
>>> dssat.close() # Terminate the simulation environment
```


### _class_ DSSATTools.run.DSSAT()

Class that represents the simulation environment. When initializing and 
seting up the environment, a new folder is created (usually in the tmp 
folder), and all of the necesary files to run the model are copied into it.

#### close()
Removes the simulation environment (tmp folder and files).


#### run(soil: SoilProfile, weather: WeatherStation, crop: Crop, management: Management)
Start the simulation and runs until the end or failure.
##### Arguments
```
soil: DSSATTools.soil.Soil
    SoilProfile instance

weather: DSSATTools.weather.WeatherStation
    WeatherStation instance

crop: DSSATTools.crop.Crop
    Crop instance

managment: DSSATTools.management.Management
    Management instance
```

#### setup(cwd=None)
Setup a simulation environment.
Creates a tmp folder to run the simulations and move all the required
files to run the model. Some rguments are optional, if those aren’t provided,
then standard files location will be used.
##### Arguments
```
cwd: str
    Working directory. All the model files would be moved to that directory.
    If None, then a tmp directory will be created.
```

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


### _class_ DSSATTools.soil.SoilLayer(base_depth: int, pars: dict)

Initialize a soil layer instance.
##### Arguments
```
base_depth: int
    Depth to the bottom of that layer (cm)

pars: dict
    Dict including the parameter values to initialize the instance. Layer
    parameters include: 
    ‘SLMH’,  ‘SLLL’,  ‘SDUL’,  ‘SSAT’,  ‘SRGF’,  ‘SSKS’,  ‘SBDM’,  ‘SLOC’,
    ‘SLCL’,  ‘SLSI’,  ‘SLCF’,  ‘SLNI’,  ‘SLHW’,  ‘SLHB’,  ‘SCEC’,  ‘SADC’
    ‘SLPX’,  ‘SLPT’,  ‘SLPO’, ‘CACO3’,  ‘SLAL’,  ‘SLFE’,  ‘SLMN’,  ‘SLBS’,
    ‘SLPA’,  ‘SLPB’,  ‘SLKE’,  ‘SLMG’,  ‘SLNA’,  ‘SLSU’,  ‘SLEC’,  ‘SLCA’
    Only mandatory parameters are ‘SLCL’ and ‘SLSI’. The rest of the basic
    parameters can be calculated from the texture.

    SCOM is optional, and it can be passed as an string referencing the color,
    or a tupple with CIELAB coordinates (L, a, b). The string can be one of
    these:

    > BLK: Black (10YR 2/1)
    > YBR: Yellowish Brown (7.5YR 5/6)
    > RBR: Redish Brown (10R 4/8)
    > DBR: Dark Brown (2.5YR 3/4) 
    > GRE: Grey (10YR 6/1)
    > YLW: Yellow (10YR 7/8)

```

### _class_ DSSATTools.soil.SoilProfile(file: Optional[str] = None, profile: Optional[str] = None, default_class: Optional[str] = None, pars: dict = {})

Soil Profile class. It can be initialized from an existing file. It also can 
be initialized from scratch.  If a file is provided, then the soil is 
initialized as the soil profile with the matching profile id in the file.
##### Arguments
```
file: str
    Optional. Path to the soil file.

profile: str
    Optional. Must be passed if file argument is passed. It’s the 
    id of the profile within the file.

pars: dict
    Dict with the non-layer soil parameters.

default_class: str
    Optional. It’s a string defining a DSSAT default soil class. If not 
    None, then the SoilClass instance is initialized with the paremeters 
    of the specified default_class.
    default_class must match any of the next codes:
    > Sand            |  S 
    > Loamy Sand      |  LS  
    > Sandy Loam      |  SL 
    > Loam            |  L 
    > Silty Loam      |  SIL 
    > Silt            |  SI 
    > Sandy Clay Loam |  SCL 
    > Clay Loam       |  CL 
    > Silty Clay Loam |  SICL 
    > Sandy Clay      |  SC 
    > Silty Clay      |  SIC 
    > Clay            |  C

```

#### add_layer(layer: SoilLayer)
Add a new layer to the Soil.
##### Arguments
```
layer: DSSATTools.soil.SoilLayer
    Soil Layer object
```

#### drop_layer(layer: int)
Drop the layer at the specified depth


#### set_parameter(parameter, value)
Set the value of a soil parameter.
##### Arguments
```
parameter: str
    Parameter name. You can use the DSSATTools.soil.list_parameters 
    function
    to have a list of the parameters and their description.

value: int, float, str
    Value for that parameter
```

#### write(filename: str = 'SOIL.SOL')
It’s called by the DSSATTools.run.Dscsm.run() method to write the file.
##### Arguments
```
filename: str
    Path to the file to write
```

### DSSATTools.soil.list_layer_parameters()
Print a list of the soil parameters


### DSSATTools.soil.list_profile_parameters()
Print a list of the soil parameters


## DSSATTools.weather module

This module includes two basic classes to create a weather station. The 
WeatherStation class is the one that storages all the station info and the 
weather data. The WeatherData class inherits all the methods of a 
pandas.DataFrame, and it’s the one that includes the weather data.

In the next example we’ll create synthetic data and we’ll create a
WeatherStation object.

```python
>>> DATES = pd.date_range('2000-01-01', '2010-12-31')
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
>>> # Create a WeatherData instance
>>> WTH_DATA = WeatherData(
        df,
        variables={
            'tn': 'TMIN', 'TMAX': 'TMAX',
            'prec': 'RAIN', 'rad': 'SRAD',
            'rh': 'RHUM'
        }
    )
>>> Create a WheaterStation instance
>>> wth = WeatherStation(
        WTH_DATA, 
        {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
    )
>>> wth.data.head() # To check the data first 5 records
```


### _class_ DSSATTools.weather.WeatherData(data: DataFrame, variables: dict = {})

WeatherData class.
Creates a WeatherData instance. That instance is the one that contains
the records for the Weather Station.
##### Arguments
```
data: pd.Dataframe
    A DataFrame containg the the weather data.

variables: dict
    A dict to map the columns of the dataframe, to the DSSAT Weather 
    variables. Use list_weather_parameters function to have a detailed
    description of the DSSAT weather variables.
```

### _class_ DSSATTools.weather.WeatherStation(wthdata: WeatherData, pars: dict, description='Weather Station')

WeatherStation Class.
Initialize a Weather station instance.

##### Arguments
```
pars: dict
    dict with the Weather station parameters. list_station_parameters
    provides a list with the parameters and their description. Only LAT,
    LON and ELEV parameters are mandatory.

description: str
    An string with the description of the weather station
```

### DSSATTools.weather.list_station_parameters()
Print a list of the weather station parameters


### DSSATTools.weather.list_weather_parameters()
Print a list of the weather data parameters
