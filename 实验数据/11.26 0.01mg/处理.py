import os
import numpy as np
from data_process.data_process import lockIn, preprocess, process, process_without_filter
from matplotlib import pyplot as plt
import fnmatch

filelist = os.listdir(".")
filelist_fs_50 = fnmatch.filter(filelist, "*50*.DAT")
filelist_fs_100 = fnmatch.filter(filelist, "*100*.DAT")

amp_fs_50 = []
fig_fs_50 = []
amp_fs_100 = []
fig_fs_100 = []
amp_list = []
fig_list = []
for file in filelist_fs_100:
    timelist, counts_per_sec = preprocess(file)
    amp, fig = process_without_filter(timelist, counts_per_sec, 20)
    amp_list.append(amp * np.pi / 2)
    fig_list.append(fig)

sum_fig = plt.figure()
plt.plot(amp_list, marker=".", ls='None')
plt.xlabel("Number of experiment")
plt.ylabel("Amp.")

amp_list = np.array(amp_list)

print("mean: {:.3f}, std: {:.3f}".format(np.mean(amp_list), np.std(amp_list)))
save_folder = os.path.join("..", "..", "figure", "Fs=100 int=20")

for ind, fig in enumerate(fig_list):
    fig.savefig("{}/Fs=100-{}.png".format(save_folder, ind), bbox_inches='tight', dpi=600)

sum_fig.savefig("{}/Fs=100 all.png".format(save_folder), bbox_inches='tight', dpi=600)
# plt.show()
