from data_process.data_process import preprocess, lockIn
import matplotlib.pyplot as plt
import os

folder = "./0mg 清洗线圈"
for file in os.listdir(folder):
    if not file.endswith(".DAT"):
        continue
    plt.figure()
    timelist, counts = preprocess(os.path.join(folder, file))
    plt.plot(timelist, counts)

plt.show()
