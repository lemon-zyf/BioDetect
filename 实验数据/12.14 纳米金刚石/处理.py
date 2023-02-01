from data_process.data_process import preprocess, lockIn
from matplotlib import pyplot as plt

filepath = "Fm=1Hz/0.01mg/50.DAT"
# filepath = "Fm=0.01Hz/0mg/50.DAT"
Fm = 1
periodNumber = 5

timelist, count = preprocess(filepath)
plt.plot(timelist, count)
plt.show()
