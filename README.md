# DSSATTools package

## Submodules

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
Example
——-

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
Bases: `Gonorrea`, `CropBase`


#### \__init__(crop_name: str = 'Maize', spe_file: Optional[str] = None)
Initializes a crop instance based on the default DSSAT Crop files, or 
on a custom crop file provided as a cultivar.

crop: str

    Crop name, it must be one of these:


        * Maize


        * TODO: Implement more crops

spe_file: str

    Optional. Path to the cultivar file to initialize the instance.


#### set_parameter(par_name: str, par_value, row_loc=0, col_loc=0)
Set the value of one parameter in the Crop class.

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

col_loc: int, str

    same as row_loc, but for parameters defined in rows (array-like).
    For example:



    ```
    *
    ```

    TEMPERATURE EFFECTS
    !       TBASE TOP1  TOP2  TMAX

    > PRFTC  6.2  16.5  33.0  44.0     
    > RGFIL  5.5  16.0  27.0  35.0

    In this case, to define the PRFTC parameter, you should specify one 
    of the columns (TBASE, TOP1, etc.) through the col_loc argument.


### _class_ DSSATTools.crop.Gonorrea(spe_file)
Bases: `object`


#### \__init__(spe_file)
## DSSATTools.management module

Management file will be initialized with custom settings. There won’t be any


### _class_ DSSATTools.management.Management(cultivar: str, planting_date: datetime, sim_start: Optional[datetime] = None, emergence_date: Optional[datetime] = None, initial_swc: float = 0.5)
Bases: `object`

Management classs


#### \__init__(cultivar: str, planting_date: datetime, sim_start: Optional[datetime] = None, emergence_date: Optional[datetime] = None, initial_swc: float = 0.5)
Initializes a management instance.

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


#### write(filename='EXP', expname='DEFAULT')
## DSSATTools.run module

Hosts the Dscsm class. That class is the simulation environment, so per each
Dscsm instance there’s a directory where all the necesary files to run the model
are allocated. To run the model there are 3 basic steps:

> 
> 1. Create a new Dscsm instance.


> 2. Initialize the environment by running the setup() method.


> 3. Run the model by running the run() method.

You can close the simulation environment by running the close() method.

### Example

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


### _class_ DSSATTools.run.Dscsm()
Bases: `object`


#### \__init__()
No arguments, this initializes the class.


#### close()
Remove all the files in the run path.


#### run(soil: SoilProfile, weather: WeatherStation, crop: Crop, management: Management)
Start the simulation and runs until the end or failure.

soil: DSSATTools.soil.Soil

    SoilProfile instance

weather: DSSATTools.weather.WeatherStation

    WeatherStation instance

crop: DSSATTools.crop.Crop

    Crop instance

managment: DSSATTools.management.Management

    Management instance


#### setup(cwd=None)
Setup a simulation environment.
Creates a tmp folder to run the simulations and move all the required
files to run the model. Some rguments are optional, if those aren’t provided,
then standard files location will be used.

cwd: str

    Working directory. All the model files would be moved to that directory.
    If None, then a tmp directory will be created.

## DSSATTools.soil module

soil module includes the basic soil class SoilProfile. This class contains
all the soil information necessary to run the DSSAT model. Each of the layers
of the soil profile is a SoilLayer instance.

SoilLayer class represents each layer in the soil profile. The layer is 
initialized by passing the layer base depth and a dict with the parameteters as 
argument.

### Example

```python
>>> layer = SoilLayer(
        base_depth=100, # Soil base depth (cm)
        pars= # layer parameter's dict
        {
            'SLOC': 1.75, # Soil Organic Carbon %
            'SLCL': 50, # Clay %
            'SLSI': 45 # Silt %
        } 
    )
```

That layer must be initialized with the texture information (‘SLCL’ and ‘SLSI’ 
parameters), or the hydraulic soil parameters (‘SLLL’, ‘SDUL’, ‘SSAT’, ‘SRGF’, 
‘SSKS’, ‘SBDM’, ‘SLOC’). If a soil hydraulic parameter is not defined, then it’s
estimated from soil texture using Pedo-transfer Functions. The previous
parameters the mandatory ones, but all the available parameters can be included
in the pars dict. list_layer_parameters function prints all the available 
parameters and their description.

A SoilProfile instance can be passed to the Dcscm.run method. There are
three different ways of initializing a SoilProfile instance:

> 1. Specify a .SOL file and Soil id. Of course, the soil id must match one 
> of the profiles in the .SOL file.
> 2. Passing a string code of one the available default soils.
> 3. Pasing a dict with the profile parameters (different from the layer 
> pars). list_profile_parameters function prints a detailed list of the 
> layer parameters. And empty dict can be pased as none of the parameters is
> mandatory.

Initializing a SoilProfile instance with no parameters is also possible.
Profile layers can be added or droped using the add_layer and drop_layer. 
They also can be overwriten, but a warning will be raised.

### Example

```python
>>> # Initializing from file 
>>> soilprofile = SoilProfile(
    file='SOIL.SOL',
    profile='IBBN910030'
)
>>> # Initializing from default soil class 
>>> soilprofile = SoilProfile(
    default_class='SCL', # Silty Clay Loam
)
>>> # Initializing and adding layers 
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

If you want to save your soil profile in .SOL a file, you can use the 
SoilProfile.write method. The only argument of this method is the filename.

For both classes any of the parameters can be modified after the initialization
as each parameter is also an attribute of the instance.

### Example

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
Bases: `Series`

Class representing a soil layer.


#### \__init__(base_depth: int, pars: dict)
Initialize a soil layer instance.

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


### _class_ DSSATTools.soil.SoilProfile(file: Optional[str] = None, profile: Optional[str] = None, default_class: Optional[str] = None, pars: dict = {})
Bases: `object`

Soil Profile class. It can be initialized from an existing file.
It also can be initialized from scratch.


#### \__init__(file: Optional[str] = None, profile: Optional[str] = None, default_class: Optional[str] = None, pars: dict = {})
Initialize a SoilClass instance. If a file is provided, then the soil
is initilized as the soil with the matching id in the file.

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


#### add_layer(layer: SoilLayer)
Add a new layer to the Soil.

layer: DSSATTools.soil.SoilLayer

    Soil Layer object


#### drop_layer(layer: int)
Drop the layer at the specified depth


#### set_parameter(parameter, value)
Set the value of a soil parameter.

parameter: str

    Parameter name. You can use the DSSATTools.soil.list_parameters 
    function
    to have a list of the parameters and their description.

value: int, float, str

    Value for that parameter


#### write(filename: str = 'SOIL.SOL')
It’s called by the DSSATTools.run.Dscsm.run() method to write the file.

filename: str

    Path to the file to write


### DSSATTools.soil.color_to_oc(color=None, L=None, a=None, b=None)
Estimate Organic Carbon from Color as described in Vodyanidskii and Savichev
(2017).https://doi.org/10.1016/j.aasci.2017.05.023

Color definitions and their CIE-L\*a\*b\* equivalents were obtained from 
Munsell tables. Color argument’s possible values are:

> BLK: Black (10YR 2/1)
> YBR: Yellowish Brown (7.5YR 5/6)
> RBR: Redish Brown (10R 4/8)
> DBR: Dark Brown (2.5YR 3/4) 
> GRE: Grey (10YR 6/1)
> YLW: Yellow (10YR 7/8)

L, a and b values can be pased directly too.


### DSSATTools.soil.list_layer_parameters()
Print a list of the soil parameters


### DSSATTools.soil.list_profile_parameters()
Print a list of the soil parameters


### DSSATTools.soil.van_genuchten(theta_r, theta_s, alpha, n, h)
Van Genuchten function for soil water retention. Returns theta 
for a given h (kPa)

> theta_r, residual water content
> theta_s, saturated water content
> log10(alpha), van Genuchten ‘alpha’ parameter (1/cm)
> log10(n), van Genuchten ‘n’ parameter


### DSSATTools.soil.wrap_NA_types(inp)
## DSSATTools.weather module

weather module includes to basic classes to create a weather station. 
The WeatherStation class is the one that storages all the station info and 
and the weather data. The WeatherData class inherits all the methods of a 
pandas DataFrame, and it’s the one that includes of the weather data.

### Example

```python
>>> # Create some synthetic data
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
Bases: `DataFrame`

WeatherData class.


#### \__init__(data: DataFrame, variables: dict = {})
Creates a WeatherData instance. That instance is the one that contains
the records for the Weather Station.

data: pd.Dataframe

    A DataFrame containg the the weather data.

variables: dict

    A dict to map the columns of the dataframe, to the DSSAT Weather 
    variables. Use list_weather_parameters function to have a detailed
    description of the DSSAT weather variables.


### _class_ DSSATTools.weather.WeatherStation(wthdata: WeatherData, pars: dict, description='Weather Station')
Bases: `object`

WeatherStation Class.


#### \__init__(wthdata: WeatherData, pars: dict, description='Weather Station')
Initialize a Weather station instance.

pars: dict

    dict with the Weather station parameters. list_station_parameters
    provides a list with the parameters and their description. Only LAT,
    LON and ELEV parameters are mandatory.

description: str

    An string with the description of the weather station


#### write(folder: str = '')
Writes the weather files in the provided folder. The name is defined
by the dates and the Institute code (INSI).

> Arguments

folder: str

    Path to the folder the files will be saved.


### DSSATTools.weather.list_station_parameters()
Print a list of the weather station parameters


### DSSATTools.weather.list_weather_parameters()
Print a list of the weather data parameters

## Module contents
