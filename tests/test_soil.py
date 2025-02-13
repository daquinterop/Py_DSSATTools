import pytest
from DSSATTools.soil import SoilProfile, estimate_from_texture
import numpy as np
import os
import platform

if 'windows' in platform.system().lower():
    BASE_PATH = 'C:/Users/daqui/'
else:
    BASE_PATH='/home/diego'

def test_from_file_single():
    soil = SoilProfile.from_file("IBMZ910214")
    return
    
def test_from_file_double():
    soil = SoilProfile.from_file("UFBG760002")
    return

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
    test_estimate()