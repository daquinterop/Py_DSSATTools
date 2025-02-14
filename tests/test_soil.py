import pytest
from DSSATTools.soil import SoilProfile, estimate_from_texture
import numpy as np
import os
import platform

def test_from_file_single():
    soil = SoilProfile.from_file("IBMZ910214")
    return
    
def test_from_file_double():
    soil = SoilProfile.from_file("UFBG760002")
    return

def test_open_all():
    from DSSATTools import __file__ as module_path
    DSSAT_MODULE_PATH = os.path.dirname(module_path)
    SOIL_PATH = os.path.join(DSSAT_MODULE_PATH, 'static', 'Soil', 'SOIL.SOL')
    with open(SOIL_PATH, "r") as f:
        lines = f.readlines()
    soil_names = list(filter(lambda x: x[0] == "*", lines))
    soil_names = [name[1:11] for name in soil_names[1:]]
    for name in soil_names:
        SoilProfile.from_file(name)

def test_profile_not_in_file():
    with pytest.raises(AssertionError) as excinfo:
        SoilProfile.from_file("UFBG760323")
        assert 'profile not in' in str(excinfo.value)

def test_wrong_name():
    soil = SoilProfile.from_file("IBMZ910214")
    with pytest.raises(AssertionError) as excinfo:
        soil["name"] = "012345678"
        assert "Soil profile Name must be 10 characters" in str(excinfo.value)
    with pytest.raises(AssertionError) as excinfo:
        soil["name"] = "012345678910"
        assert "Soil profile Name must be 10 characters" in str(excinfo.value)

def test_estimate():
    estimate_from_texture(35, 30)

if __name__ == "__main__":
    test_open_all()