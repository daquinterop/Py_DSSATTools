from pyparsing import col
import pytest
from DSSATTools.weather import Weather
import pandas as pd
import numpy as np
import shutil
import os
import platform
if 'windows' in platform.system().lower():
    BASE_PATH = 'C:/Users/daqui/'
else:
    BASE_PATH='/home/diego'

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
        folder = os.path.join(BASE_PATH, 'Py_DSSATTools', 'wth_test')
        if os.path.exists(folder): shutil.rmtree(folder)
        wth = Weather(df, variables, 4.54, -75.1, 1800)
        wth.write(folder)
        assert os.path.exists(folder)
        for year in range(2000, 2010):
            year = str(year)[2:]
            assert os.path.exists(os.path.join(folder, f'WSTA{year}01.WTH'))

    def test_wrong_variable_map(self):
        with pytest.raises(AssertionError) as excinfo:
            Weather(df, {
                'TMIN': 'TMIN', 'TMAX': 'TMAX',
                'prec': 'RAIN', 'SRAD': 'HPTA',
            }, 4.54, -75.1, 1800)
        assert 'HPTA is not a valid variable name' in str(excinfo.value)

    def test_no_minimum_required_variables(self):
        with pytest.raises(AssertionError) as excinfo:
            Weather(df[["tn", "TMAX"]], {
                'TMIN': 'TMIN', 'TMAX': 'TMAX',
                'prec': 'RAIN', 'SRAD': 'HPTA',
            }, 4.54, -75.1, 1800)
        assert 'Data must contain at least' in str(excinfo.value)

#     def test_no_max_min_consistency(self):
#         with pytest.raises(AssertionError) as excinfo:
#             WeatherData(pd.DataFrame({
#                 'TMIN': [32, 23], 'TMAX': [23, 43],
#                 'SRAD': [14, 10], 'RAIN': [0, 0]
#             }))
#         assert 'TMAX < TMIN' in str(excinfo.value)

#     def test_no_hr_consistency(self):
#         with pytest.raises(AssertionError) as excinfo:
#             WeatherData(pd.DataFrame({
#                 'TMIN': [14, 23], 'TMAX': [23, 43],
#                 'SRAD': [14, 10], 'RAIN': [0, 0],
#                 'RHUM': [0, -2]
#             }))
#         assert 'RHUM <= 100' in  str(excinfo.value)

#     def test_no_rain_consistency(self):
#         with pytest.raises(AssertionError) as excinfo:
#             WeatherData(pd.DataFrame({
#                 'TMIN': [14, 23], 'TMAX': [23, 43],
#                 'SRAD': [14, 10], 'RAIN': [-2, 0],
#                 'RHUM': [23, 12]
#             }))
#         assert '0 <= RAIN' in str(excinfo.value)

#     def test_no_srad_consistency(self):
#         with pytest.raises(AssertionError) as excinfo:
#             WeatherData(pd.DataFrame({
#                 'TMIN': [14, 23], 'TMAX': [23, 43],
#                 'SRAD': [-2, 10], 'RAIN': [1, 0],
#                 'RHUM': [23, 12]
#             }))
#         assert '0 <= SRAD' in str(excinfo.value)


#     def test_no_date(self):
#         with pytest.raises(AssertionError) as excinfo:
#             WeatherData(pd.DataFrame({
#                 'TMIN': [14, 23], 'TMAX': [23, 43],
#                 'SRAD': [2, 10], 'RAIN': [1, 0],
#                 'RHUM': [23, 12],
#             }))
#         assert 'of the data columns must be a date' in str(excinfo.value)

#     def test_index_date(self):
#         WeatherData(pd.DataFrame(
#             {
#             'TMIN': [14, 23], 'TMAX': [23, 43],
#             'SRAD': [2, 10], 'RAIN': [1, 0],
#             'RHUM': [23, 12],
#             },
#             index=pd.date_range('2022-01-01', '2022-01-02'),
#         ))