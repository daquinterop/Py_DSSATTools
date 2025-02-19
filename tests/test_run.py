# TODO: Make tests with the experiments included in DSSAT
"""
Each test is runs one of the experiments included in DSSAT for that crop. The 
test pass if the result is close enough to the one obtained using the desktop
version of DSSAT. Close enough is an error of less than 1%.

This is the list of crops and the tested experiments:

| Crop         | Experiment | Treat |
|--------------|------------|-------|
| Maize        | BRPI0202   |   1   |
| Wheat        | KSAS8101   |   1   |
| Tomato       | UFBR9401   |   4   |
| Soybean      | CLMO8501   |   1   |
| Sorghum      | ITHY8001   |   2   |
| Alfalfa      | AGZG1501   |   1   |
| Dry Bean     | CCPA8629   |   1   |
| Rice         | Pending
| Millet       | Pending
| Sugarbeet    | Pending
| Sweetcorn    | Pending
| Bermudagrass | Pending
| Canola       | Pending
| Sunflower    | Pending
| Potato       | Pending
| Cabbage      | Pending
| Sugarcane    | Pending
"""
import pytest

from DSSATTools.crop import (
    Maize, Sorghum, Wheat, Tomato, Alfalfa
)
from DSSATTools.soil import SoilProfile
from DSSATTools.filex import (
    read_filex, Field, InitialConditions, Planting, Fertilizer, 
    FertilizerEvent, SimulationControls, SCGeneral, SCManagement,
    SCMethods, SCOptions, Mow
)
from DSSATTools.weather import WeatherStation
from DSSATTools.run import DSSAT
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
import os
import tempfile
from io import StringIO

TMP = tempfile.gettempdir()
DATA_PATH = "/home/diego/dssat-csm-data"

def test_modify_runpath():
    with pytest.raises(RuntimeError) as excinfo:
        dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
        dssat.run_path = "runpath"
        assert 'run_path attribute ' in str(excinfo.value)

def test_maize():
    """
    Experiment BRPI0202, treatment 1
    """
    cultivar = Maize("IB0171")
    soil = SoilProfile.from_file(
        "BRPI020001",
        os.path.join(DATA_PATH, "Soil", "BR.SOL")
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "BRPI0201.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH,"Maize", "BRPI0202.MZX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT("/tmp/dssat_test")
    results = dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=cultivar, 
        planting=treatment["Planting"],
        initial_conditions=treatment["InitialConditions"],
        fertilizer=treatment["Fertilizer"],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(3676, results['harwt'], rtol=0.01)
    dssat.close()

def test_sorghum():
    """
    Experiment ITHY8001, treatment 2
    """
    cultivar = Sorghum('IB0026')
    soil = SoilProfile.from_file('IBSG910085')
    df = []
    for year in range(80, 82):
        df.append(pd.read_csv(
            os.path.join(DATA_PATH, 'Weather', f'ITHY{year}01.WTH'),
            skiprows=3, sep="\s+"
        ))
    df = pd.concat(df, ignore_index=True)
    df.columns = ['date', 'srad', 'tmax', 'tmin', 'rain']
    df["date"] = pd.to_datetime(df.date, format='%y%j')
    weather_station = WeatherStation(
        lat=17.530, long=78.270, elev=0, tav=25.8, amp=11.8, refht=2., 
        wndht=3., table=df
    )
    field = Field(
        id_field='ITHY0001', wsta=weather_station, flob=0, fldt='DR000', 
        fldd=0, flds=0, id_soil=soil
    )
    initial_conditions = InitialConditions(
        pcr='SG', icdat=date(1980, 1, 1)+timedelta(164), icrt=500, icnd=0,
        icrn=1, icre=1, icres=1300, icren=.5, icrep=0, icrip=100, icrid=10,
        table=pd.DataFrame([
            (10, .06, 2.5, 1.8),
            (22, .06, 2.5, 1.8),
            (52, .195, 3., 4.5),
            (82, .21, 3.5, 5.0),
            (112, 0.2, 2., 2.0),
            (142, 0.2, 1., 0.7),
            (172, 0.2, 1., 0.6),
        ], columns=['icbl', 'sh2o', 'snh4', 'sno3'])
    )
    planting = Planting(
        pdate=date(1980, 1, 1) + timedelta(168), ppop=18, ppoe=18, plme='S',
        plds='R', plrs=45, plrd=0, pldp=5
    )
    fertilizer = Fertilizer(table=[
        FertilizerEvent(
            fdate=date(1980, 1, 1) + timedelta(184), fmcd='FE005', fdep=5,
            famn=80, facd='AP002'
        )
    ])
    simulation_controls = SimulationControls(
        general=SCGeneral(sdate=date(1980, 1, 1) + timedelta(164)),
        options=SCOptions(water='Y', nitro='Y', symbi='N'),
        methods=SCMethods(infil='S'),
        management=SCManagement(irrig='N', ferti='R', resid='N', harvs='M')
    )
    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        field=field, cultivar=cultivar, planting=planting, 
        initial_conditions=initial_conditions, fertilizer=fertilizer,
        simulation_controls=simulation_controls
    )
    assert np.isclose(6334, results['harwt'], rtol=0.01)
    dssat.close()

def test_wheat():
    """
    Experiment KSAS8101, treatment 1
    """
    cultivar = Wheat('IB0488')
    soil = SoilProfile.from_file("IBWH980018")
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "KSAS8101.WTH"),
        os.path.join(DATA_PATH, 'Weather', "KSAS8201.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Wheat', "KSAS8101.WHX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=cultivar, 
        planting=treatment["Planting"],
        initial_conditions=treatment["InitialConditions"],
        fertilizer=treatment["Fertilizer"],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(2417, results['harwt'], rtol=0.01)
    dssat.close()

def test_tomato():
    """
    Experiment KSAS8101, treatment 4
    """
    cultivar = Tomato('TM0007')
    soil = SoilProfile.from_file("UFBR950001")
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "UFBR9401.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Tomato', "UFBR9401.TMX"))
    treatment = treatments[4]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=cultivar, 
        planting=treatment["Planting"],
        initial_conditions=treatment["InitialConditions"],
        fertilizer=treatment["Fertilizer"],
        irrigation=treatment["Irrigation"],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(6360, results['harwt'], rtol=0.01)
    dssat.close()

def test_soybean():
    """
    Experiment CLMO8501, treatment 1
    """
    soil = SoilProfile.from_file("IBSB910032")
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "CLMO8501.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Soybean', "CLMO8501.SBX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=treatment['Cultivar'].crop, 
        planting=treatment["Planting"],
        initial_conditions=treatment["InitialConditions"],
        irrigation=treatment["Irrigation"],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(2495, results['harwt'], rtol=0.01)
    dssat.close()
    
def test_alfalfa():
    """
    Experiment AGZG1501, Treatment 1  
    """
    mow = Mow.from_file(os.path.join(DATA_PATH, 'Alfalfa', 'AGZG1501.MOW'))
    soil = SoilProfile.from_file(
        "AGSP209115", os.path.join(DATA_PATH, 'Soil', "AG.SOL")
    )
    cultivar = Alfalfa('AL0001')
    df = []
    for year in range(15, 18):
        df.append(pd.read_fwf(
            os.path.join(DATA_PATH, 'Weather', f'TARD{year}01.WTH'),
            skiprows=4, colspecs=[(6*i, 6*i+5) for i in range(10)]
        ))
    df = pd.concat(df, ignore_index=True)
    df.columns = [
        'date', 'srad', 'tmax', 'tmin', 'rain', 'dewp',
        'wind', 'par', 'evap', 'rhum'
    ]
    df = df.interpolate() # There is one missing record for wind and par
    df["date"] = pd.to_datetime(df.date, format='%y%j')
    df = df.dropna(how='all', axis=1)
    weather_station = WeatherStation(
        lat=33.3, long=-84.3, elev=300, tav=14.3, amp=18.2, 
        table=df
    )
    treatments = read_filex(os.path.join(DATA_PATH, 'Alfalfa', "AGZG1501.ALX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=cultivar, 
        planting=treatment["Planting"],
        irrigation=treatment["Irrigation"],
        fertilizer=treatment["Fertilizer"],
        harvest=treatment['Harvest'],
        simulation_controls=treatment["SimulationControls"],
        mow=mow
    )
    # Open FORAGE.out
    forage = pd.read_fwf(
        StringIO(dssat.output_files['FORAGE']),
        skiprows=1, widths=[5, 9, 3] + [5]*18
    )
    dssat_gui_values = [2151, 3341, 6303, 3555, 4099, 4104, 6056]
    assert all([
        np.isclose(gui, i, rtol=0.01) 
        for gui, i in zip(dssat_gui_values, forage.FHWAH)
    ])
    dssat.close()

def test_dryBean():
    """
    Experiment CCPA8629, Treatment 1
    """
    soil = SoilProfile.from_file("IBBN910030")
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "CCPA8601.WTH"),
        os.path.join(DATA_PATH, 'Weather', "CCPA8501.WTH")
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Drybean', "CCPA8629.BNX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=treatment['Cultivar'].crop, 
        initial_conditions=treatment['InitialConditions'],
        planting=treatment["Planting"],
        irrigation=treatment["Irrigation"],
        fertilizer=treatment['Fertilizer'],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(3171, results['harwt'], rtol=0.01)
    dssat.close()

def test_rice():
    """
    Experiment DTSP8502, Treatment 4
    """
    soil = SoilProfile.from_file("IBRI910024")
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "DTSP8501.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Rice', "DTSP8502.RIX"))
    treatment = treatments[4]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=treatment['Cultivar'].crop, 
        initial_conditions=treatment['InitialConditions'],
        planting=treatment["Planting"],
        irrigation=treatment["Irrigation"],
        fertilizer=treatment['Fertilizer'],
        residue=treatment['Residue'],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(4698, results['harwt'], rtol=0.01)
    dssat.close()

if __name__ == "__main__":
    test_rice()