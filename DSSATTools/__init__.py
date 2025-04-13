'''
DSSATTools library allows the user to create low-code scripts to run simulations
using the DSSAT modeling framework. DSSATTools version 2.2.0 includes significant
changes when compared to previous versions. The newer is more intuitive for the 
users familiar with the model, the DSSAT GUI, and the DSSAT file creation tools.
Therefore, if you are new to DSSAT I highly recommend you to familiarize yourself
with the model, the GUI, and the file creation Tools before jumping into using 
this library.

DSSATTools implements an object-based approach to define DSSAT simulation input. 
This aims to mimic the process of creating the DSSAT input files (SOL, WTH, FileX)
using the DSSAT GUI Tools. Then, the same way that XBuild has one menu for each 
FileX section (e.g. Cultivar, Soil Analysis, Planting Date, etc.), there is one 
DSSATTools class for each section of the FileX. Also, there is one class for the 
WTH file, and one class for the SOL file. 

The filex module contains all the classes that represent each of the FileX sections.
The crop module contains the Crop classes, one per crop. Such classes represent
the crop and their cultivar and ecotype parameters. The soil module contains the
SoilProfile class, which represents a single soil profile. The weather module
hosts the WeatherStation class, which represents the Weather Station file (WTH).

Here is one example on how the package is used to run a simple simulation:

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
    >>>     general=SCGeneral(sdate=date(1980, 1, 1) + timedelta(164))
    >>> )
    >>> dssat = DSSAT()
    >>> results = dssat.run_treatment(
    >>>     field=field, cultivar=cultivar, planting=planting, 
    >>>     fertilizer=fertilizer, simulation_controls=simulation_controls
    >>> )
    >>> dssat.close() # Terminate the simulation environment

The parameters for ecach class are described in their doucmentation. As now, the
`DSSAT.run_treatment` is the only function available to run the model. This 
function runs the CSM in the 'C' mode (one treatment at a time).

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
Bean                 CROPGRO
Potato               SUBSTOR             
Sugarcane            CANEGRO
Cassava              CSYCA CIAT         
==================   =====================
'''
VERSION = '048'

from DSSATTools import crop
from DSSATTools.soil import SoilProfile, SoilLayer
from DSSATTools.weather import WeatherStation, WeatherRecord
from DSSATTools.run import DSSAT
from DSSATTools import filex

__all__ = [
    'crop', 'SoilProfile', 'WeatherStation', 'DSSAT',  'filex'
    ] 

import warnings
warnings.simplefilter('always', DeprecationWarning)
warnings.warn(
    'DSSATTools version 3.0.0 is a major upgrade and will not be backwards compatible with previous versions. If you are running code that was developed  using a previous DSSATTools version, then install DSSATTools version 2.1.6',  
    DeprecationWarning
)