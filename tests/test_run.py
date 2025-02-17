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
| Millet       | Pending
| Sugarbeet    | Pending
| Rice         | Pending
| Sweetcorn    | Pending
| Bermudagrass | Pending
| Canola       | Pending
| Sunflower    | Pending
| Potato       | Pending
| Cabbage      | Pending
| Sugarcane    | Pending
"""
import pytest

from DSSATTools.crop import Maize, Sorghum
from DSSATTools.soil import SoilProfile
from DSSATTools.filex import (
    read_filex, Field, InitialConditions, Planting, Fertilizer, 
    FertilizerEvent, SimulationControls, SCGeneral, SCManagement,
    SCMethods, SCOptions
)
from DSSATTools.weather import WeatherStation
from DSSATTools.run import DSSAT
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
import os
import tempfile

TMP = tempfile.gettempdir()
WEATHER_PATH = "/home/diego/dssat-csm-data/Weather/"

def test_modify_runpath():
    with pytest.raises(RuntimeError) as excinfo:
        dssat = DSSAT("/tmp/dssat_test")
        dssat.run_path = "runpath"
        assert 'run_path attribute ' in str(excinfo.value)

def test_maize():
    """
    Experiment BRPI0202, treatment 1
    """
    cultivar = Maize("IB0171")
    soil = SoilProfile.from_file("BRPI020001", "tests/input_files/BR.SOL")
    weather_station = WeatherStation.from_files([
        os.path.join(WEATHER_PATH, "BRPI0201.WTH"),
    ])
    treatments = read_filex("/home/diego/dssat-csm-data/Maize/BRPI0202.MZX")
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
            f"tests/input_files/ITHY{year}01.WTH", skiprows=3, 
            sep="\s+"
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
    dssat = DSSAT("/tmp/dssat_test")
    results = dssat.run_treatment(
        field=field, cultivar=cultivar, planting=planting, 
        initial_conditions=initial_conditions, fertilizer=fertilizer,
        simulation_controls=simulation_controls
    )
    assert np.isclose(6334, results['harwt'], rtol=0.01)
    dssat.close()

if __name__ == "__main__":
    test_sorghum()