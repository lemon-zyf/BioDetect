from data_process.data_process import preprocess, lockIn
from matplotlib import pyplot as plt
from math import pi

"""
2920MHz amp=684.769
2870MHz amp=976.586
"""

file = "./0mg 更换线圈/12.14.DAT"
timelist, counts = preprocess(file)
Fm = 1
periodNumber = 5

amp = pi / 2 * lockIn(inputSignal=counts, tlist=timelist, Fm=Fm, periodNumber=periodNumber)
print(amp)
plt.plot(timelist, counts)
plt.xlabel("Time (s)")
plt.ylabel("Counts")
plt.xlim(left=0, right=8 / Fm)
# plt.savefig("figure/更换好一点的玻片.png", dpi=600, bbox_inches='tight')
plt.show()
