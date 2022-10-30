'''
This module includes two basic classes to create a weather station. The `WeatherStation` class is the one that storages all the station info and the weather data. The `WeatherData` class inherits all the methods of a `pandas.DataFrame`, and it's the one that includes the weather data.

In the next example we'll create synthetic data and we'll create a `WeatherStation` object.

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
'''
import os
import pandas as pd
from pandas import DataFrame
from pandas import NA, isna
from DSSATTools.base.formater import weather_data, weather_data_header, weather_station

PARS_DESC = {
    # Station parameters
    'INSI': 'Institute and site code',
    'LAT': 'Latitude, degrees (decimals)',
    'LONG': 'Longitude, degrees (decimals)',
    'ELEV': 'Elevation, m',
    'TAV': 'Temperature average for whole year [long-term], C',
    'AMP': 'Temperature amplitude (range), monthly averages [long-term], C',
    'REFHT': 'Reference height for weather measurements, m',
    'WNDHT': 'Reference height for windspeed measurements, m',
    # Data parameters
    'DATE': 'Date, year + days from Jan. 1',
    'SRAD': 'Daily solar radiation, MJ m-2 day-1',
    'TMAX': 'Daily temperature maximum, C',
    'TMIN': 'Daily temperature minimum, C',
    'RAIN': 'Daily rainfall (incl. snow), mm day-1',
    'DEWP': 'Daily dewpoint temperature average, C',
    'WIND': 'Daily wind speed (km d-1)',
    'PAR': 'Daily photosynthetic radiation, moles m-2 day-1',
    'EVAP': 'Daily pan evaporation (mm d-1)',
    'RHUM': 'Relative humidity average, %'
}
PARS_STATION = ['INSI', 'LAT', 'LONG', 'ELEV', 'TAV', 'AMP', 'REFHT', 'WNDHT']
PARS_DATA = [i for i in PARS_DESC.keys() if i not in PARS_STATION]
MANDATORY_DATA = ['TMIN', 'TMAX', 'RAIN', 'SRAD']

def list_station_parameters():
    '''
    Print a list of the weather station parameters
    '''
    for key, value in PARS_DESC.items():
        if key in PARS_STATION:
            print(key + ': ' + value)

def list_weather_parameters():
    '''
    Print a list of the weather data parameters
    '''
    for key, value in PARS_DESC.items():
        if key in PARS_DATA:
            print(key + ': ' + value)
        

class WeatherData(DataFrame):
    '''
    Creates a WeatherData instance. That instance is the one that contains the records for the Weather Station.

    Arguments
    ----------
    data: pd.Dataframe
        A DataFrame containg the the weather data.
    variables: dict
        A dict to map the columns of the dataframe, to the DSSAT Weather variables. Use `list_weather_parameters` function to have a detailed description of the DSSAT weather variables.
    '''
    def __init__(self, data:DataFrame, variables:dict={}):
        for key, value in variables.items():
            assert value in PARS_DATA, \
                f'{value} is not a valid variable name'
            if (value in PARS_DATA) and (key not in PARS_DATA):
                data[value] = data[key]
                data.drop(columns=[key], inplace=True)

        assert all(map(lambda x: x in data.columns, MANDATORY_DATA)), \
            f'Data must contain at least {", ".join(MANDATORY_DATA)} variables'

        super().__init__(data)

        # A really quick QC check
        TEMP_QC = all(self.TMIN <= self.TMAX)
        assert TEMP_QC, 'TMAX < TMIN at some point in the series'
        if 'RHUM' in data.columns:
            RHUM_QC = all((self.RHUM >= 0) & (self.RHUM <= 100))
            assert RHUM_QC, '0 <= RHUM <= 100 must be accomplished'
        RAIN_QC = all(self.RAIN >= 0)
        assert RAIN_QC, '0 <= RAIN must be accomplished'
        if 'SRAD' in data.columns:
            SRAD_QC = all(self.SRAD >= 0)
            assert SRAD_QC, '0 <= SRAD must be accomplished'

        # Check date column
        DATE_COL = False
        for col in self.columns:
            if pd.api.types.is_datetime64_any_dtype(self[col]):
                DATE_COL = col
        if pd.api.types.is_datetime64_any_dtype(self.index):
            DATE_COL = True
        assert DATE_COL, 'At least one of the data columns must be a date'

        if isinstance(DATE_COL, str):
            self.set_index(DATE_COL, inplace=True)
            
        

class WeatherStation():
    '''
    Initialize a Weather station instance.

    Arguments
    ----------
    pars: dict
        dict with the Weather station parameters. `list_station_parameters` provides a list with the parameters and their description. Only LAT, LON and ELEV parameters are mandatory.
    description: str
        An string with the description of the weather station
    '''
    def __init__(
        self, wthdata:WeatherData, pars:dict,
        description='Weather Station'):
        self.description = description
        self.INSI = 'SERV'
        self.LAT = NA
        self.LON = NA
        self.ELEV = NA 
        self.TAV = 17 
        self.AMP = 10 
        self.REFHT = 2
        self.WNDHT = 10

        self.start_date = None
        self.end_date = None
        for par, value in pars.items():
            assert par in self.__dict__.keys(),\
                f'{par} is not a valid attribute for a WeatherStation class'
            self.__dict__[par] = value
        
        self.INSI = self.INSI[:4].upper()
        assert not any((isna(self.LAT), isna(self.LON), isna(self.ELEV))), \
            'LAT, LON and ELEV parameters are mandatory'

        assert isinstance(wthdata, WeatherData), \
            'wthdata must be a WeatherData instance'
        self.data = wthdata

    def write(self, folder:str='', **kwargs):
        '''
        Writes the weather files in the provided folder. The name is defined by the dates and the Institute code (INSI).

        Arguments
        ----------
        folder: str
            Path to the folder the files will be saved.
            
        '''
        if not os.path.exists(folder):
            os.mkdir(folder)
        man = kwargs.get('management', False)
        if man:
            from datetime import datetime
            sim_start = datetime(man.sim_start.year, man.sim_start.month, man.sim_start.day)
            self.data = self.data.loc[self.data.index >= sim_start]
        for year in self.data.index.year.unique():
            df = self.data.loc[self.data.index.year == year]
            month = df.index[0].strftime('%m')
            filename = f'{self.INSI}{str(year)[2:]}{month}.WTH'
            outstr = f'*WEATHER DATA : {self.description}\n\n'
            outstr += '@ INSI      LAT     LONG  ELEV   TAV   AMP REFHT WNDHT\n'
            outstr += weather_station([
                self.INSI, self.LAT, self.LON, self.ELEV,
                self.TAV, self.AMP, self.REFHT, self.WNDHT
            ])
            outstr += weather_data_header(self.data.columns)
            
            for day, fields in df.iterrows():
                day = day.strftime('%y%j')
                outstr += weather_data([day]+list(fields))
            
            with open(os.path.join(folder, filename), 'w') as f:
                f.write(outstr)
        
