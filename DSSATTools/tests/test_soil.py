import pytest
from DSSATTools.soil import SoilProfile, estimate_from_texture, SoilLayer
import numpy as np
import os
import platform

DATA_PATH = "/home/diego/dssat-csm-data"

def test_from_file_single():
    soil = SoilProfile.from_file(
        "IBMZ910214",
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
    return

def test_from_scratch():
    soil = SoilProfile(
        name='IBMZ910214', soil_series_name='Millhopper Fine Sand', 
        site='Gainesville', country='USA', lat=29.6, long=-82.37, 
        soil_data_source='Gainesville', soil_clasification='S',
        scs_family='Loamy,silic,hyperth Arnic Paleudult', scom='', salb=0.18, 
        slu1=2.0, sldr=0.65, slro=60.0, slnf=1.0, slpf=0.92, smhb='IB001',
        smpx='IB001', smke='IB001',
        table = [
            SoilLayer(
                slb=5.0, slmh='', slll=0.026, sdul=0.096, ssat=0.345, srgf=1.0, 
                ssks=7.4, sbdm=1.66, sloc=0.67, slcl=1.7, slsi=0.9, slcf=0.0, 
                slhw=7.0, scec=20.0
            ),
            SoilLayer(
                slb=15.0, slmh='', slll=0.025, sdul=0.105, ssat=0.345, srgf=1.0, 
                ssks=7.4, sbdm=1.66, sloc=0.67, slcl=1.7, slsi=0.9, slcf=0.0, 
                slhw=7.0
            ),
            SoilLayer(
                slb=30.0, slmh='', slll=0.075, sdul=0.12, ssat=0.345, srgf=0.7, 
                ssks=14.8, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
                slhw=7.0
            ),
            SoilLayer(
                slb=45.0, slmh='', slll=0.025, sdul=0.086, ssat=0.345, srgf=0.3, 
                ssks=3.7, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
                slhw=7.0
            ),
            SoilLayer(
                slb=60.0, slmh='', slll=0.025, sdul=0.072, ssat=0.345, srgf=0.3, 
                ssks=3.7, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
                slhw=7.0
            ),
            SoilLayer(
                slb=90.0, slmh='', slll=0.028, sdul=0.072, ssat=0.345, srgf=0.1, 
                ssks=3.7, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
                slhw=7.0
            ),
            SoilLayer(
                slb=120.0, slmh='', slll=0.028, sdul=0.08, ssat=0.345, srgf=0.1, 
                ssks=0.1, sbdm=1.66, sloc=0.18, slcl=7.7, slsi=3.1, slcf=0.0, 
                slhw=7.0,
            ),
            SoilLayer(
                slb=150.0, slmh='', slll=0.029, sdul=0.09, ssat=0.345, srgf=0.05, 
                ssks=0.1, sbdm=1.66, sloc=0.15, slcl=7.7, slsi=3.1, slcf=0.0, 
                slhw=7.0
            ),
            SoilLayer(
                slb=180.0, slmh='', slll=0.029, sdul=0.09, ssat=0.345, srgf=0.05, 
                ssks=0.1, sbdm=1.66, sloc=0.1, slcl=7.7, slsi=3.1, slcf=0.0, 
                slhw=7.0
            )
        ]
    )
    
def test_from_file_double():
    soil = SoilProfile.from_file(
        "UFBG760002",
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
    return

def test_open_all():
    from DSSATTools import __file__ as module_path
    DSSAT_MODULE_PATH = os.path.dirname(module_path)
    SOIL_PATH = os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    with open(SOIL_PATH, "r") as f:
        lines = f.readlines()
    soil_names = list(filter(lambda x: x[0] == "*", lines))
    soil_names = [name[1:11] for name in soil_names[1:]]
    for name in soil_names:
        SoilProfile.from_file(
            name,
            os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
        )

def test_profile_not_in_file():
    with pytest.raises(AssertionError) as excinfo:
        SoilProfile.from_file(
            "UFBG760323",
            os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
        )
        assert 'profile not in' in str(excinfo.value)

def test_wrong_name():
    soil = SoilProfile.from_file(
        "IBMZ910214",
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
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