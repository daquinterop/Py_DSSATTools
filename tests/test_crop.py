import pytest
from DSSATTools.crop import Crop
import shutil
import os

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

    def test_set_wrong_parameter(self):
        crop = Crop('maIZe')
        with pytest.raises(AssertionError) as excinfo:
            crop.set_parameter(
                par_name = 'TCACA',
                par_value = 30.,
                row_loc = 'IB0002'
            )
        assert 'not a valid parameter' in str(excinfo.value)

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