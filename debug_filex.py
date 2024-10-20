from DSSATTools.filex import (
    read_filex, Planting, InitialConditions, InitialConditionsLayer
    )
from DSSATTools.base.partypes import NumberType
from datetime import date

# experiment = read_filex("/home/diego/dssat-csm-data/Maize/EBPL8501.MZX")
# experiment = read_filex("/home/diego/dssat-csm-data/Soybean/UFGA8401.SBX")
experiment = read_filex("/home/diego/dssat-csm-data/Soybean/IUCA7901.SBX")

field = experiment["Field"][1]
field._write_section()
planting = experiment["Planting"][1]

planting._write_section()
# read_filex("/home/diego/dssat-csm-data/Sunflower/INRA0601.SUX")

ic = InitialConditions("MZ",
    table=[InitialConditionsLayer(10, 0.4,), InitialConditionsLayer(20, 0.4,)])

print(ic.table)
print(ic)