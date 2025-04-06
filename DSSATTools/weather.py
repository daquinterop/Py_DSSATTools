'''
This module contains the classes that handle the weather definition. The 
WeatherStation class represents the DSSAT weather station. The weather station
object can be created by reading the data from existing DSSAT wheater files:
    >>> weather = WeatherStation.from_files(["UAFD9001.WTH", "UAFD9101.WTH",])
Note that the input parameter is a list of files, as DSSAT can have multiple files
for the same station. The list of files must correspond to the same station. The
weather station can also be created using the data from a DataFrame:
    >>> weather_station = WeatherStation(
    >>>     insi='UNCU', lat=4.34, long=-74.40, elev=1800, 
    >>>     table=df_with_data
    >>> )
where the df_with_data contains the weather data and its column names match the 
DSSAT weather parameters' names. As with the event-based sections of the FileX,
the table is a list of events (daily weather records). In this case the 
WeatherRecord class is the class representing each daily weather record.
'''
import os
import pandas as pd
from io import StringIO
from datetime import date
from .base.partypes import (
    DateType, NumberType, Record, TabularRecord, DescriptionType,
    clean_comments, parse_pars_line
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

    @property
    def str(self):
        wth_year = self.table[0]["date"].year
        wth_len = self.table[-1]["date"].year - wth_year + 1
        wth_filename = f'{self["insi"]}{str(wth_year)[2:]}{wth_len:02d}'
        return wth_filename
        
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
                        sta_pars = parse_pars_line(f.readline()[2:], cls.pars_fmt)
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
            lines = clean_comments(lines)
            tmp_df = pd.read_csv(StringIO("".join(lines)), sep="\s+")
            df_list.append(tmp_df)
        
        table_df = pd.concat(df_list, ignore_index=True)
        table_df = table_df.drop_duplicates()
        table_df.columns = [
            col.replace("@", "").strip().lower()
            for col in table_df.columns
        ]
        table_df["date"] = table_df.date.map(lambda x: f'{int(x):05d}')
        table_df["date"] = pd.to_datetime(table_df.date, format=date_fmt)
        table_df = table_df.set_index("date")
        table_df = table_df.sort_index()
        table_df = table_df.dropna(how="all", axis=1)
        tmp_df = pd.DataFrame(
            index=pd.date_range(table_df.index[0], table_df.index[-1])
        )
        for col in table_df.columns: tmp_df[col] = table_df[col]
        # assert not tmp_df.isna().any(axis=0).any(), \
        #     "The files generate a timeseries with missing data"
        table_df = tmp_df.copy()
        table_df.index.name = "date"
        for col in table_df.columns: # Some Weather files have one character flags
            table_df[col] = table_df[col].astype(str)\
                .str.replace('[A-Z]','', regex=True).astype(float)
        table_df = table_df.reset_index()
        sta_pars["table"] = table_df
        weather = cls(**sta_pars)
        return weather