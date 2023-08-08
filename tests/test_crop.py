import pytest
from DSSATTools.crop import Crop
import shutil
import os
from DSSATTools import (
    Crop, SoilProfile, Weather, 
    Management, DSSAT
    )
import pandas as pd
import numpy as np
import os
import tempfile

class TestCrop:
    def test_wrong_crop_name(self):
        with pytest.raises(AssertionError) as excinfo:
            Crop('perro')
        assert 'not a valid crop' in str(excinfo.value)

    def test_right_crop_name(self):
        Crop('MAiZe')

    def test_write(self):
        filepath = 'crop_test'
        if os.path.exists(filepath): shutil.rmtree(filepath)
        crop = Crop('MAiZe')
        crop.write(filepath)
        assert os.path.exists(os.path.join(filepath, 'MZCER048.SPE'))
        assert os.path.exists(os.path.join(filepath, 'MZCER048.ECO'))
        assert os.path.exists(os.path.join(filepath, 'MZCER048.CUL'))

    # def test_set_wrong_parameter(self):
    #     crop = Crop('maIZe')
    #     with pytest.raises(AssertionError) as excinfo:
    #         crop.set_parameter(
    #             par_name = 'TCACA',
    #             par_value = 30.,
    #             row_loc = 'IB0002'
    #         )
    #     assert 'not a valid parameter' in str(excinfo.value)

    def test_define_only_name():
        return 
    
    def test_define_new_cultivar():
        return 
    
    def test_change_parameter_name():
        return
    
    def test_crop_with_no_ecotype():
        return

    def test_set_parameter(self):
        crop = Crop('maIZe')
        filepath = 'crop_test'
        assert crop.ecotype['IB0002']['TBASE'] == 8.
        crop.set_parameter(
            par_name = 'TBASE',
            par_value = 30.,
            row_loc = 'IB0002'
        )
        assert crop.ecotype['IB0002']['TBASE'] == 30.
        crop.write(filepath)

def debug_crop():
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
    # Create a WeatherData instance
    # Create a WheaterStation instance
    wth = Weather(
        df, {"tn": "TMIN", "rad": "SRAD", "prec": "RAIN", "rh": "RHUM", "TMAX": "TMAX"},
        4.54, -75.1, 1800
    )
    Crop('maIZe', "sds")
    soil = SoilProfile(default_class='SIL')
    crop = Crop('maIZe')
    man = Management(
        planting_date=DATES[10],
    )
    man.field["...........XCRD"] = 35.32
    man.field["...........YCRD"] = -3.21
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )

if __name__ == "__main__":
    debug_crop()