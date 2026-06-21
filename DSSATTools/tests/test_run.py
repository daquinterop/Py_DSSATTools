"""
Each test is runs one of the experiments included in DSSAT for that crop. The 
test pass if the result is close enough to the one obtained using the desktop
version of DSSAT (v4.8.2). Close enough is an error of less than 1%.

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
| Rice         | DTSP8502   |   4   |
| Pearl Millet | ITHY8201   |   1   |
| Sugarbeet    | NDCR1401   |   1   |
| Sweetcorn    | UFCI0401   |   1   |
| Bermudagrass | SPPI1101   |   1   |
| Canola       | NOTH1201   |   3   |
| Sunflower    | TRKO1501   |   2   |
| Potato       | CPSR1302   |   1   |
| Cabbage      | IBMC9601   |   1   |
| Sugarcane    | ESAL1401   |   1   |
| Cassava      | CCPA7801   |   1   |
| Cotton       | GACM0401   |   1   |
| Fallow       | GAGR0401FA |   1   |
"""
import pytest

from DSSATTools.crop import (
    Maize, Sorghum, Wheat, Tomato, Alfalfa, Fallow, DryBean
)
from DSSATTools.soil import SoilProfile
from DSSATTools.filex import (
    read_filex, Field, InitialConditions, Planting, Fertilizer, 
    FertilizerEvent, SimulationControls, SCGeneral, SCManagement,
    SCMethods, SCOptions, Mow, Harvest, Irrigation, IrrigationEvent,
    Tillage, TillageEvent, SCOutputs, SoilAnalysis
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
    soil = SoilProfile.from_file(
        'IBSG910085', 
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
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
    soil = SoilProfile.from_file(
        "IBWH980018", 
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
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
    soil = SoilProfile.from_file(
        "UFBR950001", 
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
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
    soil = SoilProfile.from_file(
        "IBSB910032", 
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
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
    mow = Mow.from_file(os.path.join(DATA_PATH, 'Alfalfa', 'AGZG1501.MOW'))[1]
    soil = SoilProfile.from_file(
        "AGSP209115", 
        os.path.join(DATA_PATH, 'Soil', "AG.SOL")
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
        skiprows=1, widths=[4, 6, 6, 5, 5, 5, 4] + [6]*14
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
    soil = SoilProfile.from_file(
        "IBBN910030", 
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
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
    soil = SoilProfile.from_file(
        "IBRI910024", 
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
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

def test_pearlMillet():
    """
    Experiment ITHY8201, Treatment 1
    """
    soil = SoilProfile.from_file(
        "IBML910083", 
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "ITHY8201.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'PearlMillet', "ITHY8201.MLX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=treatment['Cultivar'].crop, 
        initial_conditions=treatment['InitialConditions'],
        planting=treatment["Planting"],
        fertilizer=treatment['Fertilizer'],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(4714, results['harwt'], rtol=0.01)
    dssat.close()

def test_sugarbeet():
    """
    Experiment NDCR1401, Treatment 1
    """
    soil = SoilProfile.from_file(
        "CREC002014", 
        os.path.join(DATA_PATH, 'Soil', 'CR.SOL')
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "CRND1401.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Sugarbeet', "NDCR1401.BSX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=treatment['Cultivar'].crop, 
        planting=treatment["Planting"],
        harvest=treatment["Harvest"],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(18572, results['harwt'], rtol=0.01)
    dssat.close()

def test_sweetCorn():
    """
    Experiment UFCI0401, Treatment 1
    """
    soil = SoilProfile.from_file(
        "IBMZ910214", 
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "UFCI0401.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'SweetCorn', "UFCI0401.SWX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        cultivar=treatment['Cultivar'].crop, 
        field=treatment["Field"],
        initial_conditions=treatment['InitialConditions'], 
        planting=treatment["Planting"],
        irrigation=treatment["Irrigation"],
        fertilizer=treatment["Fertilizer"],
        harvest=treatment["Harvest"],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(3409, results['harwt'], rtol=0.01)
    dssat.close()

def test_bermudagrass():
    """
    Experiment SPPI1101, Treatment 1
    """
    soil = SoilProfile.from_file(
        "EBPI080100", 
        os.path.join(DATA_PATH, 'Soil', 'EB.SOL')
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "SPPI1101.WTH"),
        os.path.join(DATA_PATH, 'Weather', "SPPI1201.WTH"),
        os.path.join(DATA_PATH, 'Weather', "SPPI1301.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Bermudagrass', "SPPI1101.BMX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 
    mow = Mow.from_file(os.path.join(DATA_PATH, 'Bermudagrass', "SPPI1101.MOW"))[1]
    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        cultivar=treatment['Cultivar'].crop, 
        field=treatment["Field"],
        initial_conditions=treatment['InitialConditions'], 
        planting=treatment["Planting"],
        irrigation=treatment["Irrigation"],
        fertilizer=treatment["Fertilizer"],
        harvest=treatment["Harvest"],
        simulation_controls=treatment["SimulationControls"],
        mow=mow
    )
    # Open FORAGE.out
    forage = pd.read_fwf(
        StringIO(dssat.output_files['FORAGE']),
        skiprows=1, widths=[5, 9, 3] + [5]*18
    )
    dssat_gui_values = [
        0, 1348, 2438, 1844, 1509, 1135, 619, 1260, 1150, 1481, 1890, 1907, 
        2047, 2273, 1684, 2078, 2178, 1100, 1321, 604, 884, 1003, 1581, 2022, 
        2174, 2538, 2360, 2028, 2276, 1664
    ]
    assert all([
        np.isclose(gui, i, rtol=0.01) 
        for gui, i in zip(dssat_gui_values, forage.FHWAH)
    ])
    dssat.close()

def test_canola():
    """
    Experiment NOTH1201, Treatment 3
    """
    soil = SoilProfile.from_file(
        "NOTH030003", 
        os.path.join(DATA_PATH, 'Soil', 'NO.SOL')
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "NOTH1201.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Canola', "NOTH1201.CNX"))
    treatment = treatments[3]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        cultivar=treatment['Cultivar'].crop, 
        field=treatment["Field"],
        soil_analysis=treatment["SoilAnalysis"],
        initial_conditions=treatment['InitialConditions'], 
        planting=treatment["Planting"],
        fertilizer=treatment["Fertilizer"],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(2498, results['harwt'], rtol=0.01)
    dssat.close()

def test_sunflower():
    """
    Experiment TRKO1501, Treatment 2
    """
    soil = SoilProfile.from_file(
        "TRKON20150", 
        os.path.join(DATA_PATH, 'Soil', 'TR.SOL')
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "TRKO1501.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Sunflower', "TRKO1501.SUX"))
    treatment = treatments[2]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        cultivar=treatment['Cultivar'].crop, 
        field=treatment["Field"],
        initial_conditions=treatment['InitialConditions'], 
        planting=treatment["Planting"],
        irrigation=treatment['Irrigation'],
        fertilizer=treatment["Fertilizer"],
        harvest=treatment['Harvest'],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(4116, results['harwt'], rtol=0.01)
    dssat.close()

def test_potato():
    """
    Experiment CPSR1302, Treatment 1
    """
    soil = SoilProfile.from_file(
        "CPSR000022",
        os.path.join(DATA_PATH, 'Soil', 'CP.SOL')
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "CPSR1301.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Potato', "CPSR1302.PTX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        cultivar=treatment['Cultivar'].crop, 
        field=treatment["Field"],
        soil_analysis=treatment["SoilAnalysis"],
        initial_conditions=treatment['InitialConditions'], 
        planting=treatment["Planting"],
        irrigation=treatment['Irrigation'],
        fertilizer=treatment["Fertilizer"],
        harvest=treatment['Harvest'],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(2146, results['harwt'], rtol=0.01)
    dssat.close()

def test_cabbage():
    """
    Experiment IBMC9601, Treatment 1
    """
    soil = SoilProfile.from_file(
        "IB00720001", 
        os.path.join(DATA_PATH, 'Soil', 'SOIL.SOL')
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "IBMC9601.WTH"),
        os.path.join(DATA_PATH, 'Weather', "IBMC9701.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Cabbage', "IBMC9601.CBX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        cultivar=treatment['Cultivar'].crop, 
        field=treatment["Field"],
        initial_conditions=treatment['InitialConditions'], 
        planting=treatment["Planting"],
        irrigation=treatment['Irrigation'],
        fertilizer=treatment["Fertilizer"],
        harvest=treatment['Harvest'],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(178, results['harwt'], rtol=0.01)
    dssat.close()

def test_sugarcane():
    """
    Experiment ESAL1401, Treatment 1
    """
    soil = SoilProfile.from_file(
        "BRPI020003", 
        os.path.join(DATA_PATH, 'Soil', 'BR.SOL')
    )
    df = []
    for year in range(14, 16):
        df.append(pd.read_fwf(
            os.path.join(DATA_PATH, 'Weather', f'SPFA{year}01.WTH'),
            skiprows=4, colspecs=[(6*i, 6*i+5) for i in range(10)]
        ))
    df = pd.concat(df, ignore_index=True)
    df.columns = ['date', 'srad', 'tmax', 'tmin', 'rain', 'dewp', 
                  'wind', 'par', 'evap', 'rhum']
    df["date"] = pd.to_datetime(df.date, format='%y%j')
    weather_station = WeatherStation(
        lat=-22.7017, long=-47.6423, elev=547, tav=21.5, amp=7.1, refht=2., 
        wndht=2., table=df
    )
    treatments = read_filex(os.path.join(DATA_PATH, 'Sugarcane', "ESAL1401.SCX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        cultivar=treatment['Cultivar'].crop, 
        field=treatment["Field"],
        initial_conditions=treatment['InitialConditions'], 
        planting=treatment["Planting"],
        irrigation=treatment['Irrigation'],
        harvest=treatment['Harvest'],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(15748, results['harwt'], rtol=0.01)
    dssat.close()

def test_cassava():
    """
    Experiment CCPA7801, Treatment 1
    """
    soil = SoilProfile.from_file(
        "CCPA000030",
        os.path.join(DATA_PATH, 'Soil', 'SOIL.SOL')
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "CCPA7801.WTH"),
        os.path.join(DATA_PATH, 'Weather', "CCPA7901.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Cassava', "CCPA7801.CSX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        cultivar=treatment['Cultivar'].crop, 
        field=treatment["Field"],
        initial_conditions=treatment['InitialConditions'], 
        planting=treatment["Planting"],
        irrigation=treatment['Irrigation'],
        harvest=treatment['Harvest'],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(11711, results['harwt'], rtol=0.01)
    dssat.close()

def test_freeze_soya():
    """
    Experiment CLMO8501, treatment 1. The weather data is modified to induce
    freezing conditions. Created to work on the Issue 60. 
    """
    soil = SoilProfile.from_file(
        "IBSB910032", 
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "CLMO8501.WTH"),
    ])
    
    df = weather_station.to_dataframe()
    kwargs = weather_station._Record__data
    for i in range(100, 110): df.loc[i, 'tmin'] = -3.
    kwargs['table'] = df
    weather_station = WeatherStation(**kwargs)
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
    assert 'Freeze occurred' in dssat.stdout
    dssat.close()

def test_cotton():
    """
    Experiment GACM0401, Treatment 1
    """
    soil = SoilProfile.from_file(
        "GAPL850009", 
        os.path.join(DATA_PATH, 'Soil', 'GA.SOL')
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "GACM9824.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Cotton', "GACM0401.COX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    results = dssat.run_treatment(
        cultivar=treatment['Cultivar'].crop, 
        field=treatment["Field"],
        initial_conditions=treatment['InitialConditions'], 
        planting=treatment["Planting"],
        fertilizer=treatment["Fertilizer"],
        simulation_controls=treatment["SimulationControls"]
    )
    assert np.isclose(4647, results['harwt'], rtol=0.01)
    dssat.close()

def test_fallow():
    """
    Experiment GAGR0401FA, Treatment 1
    """
    cultivar = Fallow("IB0001")
    soil = SoilProfile.from_file(
        "GA00620001",
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "GAGR9626.WTH"),
    ])
    treatments = read_filex(os.path.join(DATA_PATH, 'Fallow', "GAGR0401.FAX"))
    treatment = treatments[1]
    treatment["Field"]["wsta"] = weather_station
    treatment["Field"]["id_soil"] = soil 

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    planting = treatment.get("Planting", Planting(
        pdate=date(2004, 1, 1), ppop=1, ppoe=1, plme='S',
        plds='R', plrs=50, plrd=0, pldp=5
    ))
    results = dssat.run_treatment(
        field=treatment["Field"], 
        cultivar=cultivar, 
        planting=planting,
        harvest=treatment.get("Harvest"),
        initial_conditions=treatment["InitialConditions"],
        simulation_controls=treatment["SimulationControls"]
    )
    soilwat = dssat.output_tables['SoilWat']
    # Evaluate the water content in the first layer at the last 4 days
    assert all(np.isclose(soilwat['SW1D'].iloc[-4:].values, [.088, .071, .07, .069]))
    dssat.close()

def test_sequence():
    """
    Sequence experiment QUKY1101, Wheat-Fallow-Maize sequence
    """
    cultivar_wh = Wheat("990015")
    cultivar_fa = Fallow("IB0001")
    cultivar_mz = Maize("IB0200")
    
    soil = SoilProfile.from_file(
        "QUKI100004",
        os.path.join(DATA_PATH, "Soil", "QU.SOL")
    )
    
    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "QDKY1101.WTH"),
        os.path.join(DATA_PATH, 'Weather', "QDKY1201.WTH"),
    ])
    
    field = Field(
        id_field='KYQD0001', wsta=weather_station, flob=0, fldt='DR000', 
        fldd=105, flds=0, id_soil=soil
    )
    
    initial_conditions = InitialConditions(
        pcr='BN', icdat=date(2011, 6, 8), icrt=700, icnd=-99, icrn=1, icre=1,
        icwd=-99, icres=1320, icren=1.5, icrep=-99, icrip=-99, icrid=-99,
        table=pd.DataFrame([
            (5, 0.35, 3, 4),
            (10, 0.35, 3, 5),
            (20, 0.35, 6, 9),
            (30, 0.35, 6, 4),
            (40, 0.4, 3, 3),
            (50, 0.4, 2, 1),
            (60, 0.4, 1, 1),
            (70, 0.4, 1, 1),
            (80, 0.4, 1, 1),
            (90, 0.4, 1, 1),
        ], columns=['icbl', 'sh2o', 'snh4', 'sno3'])
    )
    
    planting_wh = Planting(
        pdate=date(2011, 7, 6), ppop=125, ppoe=125, plme='S',
        plds='R', plrs=25, plrd=0, pldp=5
    )
    
    tillage_wh = Tillage(table=[
        TillageEvent(tdate=date(2011, 6, 8), timpl='TI005', tdep=20),
        TillageEvent(tdate=date(2011, 6, 10), timpl='TI010', tdep=20),
        TillageEvent(tdate=date(2011, 6, 20), timpl='TI033', tdep=15),
    ])
    
    irrigation_wh = Irrigation(
        efir=1, idep=30, ithr=50, iept=100, ioff='GS000', iame='IR001', iamt=10,
        table=[
            IrrigationEvent(idate=date(2011, 8, 11), irop='IR004', irval=40),
            IrrigationEvent(idate=date(2011, 9, 15), irop='IR004', irval=21),
            IrrigationEvent(idate=date(2011, 9, 27), irop='IR004', irval=30),
            IrrigationEvent(idate=date(2011, 10, 5), irop='IR004', irval=45),
        ]
    )
    
    harvest_wh = Harvest(
        hdate=date(2011, 11, 29), hstg='GS000', hcom='-99', hsize='-99', hpc=100, hbpc=0
    )
    
    sc_outputs = SCOutputs(
        fname='Y', ovvew='Y', sumry='Y', fropt=1, grout='Y', caout='Y',
        waout='Y', niout='Y', miout='Y', diout='N', vbose='D', chout='Y',
        opout='Y', fmopt='A'
    )

    sim_controls_wh = SimulationControls(
        general=SCGeneral(sdate=date(2011, 6, 8), sname="CONV"),
        options=SCOptions(water='Y', nitro='Y', symbi='N'),
        methods=SCMethods(evapo='R', photo='C', infil='S', mesev='S', mesol='3', meghg='1'),
        management=SCManagement(irrig='R', ferti='R', resid='N', harvs='R'),
        outputs=sc_outputs
    )
    
    planting_fa = Planting(
        pdate=date(2011, 11, 30), ppop=125, ppoe=125, plme='S',
        plds='R', plrs=25, plrd=0, pldp=5
    )
    
    harvest_fa = Harvest(
        hdate=date(2011, 12, 14), hstg='GS000', hcom='-99', hsize='-99', hpc=0, hbpc=0
    )
    
    sim_controls_fa = SimulationControls(
        general=SCGeneral(sdate=date(2011, 6, 8), sname="CONV"),
        options=SCOptions(water='Y', nitro='Y', symbi='N'),
        methods=SCMethods(evapo='F', photo='L', infil='S', mesev='S', mesol='3', meghg='1'),
        management=SCManagement(irrig='R', ferti='R', resid='N', harvs='R'),
        outputs=sc_outputs
    )
    
    planting_mz = Planting(
        pdate=date(2011, 12, 15), ppop=5, ppoe=5, plme='S',
        plds='R', plrs=93, plrd=0, pldp=5
    )
    
    tillage_mz = Tillage(table=[
        TillageEvent(tdate=date(2011, 12, 1), timpl='TI005', tdep=20),
        TillageEvent(tdate=date(2011, 12, 5), timpl='TI010', tdep=20),
        TillageEvent(tdate=date(2011, 12, 10), timpl='TI033', tdep=15),
    ])
    
    fertilizer_mz = Fertilizer(table=[
        FertilizerEvent(fdate=date(2011, 12, 21), fmcd='FE007', fdep=3, famn=40, facd='AP002')
    ])
    
    irrigation_mz = Irrigation(
        efir=1, idep=30, ithr=50, iept=100, ioff='GS000', iame='IR001', iamt=10,
        table=[
            IrrigationEvent(idate=date(2012, 1, 5), irop='IR004', irval=26),
            IrrigationEvent(idate=date(2012, 1, 23), irop='IR004', irval=40),
        ]
    )
    
    harvest_mz = Harvest(
        hdate=date(2012, 6, 20), hstg='GS000', hcom='-99', hsize='-99', hpc=100, hbpc=0
    )
    
    sim_controls_mz = SimulationControls(
        general=SCGeneral(sdate=date(2011, 6, 8), sname="CONV"),
        options=SCOptions(water='Y', nitro='Y', symbi='N'),
        methods=SCMethods(evapo='F', photo='L', infil='S', mesev='S', mesol='3', meghg='1'),
        management=SCManagement(irrig='R', ferti='R', resid='N', harvs='R'),
        outputs=sc_outputs
    )
    
    soil_analysis = SoilAnalysis(
        sadat=date(2011, 6, 9),
        table=pd.DataFrame([
            (5, 1.8, 1.2),
            (10, 1.5, 1.1),
            (20, 1.4, 1.3),
            (30, 1.1, 1.0),
            (40, 0.9, 0.7),
            (50, 0.2, 0.1),
            (60, 0.1, -99),
            (70, 0.1, -99),
            (80, 0.1, -99),
            (90, 0.1, -99),
        ], columns=['sabl', 'saoc', 'sasc'])
    )
    
    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    summary = dssat.run_sequence(
        field=field,
        initial_conditions=initial_conditions,
        sequence=[
            {
                "cultivar": cultivar_wh, "planting": planting_wh,
                "tillage": tillage_wh, "irrigation": irrigation_wh,
                "harvest": harvest_wh, "simulation_controls": sim_controls_wh,
                "soil_analysis": soil_analysis
            },
            {
                "cultivar": cultivar_fa, "planting": planting_fa,
                "harvest": harvest_fa, "simulation_controls": sim_controls_fa
            },
            {
                "cultivar": cultivar_mz, "planting": planting_mz,
                "tillage": tillage_mz, "fertilizer": fertilizer_mz,
                "irrigation": irrigation_mz, "harvest": harvest_mz,
                "simulation_controls": sim_controls_mz
            }
        ]
    )
    
    # Verify summary results
    # Index 0 is Wheat, Index 2 is Maize
    assert np.isclose(3922, summary.loc[0, 'HWAM'], rtol=0.01)
    assert np.isclose(3153, summary.loc[2, 'HWAM'], rtol=0.01)
    dssat.close()

def test_maize_bean_maize_sequence():
    """
    Maize - DryBean - Maize sequence at CCPA site (Palmira, Colombia).

    Verifies that run_sequence works correctly when crops from different
    model families (MZCER for Maize, CRGRO for DryBean) are combined in
    the same rotation, ensuring the smodel switch in the config file and
    the cultivar/ecotype file generation are both handled correctly.
    """
    cultivar_mz = Maize("IB0171")
    cultivar_bn = DryBean("IB0001")

    soil = SoilProfile.from_file(
        "IBBN910030",
        os.path.join(DATA_PATH, "Soil", "SOIL.SOL")
    )

    weather_station = WeatherStation.from_files([
        os.path.join(DATA_PATH, 'Weather', "CCPA8601.WTH"),
        os.path.join(DATA_PATH, 'Weather', "CCPA8701.WTH"),
        os.path.join(DATA_PATH, 'Weather', "CCPA8801.WTH"),
    ])

    field = Field(
        id_field='CCPA0001', wsta=weather_station, flob=0, fldt='DR000',
        fldd=0, flds=0, id_soil=soil
    )

    initial_conditions = InitialConditions(
        pcr='MZ', icdat=date(1986, 9, 1), icrt=700, icnd=-99, icrn=1, icre=1,
        icwd=-99, icres=1000, icren=1.0, icrep=-99, icrip=-99, icrid=-99,
        table=pd.DataFrame([
            (5, 0.34, 2, 15),
            (15, 0.34, 2, 15),
            (25, 0.345, 2, 15),
            (35, 0.345, 2, 15),
            (50, 0.335, 2, 15),
            (65, 0.323, 1, 4),
            (80, 0.323, 1, 4),
            (99, 0.328, 7, 4),
        ], columns=['icbl', 'sh2o', 'snh4', 'sno3'])
    )

    sc_outputs = SCOutputs(
        fname='Y', ovvew='Y', sumry='Y', fropt=1, grout='Y', caout='Y',
        waout='Y', niout='Y', miout='Y', diout='N', vbose='D', chout='Y',
        opout='Y', fmopt='A'
    )

    # --- Maize 1 (Sep 1986 - Jan 1987) ---
    planting_mz1 = Planting(
        pdate=date(1986, 9, 15), ppop=5, ppoe=5, plme='S',
        plds='R', plrs=75, plrd=0, pldp=5
    )
    fertilizer_mz1 = Fertilizer(table=[
        FertilizerEvent(fdate=date(1986, 9, 25), fmcd='FE007', fdep=5,
                        famn=80, facd='AP002')
    ])
    harvest_mz1 = Harvest(
        hdate=date(1987, 1, 31), hstg='GS000', hcom='-99', hsize='-99',
        hpc=100, hbpc=0
    )
    sim_controls_mz1 = SimulationControls(
        general=SCGeneral(sdate=date(1986, 9, 1)),
        options=SCOptions(water='Y', nitro='Y', symbi='N'),
        methods=SCMethods(infil='S', mesol='3'),
        management=SCManagement(irrig='N', ferti='R', resid='N', harvs='R'),
        outputs=sc_outputs
    )

    # --- DryBean (Feb 1987 - May 1987) ---
    planting_bn = Planting(
        pdate=date(1987, 2, 15), ppop=15, ppoe=15, plme='S',
        plds='R', plrs=30, plrd=0, pldp=2
    )
    harvest_bn = Harvest(
        hdate=date(1987, 5, 31), hstg='GS000', hcom='-99', hsize='-99',
        hpc=100, hbpc=0
    )
    sim_controls_bn = SimulationControls(
        general=SCGeneral(sdate=date(1986, 9, 1)),
        options=SCOptions(water='Y', nitro='Y', symbi='N'),
        methods=SCMethods(infil='S', mesol='3'),
        management=SCManagement(irrig='N', ferti='N', resid='N', harvs='R'),
        outputs=sc_outputs
    )

    # --- Maize 2 (Sep 1987 - Jan 1988) ---
    planting_mz2 = Planting(
        pdate=date(1987, 9, 15), ppop=5, ppoe=5, plme='S',
        plds='R', plrs=75, plrd=0, pldp=5
    )
    fertilizer_mz2 = Fertilizer(table=[
        FertilizerEvent(fdate=date(1987, 9, 25), fmcd='FE007', fdep=5,
                        famn=80, facd='AP002')
    ])
    harvest_mz2 = Harvest(
        hdate=date(1988, 1, 31), hstg='GS000', hcom='-99', hsize='-99',
        hpc=100, hbpc=0
    )
    sim_controls_mz2 = SimulationControls(
        general=SCGeneral(sdate=date(1986, 9, 1)),
        options=SCOptions(water='Y', nitro='Y', symbi='N'),
        methods=SCMethods(infil='S', mesol='3'),
        management=SCManagement(irrig='N', ferti='R', resid='N', harvs='R'),
        outputs=sc_outputs
    )

    dssat = DSSAT(os.path.join(TMP, 'dssat_test'))
    summary = dssat.run_sequence(
        field=field,
        initial_conditions=initial_conditions,
        sequence=[
            {
                "cultivar": cultivar_mz, "planting": planting_mz1,
                "fertilizer": fertilizer_mz1, "harvest": harvest_mz1,
                "simulation_controls": sim_controls_mz1
            },
            {
                "cultivar": cultivar_bn, "planting": planting_bn,
                "harvest": harvest_bn, "simulation_controls": sim_controls_bn
            },
            {
                "cultivar": cultivar_mz, "planting": planting_mz2,
                "fertilizer": fertilizer_mz2, "harvest": harvest_mz2,
                "simulation_controls": sim_controls_mz2
            }
        ]
    )

    # Verify all three crops completed (non-zero harvest weight) and
    # that the DryBean step (index 1) also produced a positive yield,
    # confirming the model switch between MZCER and CRGRO worked.
    assert summary.loc[0, 'HWAM'] > 0, "Maize 1 should produce a positive yield"
    assert summary.loc[1, 'HWAM'] > 0, "DryBean should produce a positive yield"
    assert summary.loc[2, 'HWAM'] > 0, "Maize 2 should produce a positive yield"
    dssat.close()

if __name__ == "__main__":
    test_fallow()