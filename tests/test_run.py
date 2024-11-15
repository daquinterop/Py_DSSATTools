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
| Millet       | Pending
| Sugarbeet    | Pending
| Rice         | Pending
| Sweetcorn    | Pending
| Alfalfa      | Pending
| Bermudagrass | Pending
| Canola       | Pending
| Sunflower    | Pending
| Potato       | Pending
| Cabbage      | Pending
| Sugarcane    | Pending
"""
import pytest

from DSSATTools import (
    Crop, SoilProfile, Weather,
    Management, DSSAT
    )
from DSSATTools.base.sections import TabularSubsection
from datetime import datetime
import pandas as pd
import numpy as np
import os
import tempfile

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
# Create a WheaterStation instance
wth =  Weather(
        df, {"tn": "TMIN", "rad": "SRAD", "prec": "RAIN", "rh": "RHUM", "TMAX": "TMAX"},
        4.54, -75.1, 1800
    )

soil = SoilProfile(default_class='SIL')

def test_no_setup():
    with pytest.raises(AssertionError) as excinfo:
        assert 'setup() method' in str(excinfo.value)

def test_run_maize():
    """
    Experiment BRPI0202, treatment 1
    """
    crop = Crop('maize', "IB0171")
    soil = SoilProfile("tests/input_files/BR.SOL", "BRPI020001")
    ### Build weather from existing weather files
    df = pd.read_csv(f"tests/input_files/BRPI0201.WTH", skiprows=4, sep="\s+")
    df.index = pd.to_datetime("0"+df["@DATE"].astype(str), format="%y%j")
    wth =  Weather(
        df, {"TMIN": "TMIN", "SRAD": "SRAD", "RAIN": "RAIN", "TMAX": "TMAX"},
        lat=-22.43, lon=-47.25, elev=580, tav=21.6, amp=7.2, wndht=2.
    )
    ### Define management
    man = Management(
        planting_date=datetime.strptime("02072", "%y%j"),
    )
    # Field attributes according to experiment file
    man.field["...........XCRD"] = 0
    man.field["...........YCRD"] = 0
    man.field[".....ELEV"] = 0
    # *INITIAL CONDITIONS 
    # @C   PCR ICDAT  ICRT  ICND  ICRN  ICRE  ICWD ICRES ICREN ICREP ICRIP ICRID ICNAME
    # 1    MZ 02060   -99   -99     1     1   -99  5100   1.5   -99   100    15 rainfed
    # @C  ICBL  SH2O  SNH4  SNO3
    # 1    20   .25    .4   3.9
    # 1    40   .25    .4   3.9
    # 1   120   .26    .4   3.9
    pars = {
        "PCR": "MZ", "ICDAT": "02060", "ICRN": 1, "ICRE": 1, "ICRES": 5100, 
        "ICREN": 1.5, "ICRIP": 100, "ICRID": 15,
    }
    for key, val in pars.items(): man.initial_conditions[key] = val
    man.initial_conditions["table"] = TabularSubsection(pd.DataFrame(
        [(  20,  .25, .4, 3.9),
         (  40,  .25, .4, 3.9),
         (  120, .26, .4, 3.9),],
        columns=["ICBL", "SH2O", "SNH4", "SNO3"]
    ))
    # *PLANTING DETAILS
    # @P PDATE EDATE  PPOP  PPOE  PLME  PLDS  PLRS  PLRD  PLDP  PLWT  PAGE  PENV  PLPH  SPRL                        PLNAME
    #  1 02072 02078     7     5     S     R    80    45     5   -99   -99   -99   -99     0                        -99
    pars = {
        "EDATE": "02078", "PPOP": 7, "PPOE": 5, "PLME": "S", "PLDS": "R", 
        "PLRS": 80, "PLRD": 45, "PLDP": 5
    }
    for key, val in pars.items(): man.planting_details[key] = val
    # *FERTILIZERS (INORGANIC)
    # @F FDATE  FMCD  FACD  FDEP  FAMN  FAMP  FAMK  FAMC  FAMO  FOCD FERNAME
    #  1 02072 FE027 AP001     5    20   -99   -99   -99   -99   -99 -99
    #  1 02093 FE005 AP003     0    50     0     0     0     0   -99 -99
    man.fertilizers["table"].loc[0] = (
        "02072", "FE027", "AP001", 5, 20, None, None, None, None, None, None
    )
    man.fertilizers["table"].loc[1] = (
        "02093", "FE005", "AP003", 0, 50, 0, 0, 0, 0, None, None
    )
    # *SIMULATION CONTROLS
    # @N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL
    #  1 GE              1     1     S 02060  2150 2002 Maize Experiment Ir
    # @N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2
    #  1 OP              Y     Y     N     N     N     N     N     Y     M
    # @N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL
    #  1 ME              M     M     E     R     S     R     R     1     G     S     2
    # @N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS
    #  1 MA              R     R     R     N     M
    # @N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT FMOPT
    #  1 OU              N     Y     Y     1     Y     Y     Y     Y     N     N     Y     N     N     A
    pars = {
        "SDATE": "02060", "RSEED": 2150,
        "WATER": "Y", "NITRO": "Y", "CO2": "M", "WTHER": "M", "INCON": "M",
        "LIGHT": "E", "EVAPO": "R", "INFIL": "S", "PHOTO": "R", "HYDRO": "R",
        "NSWIT": 1, "MESOM": "G", "MESEV": "S", "MESOL": 2, "PLANT": "R",
        "IRRIG": "R", "FERTI": "R", "RESID": "N", "HARVS": "M", 
    }
    for key, val in pars.items(): man.simulation_controls[key] = val
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'dssat_test'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    harwt = int(dssat.stdout.split("\n")[-1].split()[6])
    assert np.isclose(3676, harwt, rtol=0.01)
    dssat.close()

def test_run_millet():
    soil = SoilProfile(default_class='SIL')
    crop = Crop('millet')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_sugarbeet():
    crop = Crop('sugarbeet')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_rice():
    crop = Crop('rice')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_sorghum():
    """
    Experiment ITHY8001, treatment 2
    """
    crop = Crop('sorghum', "IB0026")
    soil = SoilProfile("tests/input_files/SOIL.SOL", "IBSG910085")
    ### Build weather from existing weather files
    df = pd.DataFrame()
    for year in range(80, 82):
        df = pd.concat(
            [df, pd.read_csv(f"tests/input_files/ITHY{year}01.WTH", skiprows=3, sep="\s+")], 
            ignore_index=True
        )
    df.index = pd.to_datetime(df["@DATE"].astype(str), format="%y%j")
    wth =  Weather(
        df, {"TMIN": "TMIN", "SRAD": "SRAD", "RAIN": "RAIN", "TMAX": "TMAX"},
        lat=17.530, lon=78.270, elev=0, tav=25.8, amp=11.8, refht=2., wndht=3.
    )
    ### Define management
    man = Management(
        planting_date=datetime.strptime("80169", "%y%j"),
    )
    # @C   PCR ICDAT  ICRT  ICND  ICRN  ICRE  ICWD ICRES ICREN ICREP ICRIP ICRID ICNAME
    #  2    SG 80165   500     0     1     1   -99  1300    .5     0   100    10 -99
    # @C  ICBL  SH2O  SNH4  SNO3
    #  2    10   .06   2.5   1.8
    #  2    22   .06   2.5   1.8
    #  2    52  .195     3   4.5
    #  2    82   .21   3.5     5
    #  2   112    .2     2     2
    #  2   142    .2     1    .7
    #  2   172    .2     1    .6
    pars = {
        "PCR": "SG", "ICDAT": "80165", "ICRT": 500, "ICND": 0, "ICRN": 1, 
        "ICRE": 1, "ICRES": 1300, "ICREN": .5, "ICREP": 0, "ICRIP": 100, 
        "ICRID": 10 
    }
    for key, val in pars.items(): man.initial_conditions[key] = val
    man.initial_conditions["table"] = TabularSubsection({
        'ICBL': [10, 22, 52, 82, 112, 142, 172],
        'SH2O': [.06, .06, .195, .21, .2, .2, .2],
        'SNH4': [2.5, 2.5, 3, 3.5, 2, 1, 1],
        'SNO3': [1.8, 1.8, 4.5, 5, 2, .7, .6]
    })
    # *PLANTING DETAILS
    # @P PDATE EDATE  PPOP  PPOE  PLME  PLDS  PLRS  PLRD  PLDP  PLWT  PAGE  PENV  PLPH  SPRL                        PLNAME
    #  1 80169   -99    18    18     S     R    45     0     5   -99   -99   -99   -99     0                        -99
    pars = {
        "PPOP": 18, "PPOE": 18, "PLME": "S", "PLDS": "R", "PLRS": 45, 
        "PLRD": 0, "PLDP": 5, "SPRL": 0 
    }
    for key, val in pars.items(): man.planting_details[key] = val
    # *FERTILIZERS (INORGANIC)
    # @F FDATE  FMCD  FACD  FDEP  FAMN  FAMP  FAMK  FAMC  FAMO  FOCD FERNAME
    #  2 80185 FE005 AP002     5    80   -99   -99   -99   -99   -99 -99
    man.fertilizers["table"].loc[0] = (
        "80185", "FE005", "AP002", 5, 80, None, None, None, None, None, None
    )
    # *SIMULATION CONTROLS
    # @N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL
    #  1 GE              1     1     S 80165  2150 ICRISAT Alfisol N 1980 E
    # @N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2
    #  1 OP              Y     Y     N     N     N     N     N     N     M
    # @N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL
    #  1 ME              M     M     E     R     S     C     R     1     P     S     2
    # @N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS
    #  1 MA              R     N     R     N     M
    # @N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT
    #  1 OU              N     Y     Y     1     Y     N     Y     Y     N     N     Y     N     N
    pars = {
        "SDATE": "80165", "RSEED": 2150,
        "WATER": "Y", "NITRO": "Y", "CO2": "M", 
        "WTHER": "M", "INCON": "M", "LIGHT": "E", "EVAPO": "R", "INFIL": "S", 
            "PHOTO": "C", "HYDRO": "R", "NSWIT": 1, "MESOM": "P", "MESEV": "S", 
            "MESOL": 2, 
        "PLANT": "R", "IRRIG": "N", "FERTI": "R", "RESID": "N", "HARVS": "M", 
    }
    for key, val in pars.items(): man.simulation_controls[key] = val
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'dssat_test'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    harwt = int(dssat.stdout.split("\n")[-1].split()[6])
    assert np.isclose(6334, harwt, rtol=0.01)

def test_run_sweetcorn():
    crop = Crop('sweetcorn')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_alfalfa():
    crop = Crop('alfalfa')
    man = Management(
        planting_date=DATES[10],
    )
    man.mow['table'] = TabularSubsection({
        'DATE': [DATES[300].strftime('%y%j'), DATES[340].strftime('%y%j')], 
        'MOW': [1000, 1000], 'RSPLF': [20, 20], 'MVS': [2, 2], 'RSHT': [5, 5]
    })
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_bermudagrass():
    crop = Crop('bermudagrass')
    man = Management(
        planting_date=DATES[10],
    )
    man.mow['table'] = TabularSubsection({
        'DATE': [DATES[300].strftime('%y%j'), DATES[340].strftime('%y%j')], 
        'MOW': [1000, 1000], 'RSPLF': [20, 20], 'MVS': [2, 2], 'RSHT': [5, 5]
    })
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    # dssat.close()
    # assert not os.path.exists(dssat._RUN_PATH)

def test_run_soybean():
    """
    Experiment CLMO8501, treatment 1
    """
    crop = Crop('Soybean', "IB0011")
    soil = SoilProfile("tests/input_files/SOIL.SOL", "IBSB910032")
    ### Build weather from existing weather files
    df = pd.read_csv(f"tests/input_files/CLMO8501.WTH", skiprows=3, sep="\s+")
    df.index = pd.to_datetime(df["@DATE"], format="%y%j")
    wth =  Weather(
        df, {"TMIN": "TMIN", "SRAD": "SRAD", "RAIN": "RAIN", "TMAX": "TMAX",
             "PAR": "PAR"},
        lat=45.56, lon=-95.67
    )
    ### Define management
    man = Management(
        planting_date=datetime.strptime("85140", "%y%j"),
    )
    # *INITIAL CONDITIONS
    # @C   PCR ICDAT  ICRT  ICND  ICRN  ICRE  ICWD ICRES ICREN ICREP ICRIP ICRID ICNAME
    #  1    SB 85140     1   -99     1     1   -99   -99   -99   -99   -99   -99 -99
    # @C  ICBL  SH2O  SNH4  SNO3
    #  1     7  .467     0     0
    #  1    19  .444     0     0
    #  1    32  .444     0     0
    #  1    47  .444     0     0
    #  1    62  .444     0     0
    #  1    92  .333     0     0
    #  1   122  .333     0     0
    #  1   152  .333     0     0
    #  1   182  .333     0     0
    pars = {
        "PCR": "SB", "ICDAT": "85140", "ICRT": 1, "ICRN": 1, "ICRE": 1, 
    }
    for key, val in pars.items(): man.initial_conditions[key] = val
    man.initial_conditions["table"] = TabularSubsection({
        'ICBL': [7, 19, 32, 47, 62, 92, 122, 152, 182],
        'SH2O': [.467, .444, .444, .444, .444, .333, .333, .333, .333],
        'SNH4': [0, 0, 0, 0, 0, 0, 0, 0, 0],
        'SNO3': [0, 0, 0, 0, 0, 0, 0, 0, 0]
    })
    # *PLANTING DETAILS
    # @P PDATE EDATE  PPOP  PPOE  PLME  PLDS  PLRS  PLRD  PLDP  PLWT  PAGE  PENV  PLPH  SPRL                        PLNAME
    #  1 85140   -99  25.3  25.3     S     R    74     0     4   -99   -99   -99   -99   -99                        -99
    pars = {
        "PPOP": 25.3, "PPOE": 25.3, "PLME": "S", "PLDS": "R", "PLRS": 74, 
        "PLRD": 0, "PLDP": 4, 
    }
    for key, val in pars.items(): man.planting_details[key] = val
    #  *IRRIGATION AND WATER MANAGEMENT
    # @I  EFIR  IDEP  ITHR  IEPT  IOFF  IAME  IAMT IRNAME
    #  1   .75   -99   -99   -99   -99   -99   -99 -99
    # @I IDATE  IROP IRVAL
    #  1 85183 IR001    41
    #  1 85189 IR001    54
    #  1 85196 IR001    56
    #  1 85200 IR001    51
    #  1 85214 IR001    40
    #  1 85221 IR001    25
    man.irrigation["EFIR"] = .75
    man.irrigation["table"] = TabularSubsection({
        'IDATE': ["85183", "85189", "85196", "85200", "85214", "85221"],
        'IROP': ["IR001"]*6,
        'IRVAL': [41, 54, 56, 51, 40, 25],
    })
    #  *SIMULATION CONTROLS
    # @N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL
    #  1 GE              1     1     S 85140  2150 EVANS, IRRIGATED AND NON
    # @N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2
    #  1 OP              Y     Y     Y     N     N     N     N     Y     M
    # @N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL
    #  1 ME              M     M     E     R     S     L     R     1     G     R     2
    # @N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS
    #  1 MA              R     R     R     R     M
    # @N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT
    #  1 OU              N     Y     Y     1     Y     Y     Y     Y     N     N     Y     N     N
    pars = {
        "SDATE": "85140", "RSEED": 2150,
        "WATER": "Y", "NITRO": "Y", "SYMBI": "Y", "TILL": "Y", "CO2": "M", 
        "WTHER": "M", "INCON": "M", "LIGHT": "E", "EVAPO": "R", "INFIL": "S", 
            "PHOTO": "L", "HYDRO": "R", "NSWIT": 1, "MESOM": "G", "MESEV": "R", 
            "MESOL": 2, 
        "PLANT": "R", "IRRIG": "R", "FERTI": "R", "RESID": "R", "HARVS": "M", 
    }
    for key, val in pars.items(): man.simulation_controls[key] = val
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'dssat_test'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    harwt = int(dssat.stdout.split("\n")[-1].split()[6])
    assert np.isclose(2495, harwt, rtol=0.01)

def test_run_canola():
    crop = Crop('canola')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_run_sunflower():
    crop = Crop('sunflower')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_run_potato():
    crop = Crop('potato')
    man = Management(
        planting_date=DATES[10],
    )
    man.planting_details['PLWT'] = 1500
    man.planting_details['SPRL'] = 2
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_run_potato_no_transplanting():
    crop = Crop('potato')
    man = Management(
        planting_date=DATES[10],
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    with pytest.raises(AssertionError) as excinfo:
        dssat.run(
            soil=soil, weather=wth, crop=crop, management=man,
        )
        assert 'transplanting parameters are mandatory' in str(excinfo.value)

def test_run_tomato():
    """
    Experiment UFBR9401, treatment 4
    """
    crop = Crop('Tomato', "TM0007")
    soil = SoilProfile("tests/input_files/SOIL.SOL", "UFBR950001")
    ### Build weather from existing weather files
    df = pd.read_csv(f"tests/input_files/UFBR9401.WTH", skiprows=4, sep="\s+")
    df.index = pd.to_datetime(df["@DATE"], format="%y%j")
    wth =  Weather(
        df, {"TMIN": "TMIN", "SRAD": "SRAD", "RAIN": "RAIN", "TMAX": "TMAX"},
        lat=27.600, lon=-82.600, elev=10,
    )
    ### Define management
    man = Management(
        planting_date=datetime.strptime("94060", "%y%j"),
    )
    # *INITIAL CONDITIONS
    # @C   PCR ICDAT  ICRT  ICND  ICRN  ICRE  ICWD ICRES ICREN ICREP ICRIP ICRID ICNAME
    #  1    PR 94060     1     0     1     1   -99     0     0     0   100    15 -99
    # @C  ICBL  SH2O  SNH4  SNO3
    #  1    18  .133    .5     2
    #  1    36  .222    .5     2
    #  1    50    .3    .5     2
    #  1    74  .389     0     0
    #  1    81    .4     0     0
    #  1   119    .4     0     0
    #  1   173    .4     0     0
    #  1   190    .4     0     0
    #  1   203    .4     0     0
    pars = {
        "PCR": "PR", "ICDAT": "94060", "ICRT": 1, "ICND": 0, "ICRN": 1, 
        "ICRE": 1, "ICRES": 0, "ICREN": 0, "ICRIP": 100, "ICRID": 15,
    }
    for key, val in pars.items(): man.initial_conditions[key] = val
    man.initial_conditions["table"] = TabularSubsection({
        'ICBL': [18, 36, 50, 74, 81, 119, 173, 190, 203],
        'SH2O': [.133, .222, .3, .389, .4, .4, .4, .4, .4],
        'SNH4': [.5, .5, .5, 0, 0, 0, 0, 0, 0],
        'SNO3': [2, 2, 2, 0, 0, 0, 0, 0, 0]
    })
    # *PLANTING DETAILS
    # @P PDATE EDATE  PPOP  PPOE  PLME  PLDS  PLRS  PLRD  PLDP  PLWT  PAGE  PENV  PLPH  SPRL                        PLNAME
    #  1 94060   -99   1.1   1.1     T     R   152    90     1     3    25    25     1     0                        -99
    pars = {
        "PPOP": 1.1, "PPOE": 1.1, "PLME": "T", "PLDS": "R", "PLRS": 152, "PLRD": 90, 
        "PLDP": 1, "PLWT": 3, "PAGE": 25, "PENV": 25, "PLPH": 1, "SPRL": 0
    }
    for key, val in pars.items(): man.planting_details[key] = val
    # *HARVEST DETAILS
    # @H HDATE  HSTG  HCOM HSIZE   HPC  HBPC HNAME
    #  1 94160 GS000   -99   -99   -99     0 
    man.harvest_details["HDATE"] = "94160"
    man.harvest_details["HSTG"] =  "GS000"
    # *FERTILIZERS (INORGANIC)
    # @F FDATE  FMCD  FACD  FDEP  FAMN  FAMP  FAMK  FAMC  FAMO  FOCD FERNAME
    #  4 94050 FE001 AP001    10   255     0     0     0     0   -99 -99
    man.fertilizers["table"].loc[1] = (
        "94050", "FE001", "AP001", 10, 255, 0, 0, 0, 0, None, None
    )
    #  *IRRIGATION AND WATER MANAGEMENT
    # @I  EFIR  IDEP  ITHR  IEPT  IOFF  IAME  IAMT IRNAME
    #  1   .95     5   -99   -99   -99   -99   -99 -99
    # @I IDATE  IROP IRVAL
    #  1 94061 IR007     3
    #  1 94062 IR007     3
    #  . ..... .....     .
    #  1 94174 IR007     5
    #  1 94175 IR007     5
    man.irrigation["EFIR"] = .95
    man.irrigation["IDEP"]= 5
    man.irrigation["table"] = TabularSubsection({
        'IDATE': [
            '94061','94062','94063','94064','94065','94066','94067','94068',
            '94069','94070','94071','94072','94073','94074','94075','94076',
            '94077','94078','94079','94080','94081','94082','94083','94084',
            '94085','94086','94087','94088','94089','94090','94091','94092',
            '94093','94094','94095','94096','94097','94098','94099','94100',
            '94101','94102','94103','94104','94105','94106','94107','94108',
            '94109','94110','94111','94112','94113','94113','94114','94115',
            '94116','94117','94118','94119','94120','94121','94122','94123',
            '94124','94125','94126','94127','94128','94129','94130','94131',
            '94132','94133','94134','94135','94136','94137','94138','94139',
            '94140','94141','94142','94143','94144','94145','94146','94147',
            '94148','94149','94150','94151','94152','94153','94154','94155',
            '94156','94157','94158','94159','94160','94161','94162','94163',
            '94164','94165','94166','94167','94168','94169','94160','94161',
            '94162','94163','94164','94165','94166','94167','94168','94169',
            '94170','94171','94172','94173','94174','94175'
        ],
        'IROP': ["IR007"]*126,
        'IRVAL': [
            3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,4,4,3,3,4,3,3,4,4,3,3,3,4,
            4,4,3,4,4,4,4,4,4,5,4,4,4,4,4,4,4,4,3,3,4,4,3,4,4,4,5,5,4,5,5,5,
            5,5,5,5,4,5,4,5,4,4,5,5,5,3,3,5,4,5,5,5,5,5,5,5,5,4,4,5,5,3,2,2,
            4,4,3,3,5,5,5,6,6,4,6,6,6,6,6,6,6,6,6,6,6,6,6,5,5,5,5,5,5,5
        ],
    })
    # *SIMULATION CONTROLS
    # @N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL
    #  1 GE              1     1     S 94050  2150 FERT TRIAL
    # @N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2
    #  1 OP              N     N     N     N     N     N     N     N     M
    # @N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL
    #  1 ME              M     M     E     R     S     L     R     1     G     R     2
    # @N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS
    #  1 MA              R     A     R     N     M
    # @N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT FMOPT
    #  1 OU              N     Y     Y     1     Y     Y     Y     Y     N     N     Y     N     N     A
    pars = {
        "SDATE": "94050", "RSEED": 2150,
        "WATER": "N", "NITRO": "N", "CO2": "M", "WTHER": "M", "INCON": "M",
        "LIGHT": "E", "EVAPO": "R", "INFIL": "S", "PHOTO": "L", "HYDRO": "R",
        "NSWIT": 1, "MESOM": "G", "MESEV": "R", "MESOL": 2, "PLANT": "R",
        "IRRIG": "A", "FERTI": "R", "RESID": "N", "HARVS": "M", 
    }
    for key, val in pars.items(): man.simulation_controls[key] = val
    # @  AUTOMATIC MANAGEMENT
    # @N PLANTING    PFRST PLAST PH2OL PH2OU PH2OD PSTMX PSTMN
    #  1 PL          10099 10099    40   100    30    45    40
    # @N IRRIGATION  IMDEP ITHRL ITHRU IROFF IMETH IRAMT IREFF
    #  1 IR             30    80   100 GS000 SI001    10     1
    # @N NITROGEN    NMDEP NMTHR NAMNT NCODE NAOFF
    #  1 NI            200    50    25 SI001 SI001
    # @N RESIDUES    RIPCN RTIME RIDEP
    #  1 RE            100    60    20
    # @N HARVEST     HFRST HLAST HPCNP HPCNR
    #  1 HA            160 94160    75     0
    pars = {
        "IMDEP": 30, "ITHRL": 80, "ITHRU": 100, "IROFF": "GS000", 
        "IMETH": "SI001", "IRAMT": 10, "IREFF": 1
    }
    for key, val in pars.items(): man.automatic_management[key] = val

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'dssat_test'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    harwt = int(dssat.stdout.split("\n")[-1].split()[6])
    assert np.isclose(6360, harwt, rtol=0.01)
    # dssat.close()

def test_run_cabbage():
    crop = Crop('cabbage')
    man = Management(
        planting_date=DATES[10],
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_run_sugarcane():
    crop = Crop('Sugarcane')
    man = Management(
        planting_date=DATES[10],
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_sc'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))

def test_run_wheat():
    """
    KSAS8101 experiment, treatment 1
    """
    crop = Crop('Wheat', "IB0488")
    soil = SoilProfile("tests/input_files/SOIL.SOL", "IBWH980018")
    # Management
    df = pd.DataFrame()
    for year in range(81, 83):
        df = pd.concat(
            [df, pd.read_csv(f"tests/input_files/wheat/KSAS{year}01.WTH", skiprows=4, sep="\s+")], 
            ignore_index=True
        )
    df.index = pd.to_datetime(df["@DATE"], format="%y%j")
    wth =  Weather(
        df, {"TMIN": "TMIN", "SRAD": "SRAD", "RAIN": "RAIN", "TMAX": "TMAX"},
        lat=37.18, lon=-99.75, elev=226, tav=12., amp=32
    )
    
    man = Management(
        planting_date=datetime.strptime("81289", "%y%j"),
    )
    # Initial conditions 
    pars = {
        "PCR": "WH", "ICDAT": "81279", "ICRT": 1200, "ICND": 0, "ICRN": 1,
        "ICRE": 1, "ICRES": 6500, "ICREN": 1.14, "ICREP": 0, "ICRIP": 100,
        "ICRID": 15,
    }
    for key, val in pars.items(): man.initial_conditions[key] = val
    man.initial_conditions["table"] = TabularSubsection(pd.DataFrame(
        [(  15,  .205,   3.4,   9.8),
         (  30,   .17,   3.2,   7.3),
         (  60,  .092,   2.5,   5.1),
         (  90,  .065,   2.2,   4.7),
         ( 120,  .066,   2.7,   4.3),
         ( 150,  .066,   2.7,   4.3),
         ( 180,  .066,   2.7,   4.3)],
        columns=["ICBL", "SH2O", "SNH4", "SNO3"]
    ))
    # Planting
    pars = {
        "EDATE": None, "PPOP": 162, "PPOE": 162, "PLME": "S", "PLRS": 16,
        "PLRD": 0, "PLDP": 5.5 
    }
    for key, val in pars.items(): man.planting_details[key] = val
    # Simulation controls
    pars = {
        "WATER": "Y", "NITRO": "Y", "CO2": "M", "WTHER": "M", "INCON": "M",
        "LIGHT": "E", "EVAPO": "R", "INFIL": "S", "PHOTO": "C", "HYDRO": "R",
        "NSWIT": 1, "MESOM": "G", "MESEV": "S", "MESOL": 2, "PLANT": "R",
        "IRRIG": "R", "FERTI": "R", "RESID": "N", "HARVS": "M", "SDATE": 81279,
        "RSEED": 2150, "NIOUT": "Y", "CAOUT": "N",
    }
    for key, val in pars.items(): man.simulation_controls[key] = val
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_wh'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    harwt = int(dssat.stdout.split("\n")[-1].split()[6])
    assert np.isclose(2417, harwt, rtol=0.01)

def test_close():
    crop = Crop('cabbage')
    man = Management(
        planting_date=DATES[10],
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(TMP, 'test_mz'))
    dssat.close()
    assert not os.path.exists(os.path.join(TMP, 'test_mz'))

def test_issue_1():
    # https://github.com/daquinterop/Py_DSSATTools/issues/1
    crop = Crop('soybean', 'IB0011')
    man = Management(
        planting_date=DATES[10],
        irrigation='A',
        fertilization='A'
    )
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    assert crop.cultivar['LFMAX'] == 1.020
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))
    final_yield = int(dssat.output['PlantGro']['GWAD'].max())
    crop.cultivar['LFMAX'] = 1.35
    assert crop.cultivar['LFMAX'] == 1.35
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert dssat.output['PlantGro']['GWAD'].max() != final_yield    

def test_set_crop_parameter_and_run():
        crop = Crop('maize', 'IB0011')
        assert crop.cultivar['PHINT'] == 38.9
        crop.cultivar['PHINT'] = 30.
        assert crop.cultivar['PHINT'] == 30.

        man = Management(
            planting_date=DATES[10],
            irrigation='A',
            fertilization='A'
        )

        dssat = DSSAT()
        dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
        dssat.run(
            soil=soil, weather=wth, crop=crop, management=man,
        )
    
def test_issue_11():
    crop = Crop('maize')
    man = Management(
        planting_date=DATES[10],
    )
    crop.cultivar['P5'] = 1100.
    crop.cultivar['G2'] = 1050.
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert os.path.exists(os.path.join(dssat._RUN_PATH, 'Summary.OUT'))    

def test_outputs():
    """
    Test that different outputs are saved if they have been defined in the 
    simulation_controls
    """
    crop = Crop('maize')
    man = Management(
        planting_date=DATES[10],
    )

    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    outputs = ['PlantGro', "Weather", "SoilWat", "SoilOrg"]
    assert all(map(lambda x: x in outputs, dssat.output))

    man.simulation_controls["GROUT"] = "N"
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert all(
        map(lambda x: (x in ["SoilWat", "SoilOrg"]) 
            and (x not in ['PlantGro', "Weather"]) 
            ,dssat.output)
    )
    assert all(map(lambda x: x in outputs, dssat.output))

    man.simulation_controls["WAOUT"] = "N"
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    assert all(
        map(lambda x: (x in ["SoilOrg"]) 
            and (x not in ['PlantGro', "Weather", "SoilWat"]) 
            ,dssat.output)
    )

    man.simulation_controls["CAOUT"] = "N"
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )
    with pytest.warns(UserWarning, match='No output has been'):
        dssat.output 

def test_no_wat_sim():
    crop = Crop('maize')
    man = Management(
        planting_date=DATES[10],
    )
    man.simulation_controls["WATER"] = "N" 
    dssat = DSSAT()
    dssat.setup(cwd=os.path.join(TMP, 'test_mz'))
    dssat.run(
        soil=soil, weather=wth, crop=crop, management=man,
    )

def test_setup_setup_deprecation():
    dssat = DSSAT()
    with pytest.warns(DeprecationWarning, match='calling setup method is not longer needed'):
        dssat.setup()

if __name__ == '__main__':
    test_run_sorghum()