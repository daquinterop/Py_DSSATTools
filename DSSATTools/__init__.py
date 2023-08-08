'''
DSSATTools library allows the user to create low-code scripts to run simulations
using the DSSAT modeling framework. The library structure allows to executes DSSAT
based on four input classes: `Crop`, `SoilProfile`, `Weather` and `Management`.
The simulation environment is managed by the `DSSAT` Class. There are three stages
for the simulation to be performed: 

1. Initialize a `DSSAT` instance. 
2. setup the simulation environment by using the `DSSAT.setup` method. When that 
method is called a new directory is created in the provided location (a tmp 
directory is default) and all the files that are necessary to run the model are 
copied in that folder.
3. run the simulation using the `DSSAT.run` method. That method needs three 
parameters to be pased, each one indicating the crop, soil, weather, and management.
This step can be performed as many times as one wants.
4. close the environment using `DSSAT.close`. This removes the directory and the
files created during the environment setup.

The next simple example illustrates how to run a simulation using the five 
aforementioned classes:

    >>> crop = Crop('maize')
    >>> weather = Weather(
            df, 
            {"tn": "TMIN", "rad": "SRAD", "prec": "RAIN", "rh": "RHUM", "TMAX": "TMAX"},
            4.54, -75.1, 1800
        )
    >>> soil = SoilProfile(default_class='SIL')
    >>> man = Management(planting_date=datetime(12, 3, 2020))
    >>> dssat = DSSAT()
    >>> dssat.setup()
    >>> dssat.run(soil, wth, crop, man)

The parameters for ecach class are described later. It is very important to note
that this library will allow the user to run one treatment at a time. If the user
is familiar with DSSAT, they must know that DSSAT allows to define multiple
treatments in the same experimental file.

All of the parameters and attributes of the four basic clases have the same name
you find in the DSSAT files (Take a look at the .CDE files in 
https://github.com/DSSAT/dssat-csm-os/tree/develop/Data). DSSAT includes several
parameters, and some users are not familiar with the model's github repository.

Up to date next crops and models are included:

==================   =====================
Crop                 Model
==================   =====================
Maize                CERES               
Millet               CERES               
Rice                 CERES               
Sugarbeet            CERES               
Sorghum              CERES               
Sweetcorn            CERES               
Alfalfa              FORAGE-Alfalfa      
Bermudagrass         FORAGE-Bermudagrass 
Soybean              CROPGRO             
Canola               CROPGRO             
Sunflower            CROPGRO             
Potato               SUBSTOR
Tomato               CROPGRO
Cabbage              CROPGRO
Potato               SUBSTOR             
Sugarcane            CANEGRO             
==================   =====================
'''
VERSION = '048'

from DSSATTools.crop import Crop
from DSSATTools.soil import SoilProfile, SoilLayer
from DSSATTools.weather import Weather
from DSSATTools.management import Management
from DSSATTools.run import DSSAT
from DSSATTools.base.sections import TabularSubsection

__all__ = [
    'Crop', 'SoilProfile', 'SoilLayer', 'Weather',
    'Management', 'DSSAT', 'TabularSubsection'
    ] 