from pyparsing import col
import pytest
from DSSATTools import Weather, SoilProfile, DSSAT, Management, Crop
from datetime import datetime
import pandas as pd
import numpy as np
import shutil
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

DATES = pd.date_range('2000-01-01', '2010-12-31')
N = len(DATES)
df = pd.DataFrame(
    {
    'tn': np.random.gamma(10, 1, N),
    'rad': np.random.gamma(10, 1.5, N),
    'prec': np.round(np.random.gamma(.4, 10, N), 1),
    'rh': 100 * np.random.beta(1.5, 1.15, N),
    },
    index=DATES,
)
df['TMAX'] = df.tn + np.random.gamma(5., .5, N)
WTH_DATA = df

variables={
    'tn': 'TMIN', 'TMAX': 'TMAX',
    'prec': 'RAIN', 'rad': 'SRAD',
    'rh': 'RHUM'
}

class TestWeather:  
    def test_write(self):
        folder = os.path.join(PROJECT_ROOT, 'tests', 'wth_test')
        if os.path.exists(folder): shutil.rmtree(folder)
        wth = Weather(df, variables, 4.54, -75.1, 1800)
        wth.write(folder)
        assert os.path.exists(folder)
        assert os.path.exists(os.path.join(folder, f'WSTA0011.WTH'))

    def test_wrong_variable_map(self):
        with pytest.raises(AssertionError) as excinfo:
            Weather(df, {
                'tn': 'TMIN', 'TMAX': 'TMAX',
                'prec': 'RAIN', 'rad': 'HPTA',
            }, 4.54, -75.1, 1800)
        assert 'HPTA is not a valid variable name' in str(excinfo.value)

    def test_no_minimum_required_variables(self):
        with pytest.raises(AssertionError) as excinfo:
            Weather(df[["tn", "TMAX"]], {
                'tn': 'TMIN', 'TMAX': 'TMAX',
            }, 4.54, -75.1, 1800)
        assert 'Data must contain at least' in str(excinfo.value)

    def test_no_max_min_consistency(self):
        with pytest.raises(AssertionError) as excinfo:
            Weather(
                pd.DataFrame({
                'TMIN': [32, 23], 'TMAX': [23, 43],
                'SRAD': [14, 10], 'RAIN': [0, 0]
                }),
                {"TMIN": "TMIN", "TMAX": "TMAX", 
                 "RAIN": "RAIN", "SRAD": "SRAD"},
                 2.54, -75.1, 1800
            )
        assert 'TMAX < TMIN' in str(excinfo.value)

    def test_no_hr_consistency(self):
        with pytest.raises(AssertionError) as excinfo:
            Weather(
                pd.DataFrame({
                'TMIN': [14, 23], 'TMAX': [23, 43],
                'SRAD': [14, 10], 'RAIN': [0, 0],
                'RHUM': [0, -2]
                }),
                {"TMIN": "TMIN", "TMAX": "TMAX", "RHUM": "RHUM", 
                 "RAIN": "RAIN", "SRAD": "SRAD"},
                 2.54, -75.1, 1800
            )
        assert 'RHUM <= 100' in  str(excinfo.value)

    def test_no_rain_consistency(self):
        with pytest.raises(AssertionError) as excinfo:
            Weather(
                pd.DataFrame({
                'TMIN': [14, 23], 'TMAX': [23, 43],
                'SRAD': [14, 10], 'RAIN': [-2, 0],
                'RHUM': [23, 12]
                }),
                {"TMIN": "TMIN", "TMAX": "TMAX", "RHUM": "RHUM", 
                 "RAIN": "RAIN", "SRAD": "SRAD"},
                 2.54, -75.1, 1800
            )
        assert '0 <= RAIN' in str(excinfo.value)

    def test_no_srad_consistency(self):
        with pytest.raises(AssertionError) as excinfo:
            Weather(
                pd.DataFrame({
                'TMIN': [14, 23], 'TMAX': [23, 43],
                'SRAD': [-2, 10], 'RAIN': [1, 0],
                'RHUM': [23, 12]
                }),
                {"TMIN": "TMIN", "TMAX": "TMAX", "RHUM": "RHUM", 
                 "RAIN": "RAIN", "SRAD": "SRAD"},
                 2.54, -75.1, 1800
            )
        assert '0 <= SRAD' in str(excinfo.value)

    def test_no_date(self):
        with pytest.raises(AssertionError) as excinfo:
            Weather(
                pd.DataFrame({
                'TMIN': [14, 23], 'TMAX': [23, 43],
                'SRAD': [2, 10], 'RAIN': [1, 0],
                'RHUM': [23, 12],
                }),
                {"TMIN": "TMIN", "TMAX": "TMAX", "RHUM": "RHUM", 
                 "RAIN": "RAIN", "SRAD": "SRAD"},
                 2.54, -75.1, 1800
            )
        assert 'of the data columns must be a date' in str(excinfo.value)

    def test_co2_value(self):
        '''
        Run with default CO2 option (Mauna Loa), then modify CO2 and check the 
        Weather output files.
        '''
        wth = Weather(df, {
            'tn': 'TMIN', 'TMAX': 'TMAX',
            'prec': 'RAIN', 'rad': 'SRAD',
        }, 4.54, -75.1, 1800)
        soil = SoilProfile(default_class='SIL')
        man = Management(planting_date=datetime(2000, 2, 1))
        crop = Crop("maize")
        dssat = DSSAT()
        dssat.setup()
        # Test CO2 from Mauna Loa
        man.simulation_controls["CO2"] = "M"
        dssat.run(
            soil, wth, crop, man
        )
        assert np.isclose(dssat.output["Weather"]["CO2D"].iloc[0], 368.73, atol=1)
        # Test default value (380)
        man.simulation_controls["CO2"] = "D"
        dssat.run(
            soil, wth, crop, man
        )
        assert np.isclose(dssat.output["Weather"]["CO2D"].iloc[0], 380., atol=1)
        # test CO2 in weather station
        man.simulation_controls["CO2"] = "W"
        wth.CO2 = 500
        dssat.run(
            soil, wth, crop, man
        )
        assert np.isclose(dssat.output["Weather"]["CO2D"].iloc[0], 500., atol=1)
