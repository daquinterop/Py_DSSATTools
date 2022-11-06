'''
DSSAT library is a collection of classes that allows the user to create low-code scripts to run simulations with DSSAT model. The library structure allows to  execute DSSAT model based on four input classes: `Crop`, `SoilProfile`, `WeatherStation` and `Management`.

The simulation environment is represented by the `DSSAT` Class. There are three stages for the simulation to be excecuted: 
#. Initialize a `DSSAT` instance
#. setup the simulation environment by using the `DSSAT.setup` method
#. run the simulation using the `DSSAT.run` method.

During the environment setup (`DSSAT.setup`) a directory is created and all the static files required to run DSSAT are copied in that directory. This directory will be removed when the `DSSAT.close` method is called. After the environment has been set up, the `DSSAT.run` method can be called as many times as you want.

Input clases are defined by sections and tabular subsections within some sections. Each section is an attribute of the input instance and is defined as an independent `RowBasedSection` class. This class inherits from `dict`, so you can modify any parameter in the section the same way that you'd modify a `dict`'s item.

All of the parameters and attributes of the four basic clases have the same name you find in the DSSAT files (Take a look at the .CDE files in https://github.com/DSSAT/dssat-csm-os/tree/develop/Data).

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
==================   =====================

'''
VERSION = '048'

from DSSATTools.crop import Crop
from DSSATTools.soil import SoilProfile, SoilLayer
from DSSATTools.weather import WeatherStation, WeatherData
from DSSATTools.management import Management
from DSSATTools.run import DSSAT
from DSSATTools.base.sections import TabularSubsection

__all__ = [
    'Crop', 'SoilProfile', 'SoilLayer', 'WeatherStation', 'WeatherData',
    'Management', 'DSSAT', 'TabularSubsection'
    ] 