import pytest
from DSSATTools.base.input import Crop
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