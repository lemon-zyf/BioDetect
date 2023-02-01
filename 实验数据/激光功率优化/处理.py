from data_process.data_process import preprocess, lockIn
from matplotlib import pyplot as plt
from math import pi
import os

for files in os.listdir("."):
    if not files.endswith(".DAT"):
        continue
    timelist, counts = preprocess(files)
    amp = pi / 2 * lockIn(counts, timelist, 1, 1)
    print(files, amp)
    plt.figure()
    plt.plot(timelist, counts, label="amp: {:.3f}".format(amp))
    plt.legend(loc='upper right')
    plt.xlabel("Time (s)")
    plt.ylabel("Counts")
    plt.savefig("figure/{}.png".format(files.split(".DAT")[0]), bbox_inches='tight', dpi=600)
plt.show()
