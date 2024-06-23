from DSSATTools.filex import (
    read_filex, Planting, InitialConditions, InitialConditionsLayer
    )
from DSSATTools.base.partypes import NumberType
from datetime import date

read_filex("/home/diego/dssat-csm-data/Maize/GHWA0401.MZX")

ic = InitialConditions("MZ",
    table=[InitialConditionsLayer(10, 0.4,), InitialConditionsLayer(20, 0.4,)])

print(ic.table)
print(ic)