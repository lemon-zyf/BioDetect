from data_process.data_process import preprocess
from matplotlib import pyplot as plt

timelist, counts = preprocess("50.DAT")
plt.plot(timelist, counts)
plt.show()
