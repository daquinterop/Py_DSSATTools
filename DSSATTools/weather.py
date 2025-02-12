'''
This module hosts the `Weather` class. It also contains the
`list_station_parameters` and `list_weather_variables` which return a list of the
parameters that define the weather station where the data was collected, and the
weather variables that can be included in the dataset. A `Weather` instance is
initialized by passing five mandatory arguments: a pandas dataframe including
the weather data, a dict mapping each dataframe column to one of the DSSAT
weather varaibles, latitude, longitude, and elevation.

The next example illustrates how to define a Weather instance from syntetic data:

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

The parameters of the weather station are defined as attributes of the `Weather`
class. Those parameters can be listed by calling the `list_station_parameters`.
In the next example the reference height for windspeed measurements is defined
for the weather instance created in the previous example:

    >>> weather.WNDHT = 2

'''
import os
import pandas as pd
from pandas import DataFrame
from io import StringIO
from datetime import datetime, date
from pandas import NA, isna
from DSSATTools.base.formater import weather_data, weather_data_header, weather_station
from DSSATTools.base.partypes import (
    DateType, NumberType, Record, TabularRecord, DescriptionType
)

class WeatherRecord(Record):
    prefix=None
    dtypes={
        'date': DateType, 'srad': NumberType, 'tmax': NumberType, 
        'tmin': NumberType, 'rain': NumberType, 'dewp': NumberType,
        'wind': NumberType, 'par': NumberType, 'evap': NumberType, 
        'rhum': NumberType,
    }
    pars_fmt = {
        'date': "%Y%j", 'srad': '>5.1f', 'tmax': '>5.1f', 'tmin': '>5.1f', 
        'rain': '>5.1f', 'dewp': '>5.1f', 'wind': '>5.1f', 'par': '>5.1f', 
        'evap': '>5.1f', 'rhum': '>5.1f',
    }
    table_index = "date"
    def __init__(self, date:date, srad:float, tmax:float, tmin:float, rain:float,
                 dewp:float=None, wind:float=None, par:float=None, evap:float=None,
                 rhum:float=None):
        """
        Initializes a weather record.

        Arguments
        ----------
        date: date
            Date
        srad: float
            Daily solar radiation, MJ m-2 day-1
        tmax: float
            Daily temperature maximum, C
        tmin: float
            Daily temperature minimum, C
        rain: float
            Daily rainfall (incl. snow), mm day-1
        dewp: float
            Daily dewpoint temperature average, C
        wind: float
            Daily wind speed (km d-1)
        par: float
            Daily photosynthetic radiation, moles m-2 day-1
        evap: float
            Daily pan evaporation (mm d-1)
        rhum: float
            Relative humidity average, %
        """
        super().__init__()
        kwargs = {
            'date': date, 'srad': srad, 'tmax': tmax, 'tmin': tmin, 
            'rain': rain, 'dewp': dewp, 'wind': wind, 'par': par, 
            'evap': evap, 'rhum': rhum,
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)


class WeatherStation(TabularRecord):
    """
    A class to represent the DSSAT WTH file/s.
    """
    table_dtype = WeatherRecord
    dtypes = {
        "insi": DescriptionType, 'lat': NumberType, 'long': NumberType, 
        'elev': NumberType, 'tav': NumberType, 'amp': NumberType,  
        'refht': NumberType, 'wndht': NumberType, "cco2": NumberType
    }
    pars_fmt = {
        "insi": '>4', 'lat': '>8.3f', 'long': '>8.3f', 'elev': '>5.0f', 
        'tav': '>5.1f', 'amp': '>5.1f', 'refht': '>5.1f', 'wndht': '>5.1f',
        'cco2': '>5.1f'
    }
    def __init__(self, table:list[WeatherRecord], lat:float, long:float, 
                 insi:str="WSTA", elev:float=None, tav:float=None, amp:float=None,
                 refht:float=None, wndht:float=None, cco2:float=None):
        """
        Initializes a WeatherStation class. It represents the Weather file
        of DSSAT.

        Arguments
        ----------
        table: DataFrame or list[WeatherRecord]
            The weather data table. It can be a DataFrame or a list of 
            WeatherRecords objects. If it's a dataframe, the columnn names must 
            match the DSSAT weather variables standards.
        insi: str
            Institute and site code (4 characters)
        lat: float
            Latitude, degrees (decimals)
        long: float
            Longitude, degrees (decimals)
        elev: float
            Elevation, m
        tav: float
            Temperature average for whole year [long-term], C
        amp: float
            Temperature amplitude (range), monthly averages [long-term], C
        refht: float
            Reference height for weather measurements, m
        wndht: float
            Reference height for windspeed measurements, m
        cco2: float
            CO2 (vpm),
        """
        super().__init__()
        kwargs = {
            "insi": insi, 'lat': lat, 'long': long, 'elev': elev, 'tav': tav, 
            'amp': amp, 'refht': refht, 'wndht': wndht, 'cco2': cco2
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
        self.table = table

    def _write_wth(self):
        out_str = f'$WEATHER DATA : Created with DSSATTools\n\n'
        out_str += '@ INSI      LAT     LONG  ELEV   TAV   AMP REFHT WNDHT  CCO2\n'
        out_str += "  "+self._write_row()
        table_str = self.table._write_table().split("\n")
        header_str = table_str[0]
        table_str = f"@{header_str[1:]}\n" + "\n".join(table_str[1:])
        out_str += table_str
        return out_str
    
    def _write_section(self):
        raise NotImplementedError
    
    def __setitem__(self, key, value):
        if key == "insi":
            assert len(value.strip()) == 4, "INSI must be a 4-character code"
        super().__setitem__(key, value)
        
    @classmethod
    def from_files(cls, files:list[str]):
        """
        Reads a set of WTH files, and returns a WeatherStation object with the
        data and parameters of those files.
        """
        assert len(files) > 0, "files can't be an empty list"
        assert isinstance(files, (list, tuple, set)), \
            "Input must be a list of paths to WTH files"
        assert len({os.path.basename(f)[:4] for f in files}) == 1, \
            "You must provide paths to the same weather station"
        insi = os.path.basename(files[0])[:4]
        files = sorted(files)
        df_list = []
        for file in files:
            with open(file, "r") as f:
                lines = []
                for line in f:
                    if "@ INSI" in line:
                        insi, lat, long, elev, tav, amp, refht, wndth = \
                            f.readline().split()
                    elif ("@DATE" in line):
                        date_fmt = "%y%j"
                        lines.append(line)
                        lines += f.readlines()
                    elif("@  DATE" in line):
                        line = line.replace("@  DATE", "@DATE")
                        date_fmt = "%Y%j"
                        lines.append(line)
                        lines += f.readlines()
                    else:
                        continue
            tmp_df = pd.read_csv(StringIO("".join(lines)), sep="\s+")
            df_list.append(tmp_df)
        
        table_df = pd.concat(df_list, ignore_index=True)
        table_df.columns = [
            col.replace("@", "").strip().lower()
            for col in table_df.columns
        ]
        table_df["date"] = pd.to_datetime(table_df.date, format=date_fmt)
        table_df = table_df.set_index("date")
        table_df = table_df.sort_index()
        table_df = table_df.dropna(how="all", axis=1)
        tmp_df = pd.DataFrame(
            index=pd.date_range(table_df.index[0], table_df.index[-1])
        )
        for col in table_df.columns: tmp_df[col] = table_df[col]
        assert not tmp_df.isna().any(axis=0).any(), \
            "The files generate a timeseries with missing data"
        table_df = tmp_df.copy()
        table_df.index.name = "date"
        table_df = table_df.reset_index()
        
        weather = cls(
            lat=lat, long=long, insi=insi, elev=elev, tav=tav, amp=amp,
            refht=refht, wndht=wndth, table=table_df
        )
        return weather