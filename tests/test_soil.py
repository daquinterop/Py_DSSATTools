from pickletools import pybytes
import pytest
from DSSATTools import soil
import numpy as np
import os
import platform

if 'windows' in platform.system().lower():
    BASE_PATH = 'C:/Users/daqui/'
else:
    BASE_PATH='/home/diego'

class TestSoilLayer:
    def test_no_texture_no_hydpars(self):
        with pytest.raises(AssertionError):
            soil.SoilLayer(100, {'SLCF': 34})

    def test_no_texture_hydpars(self):
        layer = soil.SoilLayer(100, {
            key: 0 for key in ['SLLL', 'SDUL', 'SSAT', 'SRGF', 'SSKS', 'SBDM', 'SLOC']
        })
        assert layer['SLLL'] == 0

    def test_texture_no_hydpars(self):
        layer = soil.SoilLayer(100, {'SLSI': 34, 'SLCL': 10})
        assert ((layer['SLSI'] == 34) and (layer['SLCL'] == 10))

    def test_wrong_color(self):
        with pytest.raises(AssertionError):
            soil.SoilLayer(100, {'SCOM': 'orange', 'SLCL': 30, 'SLSI': 20})
    
    def test_right_color(self):
        layer = soil.SoilLayer(100, {'SCOM': 'BLK', 'SLCL': 30, 'SLSI': 20})
        assert layer.SLOC >= 0

    def test_layer_example(self):
        layer = soil.SoilLayer(
            base_depth=100, # Soil base depth (cm)
            pars= # layer parameter's dict
            {
                'SLOC': 1.75, # Soil Organic Carbon %
                'SLCL': 50, # Clay %
                'SLSI': 45 # Silt %
            } 
        )

class TestSoilProfile:       
    def remove_outs(self):
        try:
            os.remove('/tmp/soil.SOL')
        except:
            pass
    def test_initialize_file(self):
        soilprofile = soil.SoilProfile(
            file=os.path.join(BASE_PATH, 'dssat-csm-data', 'Soil', 'SOIL.SOL'),
            profile='IBBN910030'
        )
        assert np.isclose(soilprofile.layers[65].SLLL, 0.185, .05)

    def test_initialize_and_add_layers(self):
        soilprofile = soil.SoilProfile(
            pars={
                'SALB': 0.25, # Albedo
                'SLU1': 6, # Stage 1 Evaporation (mm)
                'SLPF': 0.8 # Soil fertility factor
            }
        )
        layers = [
            soil.SoilLayer(20, {'SLCL': 50, 'SLSI': 45}),
            soil.SoilLayer(50, {'SLCL': 30, 'SLSI': 30}),
            soil.SoilLayer(100, {'SLCL': 30, 'SLSI': 35}),
            soil.SoilLayer(180, {'SLCL': 20, 'SLSI': 30})
        ]
        for layer in layers: soilprofile.add_layer(layer)
        assert np.isclose(soilprofile.layers[50].SSAT, 0.42, .2)

    def test_initialize_default_soil(self):
        soilprofile = soil.SoilProfile(default_class='LS')
        assert np.isclose(soilprofile.layers[71].SSAT, 0.350)

    def test_write_from_file(self):
        self.remove_outs()
        soilprofile = soil.SoilProfile(
            file=os.path.join(BASE_PATH, 'dssat-csm-data', 'Soil', 'SOIL.SOL'),
            profile='IBBN910030'
        )
        soilprofile.write(os.path.join(BASE_PATH, 'dssat-csm-data', 'soil.SOL'))
        assert os.path.exists(os.path.join(BASE_PATH, 'dssat-csm-data', 'soil.SOL'))

    def test_write_from_custom(self):
        self.remove_outs()
        soilprofile = soil.SoilProfile(default_class='LS')
        soilprofile.write(os.path.join(BASE_PATH, 'dssat-csm-data', 'Soil', 'sosol.SOL'))
        assert os.path.exists(os.path.join(BASE_PATH, 'dssat-csm-data', 'Soil', 'sosol.SOL'))

    def test_write_from_scratch(self):
        self.remove_outs()
        soilprofile = soil.SoilProfile(
            pars={
                'SALB': 0.25, # Albedo
                'SLU1': 6, # Stage 1 Evaporation (mm)
                'SLPF': 0.8 # Soil fertility factor
            }
        )
        layers = [
            soil.SoilLayer(20, {'SLCL': 50, 'SLSI': 45}),
            soil.SoilLayer(50, {'SLCL': 30, 'SLSI': 30}),
            soil.SoilLayer(100, {'SLCL': 30, 'SLSI': 35}),
            soil.SoilLayer(180, {'SLCL': 20, 'SLSI': 30})
        ]
        for layer in layers: soilprofile.add_layer(layer)
        soilprofile.write(os.path.join(BASE_PATH, 'dssat-csm-data', 'Soil', 'sosol.SOL'))
        assert os.path.exists(os.path.join(BASE_PATH, 'dssat-csm-data', 'Soil', 'sosol.SOL'))

    def test_no_layers(self):
        soilprofile = soil.SoilProfile(
            pars={
                'SALB': 0.25, # Albedo
                'SLU1': 6, # Stage 1 Evaporation (mm)
                'SLPF': 0.8 # Soil fertility factor
            }
        )
        with pytest.raises(AssertionError):
            soilprofile.write()

    def test_pars_assignment(self):
        soilprofile = soil.SoilProfile(
            pars={
                'SALB': 0.25, # Albedo
                'SLU1': 6, # Stage 1 Evaporation (mm)
                'SLPF': 0.8 # Soil fertility factor
            }
        )
        soilprofile.SLRO = 48
        assert (soilprofile.SALB, soilprofile.SLRO) == (.25, 48)

    def test_wrong_parameter(self):
        with pytest.raises(AssertionError):
            soilprofile = soil.SoilProfile(
            pars={
                    'SALB': 0.25, # Albedo
                    'SLU1': 6, # Stage 1 Evaporation (mm)
                    'Perro': 0.8 # Soil perrility factor
                }
            )

    def test_wrong_default(self):
        with pytest.raises(AssertionError):
            soil.SoilProfile(default_class='perro')

    def test_wrong_profile_id(self):
        with pytest.raises(AssertionError):
            soilprofile = soil.SoilProfile(
                file=os.path.join(BASE_PATH, 'dssat-csm-data', 'Soil', 'SOIL.SOL'),
                profile='sisisperro'
            )