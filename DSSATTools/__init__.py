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

3. run the simulation calling `DSSAT.run` method. That method needs four 
parameters to be pased. Each parameter indicates the crop, soil, weather, and management.
This step can be performed as many times as one wants. 

4. close the environment using `DSSAT.close`. This removes the directory and the
files created during the environment setup.

The next simple example illustrates how to run a simulation using the five 
aforementioned classes:

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

The parameters for ecach class are described in their doucmentation. It is very 
important to highlight that this library will allow the user to run only one treatment
at a time. If the users are familiar to DSSAT, they must know that DSSAT allows to
define multiple treatments in the same experimental file.

All of the parameters for the four basic clases have the same names you find in 
the DSSAT files (Take a look at the .CDE files in 
https://github.com/DSSAT/dssat-csm-os/tree/develop/Data).

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
Wheat                CERES         
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

from DSSATTools.crop import Crop, available_cultivars
from DSSATTools.soil import SoilProfile, SoilLayer
from DSSATTools.weather import Weather
from DSSATTools.management import Management
from DSSATTools.run import DSSAT
from DSSATTools.base.sections import TabularSubsection

__all__ = [
    'Crop', 'SoilProfile', 'SoilLayer', 'Weather', 'Management', 'DSSAT', 
    'TabularSubsection', "available_cultivars"
    ] 