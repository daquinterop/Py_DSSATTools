# TODO: Make tests with the experiments included in DSSAT
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
wth =  Weather(
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

def test_run_wheat():
    # KSAS8101 experiment, treatment 1
    crop = Crop('Wheat', "IB0488")
    soil = SoilProfile("tests/input_files/SOIL.SOL", "IBWH980018")
    # Management
    df = pd.DataFrame()
    for year in range(81, 83):
        df = pd.concat(
            [df, pd.read_csv(f"tests/input_files/wheat/KSAS{year}01.WTH", skiprows=4, sep="\s+")], 
            ignore_index=True
        )
    df.index = pd.to_datetime(df["@DATE"], format="%y%j")
    df = df.sort_index()
    wth =  Weather(
        df, {"TMIN": "TMIN", "SRAD": "SRAD", "RAIN": "RAIN", "TMAX": "TMAX"},
        lat=37.18, lon=-99.75, elev=226, tav=12., amp=32
    )
    
    man = Management(
        planting_date=datetime.strptime("81289", "%y%j"),
    )
    # Initial conditions 
    pars = {
        "PCR": "WH", "ICDAT": "81279", "ICRT": 1200, "ICND": 0, "ICRN": 1,
        "ICRE": 1, "ICRES": 6500, "ICREN": 1.14, "ICREP": 0, "ICRIP": 100,
        "ICRID": 15,
    }
    for key, val in pars.items(): man.initial_conditions[key] = val
    man.initial_conditions["table"] = TabularSubsection(pd.DataFrame(
        [(  15,  .205,   3.4,   9.8),
         (  30,   .17,   3.2,   7.3),
         (  60,  .092,   2.5,   5.1),
         (  90,  .065,   2.2,   4.7),
         ( 120,  .066,   2.7,   4.3),
         ( 150,  .066,   2.7,   4.3),
         ( 180,  .066,   2.7,   4.3)],
        columns=["ICBL", "SH2O", "SNH4", "SNO3"]
    ))
    # Planting
    pars = {
        "EDATE": None, "PPOP": 162, "PPOE": 162, "PLME": "S", "PLRS": 16,
        "PLRD": 0, "PLDP": 5.5 
    }
    for key, val in pars.items(): man.planting_details[key] = val
    # Simulation controls
    pars = {
        "WATER": "Y", "NITRO": "Y", "CO2": "M", "WTHER": "M", "INCON": "M",
        "LIGHT": "E", "EVAPO": "R", "INFIL": "S", "PHOTO": "C", "HYDRO": "R",
        "NSWIT": 1, "MESOM": "G", "MESEV": "S", "MESOL": 2, "PLANT": "R",
        "IRRIG": "R", "FERTI": "R", "RESID": "N", "HARVS": "M", "SDATE": 81279,
        "RSEED": 2150, "NIOUT": "Y", "CAOUT": "N",
    }
    for key, val in pars.items(): man.simulation_controls[key] = val
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_wh'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    harwt = int(dssat.stdout.split("\n")[-1].split()[6])
    assert np.isclose(2417, harwt, rtol=0.01)

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

def test_setup_setup_deprecation():
    dssat = DSSAT()
    with pytest.warns(DeprecationWarning, match='calling setup method is not longer needed'):
        dssat.setup()
    
    

if __name__ == '__main__':
    test_run_wheat()