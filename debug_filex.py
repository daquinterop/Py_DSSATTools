from DSSATTools.filex import (
    read_filex, Planting, InitialConditions, InitialConditionsLayer
    )
from DSSATTools.base.partypes import NumberType
from datetime import date
from DSSATTools.crop import Maize

# experiment = read_filex("/home/diego/dssat-csm-data/Maize/EBPL8501.MZX")
# experiment = read_filex("/home/diego/dssat-csm-data/Soybean/UFGA8401.SBX")
# experiment = FileX("/home/diego/dssat-csm-data/Soybean/IUCA7901.SBX")
treatments = read_filex("SAMPLE.fileX")
# print(experiment["Irrigation"][1].table._write_table())
for t, treat in treatments.items():
    for _, sec in treat.items():
        print(sec._write_section())

cultivar = Maize("IB0009")


# print(ic.table)
# print(ic)