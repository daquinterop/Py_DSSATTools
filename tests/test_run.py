import pytest

from DSSATTools import (
    Crop, SoilProfile, WeatherData, WeatherStation,
    Management, DSSAT
    )

from datetime import datetime
import pandas as pd
import numpy as np
import os

DATES = pd.date_range('2000-01-01', '2010-12-31')
N = len(DATES)

def test_no_setup():
    with pytest.raises(AssertionError) as excinfo:
        assert 'setup() method' in str(excinfo.value)

def test_run_maize():
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
    # Create a WeatherData instance
    WTH_DATA = WeatherData(
        df,
        variables={
            'tn': 'TMIN', 'TMAX': 'TMAX',
            'prec': 'RAIN', 'rad': 'SRAD',
            'rh': 'RHUM'
        }
    )
    # Create a WheaterStation instance
    wth = WeatherStation(
        WTH_DATA, 
        {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
    )

    soil = SoilProfile(default_class='SIL')
    crop = Crop('maize')
    man = Management(
        cultivar='IB0001',
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd='/tmp/test_mz')
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_millet():
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
    # Create a WeatherData instance
    WTH_DATA = WeatherData(
        df,
        variables={
            'tn': 'TMIN', 'TMAX': 'TMAX',
            'prec': 'RAIN', 'rad': 'SRAD',
            'rh': 'RHUM'
        }
    )
    # Create a WheaterStation instance
    wth = WeatherStation(
        WTH_DATA, 
        {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
    )

    soil = SoilProfile(default_class='SIL')
    crop = Crop('millet')
    man = Management(
        cultivar='999991',
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd='/tmp/test_ml')
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_sugarbeet():
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
    # Create a WeatherData instance
    WTH_DATA = WeatherData(
        df,
        variables={
            'tn': 'TMIN', 'TMAX': 'TMAX',
            'prec': 'RAIN', 'rad': 'SRAD',
            'rh': 'RHUM'
        }
    )
    # Create a WheaterStation instance
    wth = WeatherStation(
        WTH_DATA, 
        {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
    )

    soil = SoilProfile(default_class='SIL')
    crop = Crop('sugarbeet')
    man = Management(
        cultivar='CR0001',
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd='/tmp/test_bs')
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_rice():
    df = pd.DataFrame(
        {
        'tn': np.random.gamma(24, 1, N),
        'rad': np.random.gamma(15, 1.5, N),
        'prec': np.round(np.random.gamma(.4, 10, N), 1),
        'rh': 100 * np.random.beta(1.5, 1.15, N),
        },
        index=DATES,
    )
    df['TMAX'] = df.tn + np.random.gamma(5., .5, N)
    # Create a WeatherData instance
    WTH_DATA = WeatherData(
        df,
        variables={
            'tn': 'TMIN', 'TMAX': 'TMAX',
            'prec': 'RAIN', 'rad': 'SRAD',
            'rh': 'RHUM'
        }
    )
    # Create a WheaterStation instance
    wth = WeatherStation(
        WTH_DATA, 
        {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
    )

    soil = SoilProfile(default_class='SIL')
    crop = Crop('rice')
    man = Management(
        cultivar='IB0003',
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd='/tmp/test_ri')
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_sorghum():
    df = pd.DataFrame(
        {
        'tn': np.random.gamma(24, 1, N),
        'rad': np.random.gamma(15, 1.5, N),
        'prec': np.round(np.random.gamma(.4, 10, N), 1),
        'rh': 100 * np.random.beta(1.5, 1.15, N),
        },
        index=DATES,
    )
    df['TMAX'] = df.tn + np.random.gamma(5., .5, N)
    # Create a WeatherData instance
    WTH_DATA = WeatherData(
        df,
        variables={
            'tn': 'TMIN', 'TMAX': 'TMAX',
            'prec': 'RAIN', 'rad': 'SRAD',
            'rh': 'RHUM'
        }
    )
    # Create a WheaterStation instance
    wth = WeatherStation(
        WTH_DATA, 
        {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
    )

    soil = SoilProfile(default_class='SIL')
    crop = Crop('sorghum')
    man = Management(
        cultivar='IB0001',
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd='/tmp/test_sg')
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_sweetcorn():
    df = pd.DataFrame(
        {
        'tn': np.random.gamma(24, 1, N),
        'rad': np.random.gamma(15, 1.5, N),
        'prec': np.round(np.random.gamma(.4, 10, N), 1),
        'rh': 100 * np.random.beta(1.5, 1.15, N),
        },
        index=DATES,
    )
    df['TMAX'] = df.tn + np.random.gamma(5., .5, N)
    # Create a WeatherData instance
    WTH_DATA = WeatherData(
        df,
        variables={
            'tn': 'TMIN', 'TMAX': 'TMAX',
            'prec': 'RAIN', 'rad': 'SRAD',
            'rh': 'RHUM'
        }
    )
    # Create a WheaterStation instance
    wth = WeatherStation(
        WTH_DATA, 
        {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'dpoes'}
    )

    soil = SoilProfile(default_class='SIL')
    crop = Crop('sweetcorn')
    man = Management(
        cultivar='SW0001',
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd='/tmp/test_sw')
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

if __name__ == '__main__':
    test_run_sweetcorn()