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
    man.harvest_details['table'].loc[0, ['HDATE', 'HPC']] = \
        [DATES[190].strftime('%y%j'), 100]

    dssat = DSSAT()
    dssat.setup(cwd='/tmp/dssattest')
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    dssat.close()
    assert not os.path.exists(dssat._RUN_PATH)
