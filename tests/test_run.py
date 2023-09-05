import pytest

from DSSATTools import (
    Crop, SoilProfile, Weather,
    Management, DSSAT
    )
from DSSATTools.base.sections import TabularSubsection
from datetime import datetime
import pandas as pd
import numpy as np
import os
import tempfile

TMP = tempfile.gettempdir()

DATES = pd.date_range('2000-01-01', '2002-12-31')
N = len(DATES)
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
# Create a WheaterStation instance
wth = wth = Weather(
        df, {"tn": "TMIN", "rad": "SRAD", "prec": "RAIN", "rh": "RHUM", "TMAX": "TMAX"},
        4.54, -75.1, 1800
    )

soil = SoilProfile(default_class='SIL')

def test_no_setup():
    with pytest.raises(AssertionError) as excinfo:
        assert 'setup() method' in str(excinfo.value)

def test_run_maize():
    crop = Crop('maize')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_millet():
    soil = SoilProfile(default_class='SIL')
    crop = Crop('millet')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_sugarbeet():
    crop = Crop('sugarbeet')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_rice():
    crop = Crop('rice')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_sorghum():
    crop = Crop('sorghum')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_sweetcorn():
    crop = Crop('sweetcorn')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_alfalfa():
    crop = Crop('alfalfa')
    man = Management(
        planting_date=DATES[10],
    )
    man.mow['table'] = TabularSubsection({
        'DATE': [DATES[300].strftime('%y%j'), DATES[340].strftime('%y%j')], 
        'MOW': [1000, 1000], 'RSPLF': [20, 20], 'MVS': [2, 2], 'RSHT': [5, 5]
    })
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_bermudagrass():
    crop = Crop('bermudagrass')
    man = Management(
        planting_date=DATES[10],
    )
    man.mow['table'] = TabularSubsection({
        'DATE': [DATES[300].strftime('%y%j'), DATES[340].strftime('%y%j')], 
        'MOW': [1000, 1000], 'RSPLF': [20, 20], 'MVS': [2, 2], 'RSHT': [5, 5]
    })
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_soybean():
    crop = Crop('soybean')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_run_canola():
    crop = Crop('canola')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_run_sunflower():
    crop = Crop('sunflower')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))


def test_run_potato():
    crop = Crop('potato')
    man = Management(
        planting_date=DATES[10],
    )
    man.planting_details['PLWT'] = 1500
    man.planting_details['SPRL'] = 2
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_run_potato_no_transplanting():
    crop = Crop('potato')
    man = Management(
        planting_date=DATES[10],
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    with pytest.raises(AssertionError) as excinfo:
        dssat.run(
            soil=soil, weather=wth, crop=crop, management=man,
        )
        assert 'transplanting parameters are mandatory' in str(excinfo.value)

def test_run_tomato():
    crop = Crop('tomato')
    man = Management(
        planting_date=DATES[10],
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_run_cabbage():
    crop = Crop('cabbage')
    man = Management(
        planting_date=DATES[10],
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_run_sugarcane():
    crop = Crop('Sugarcane')
    man = Management(
        planting_date=DATES[10],
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_sc'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_close():
    crop = Crop('cabbage')
    man = Management(
        planting_date=DATES[10],
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(TMP, 'test_mz'))
    dssat.close()
    assert not os.path.exists(os.path.join(TMP, 'test_mz'))


def test_issue_1():
    # https://github.com/daquinterop/Py_DSSATTools/issues/1
    crop = Crop('soybean', 'IB0011')
    man = Management(
        planting_date=DATES[10],
        irrigation='A',
        fertilization='A'
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    assert crop.cultivar['LFMAX'] == 1.020
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    final_yield = int(dssat.output['PlantGro']['GWAD'].max())
    crop.cultivar['LFMAX'] = 1.35
    assert crop.cultivar['LFMAX'] == 1.35
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert dssat.output['PlantGro']['GWAD'].max() != final_yield    


def test_set_crop_parameter_and_run():
        crop = Crop('maize', 'IB0011')
        assert crop.cultivar['PHINT'] == 38.9
        crop.cultivar['PHINT'] = 30.
        assert crop.cultivar['PHINT'] == 30.

        man = Management(
            planting_date=DATES[10],
            irrigation='A',
            fertilization='A'
        )

        dssat = DSSAT()
        dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
        dssat.run(
            soil=soil, weather=wth, crop=crop, management=man,
        )
    
def test_issue_11():
    crop = Crop('maize')
    man = Management(
        planting_date=DATES[10],
    )
    crop.cultivar['P5'] = 1100.
    crop.cultivar['G2'] = 1050.
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))    

def test_outputs():
    """
    Test that different outputs are saved if they have been defined in the 
    simulation_controls
    """
    crop = Crop('maize')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    outputs = ['PlantGro', "Weather", "SoilWat", "SoilOrg"]
    assert all(map(lambda x: x in outputs, dssat.output))

    man.simulation_controls["GROUT"] = "N"
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert all(
        map(lambda x: (x in ["SoilWat", "SoilOrg"]) 
            and (x not in ['PlantGro', "Weather"]) 
            ,dssat.output)
    )
    assert all(map(lambda x: x in outputs, dssat.output))

    man.simulation_controls["WAOUT"] = "N"
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert all(
        map(lambda x: (x in ["SoilOrg"]) 
            and (x not in ['PlantGro', "Weather", "SoilWat"]) 
            ,dssat.output)
    )

    man.simulation_controls["CAOUT"] = "N"
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    with pytest.warns(UserWarning, match='No output has been'):
        dssat.output 

# def test_issue14():
#     crop = Crop('maize')
#     man = Management(
#         planting_date=DATES[10],
#     )
#     man.simulation_controls["NYERS"] = 2
#     dssat = DSSAT()
#     dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
#     dssat.run(
#         soil=soil, weather=wth, crop=crop, management=man,
#     )


def test_no_wat_sim():
    crop = Crop('maize')
    man = Management(
        planting_date=DATES[10],
    )
    man.simulation_controls["WATER"] = "N" 
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )



if __name__ == '__main__':
    test_issue14()