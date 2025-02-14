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

from DSSATTools.crop import Maize
from DSSATTools.soil import SoilProfile
from DSSATTools.filex import read_filex, Field
from DSSATTools.weather import WeatherStation
from DSSATTools.run import DSSAT
from datetime import datetime, timedelta
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
    dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=cultivar, 
        planting=treatment["Planting"],
        initial_conditions=treatment["InitialConditions"],
        fertilizer=treatment["Fertilizer"],
        simulation_controls=treatment["SimulationControls"]
    )
    harwt = int(dssat.stdout.split("\n")[-1].split()[6])
    assert np.isclose(3676, harwt, rtol=0.01)
    dssat.close()


if __name__ == "__main__":
    test_maize()