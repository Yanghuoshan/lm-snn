import os
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as manimation

from tqdm import tqdm
from mpl_toolkits.axes_grid1 import make_axes_locatable


parser = argparse.ArgumentParser()
parser.add_argument('--n_files', type=int, default=-1)
parser.add_argument('--conv_features', type=int, default=400)
parser.add_argument('--conv_stride', type=int, default=0)
parser.add_argument('--conv_size', type=int, default=28)
parser.add_argument('--num_train', type=int, default=10000)
parser.add_argument('--random_seed', type=int, default=42)

args = parser.parse_args()
args = vars(args)
locals().update(args)

if conv_size == 28 and conv_stride == 0:
	n_e = 1
else:
	n_e = ((n_input_sqrt - conv_size) / conv_stride + 1) ** 2

model_name = 'csnn_growing_inhibition'

top_level_path = os.path.join('..', '..')
spikes_dir = os.path.join(top_level_path, 'spikes', model_name)

model = '_'.join(map(str, [ conv_size, conv_stride, conv_features, n_e, num_train, random_seed ]))

n_input_sqrt = 28
conv_features_sqrt = int(np.sqrt(conv_features))

activity_files = sorted([ file for file in os.listdir(spikes_dir) \
			if 'spike_counts' in file and model in file ], key=lambda x: int(x.split('_')[-1][:-4]))
rates_files = sorted([ file for file in os.listdir(spikes_dir) \
			if 'rates' in file and model in file ], key=lambda x: int(x.split('_')[-1][:-4]))

FFMpegWriter = manimation.writers['ffmpeg']
writer = FFMpegWriter(fps=5, bitrate=-1)

fig, (ax1, ax2) = plt.subplots(1, 2)
image1 = ax1.imshow(np.zeros([ conv_features_sqrt, conv_features_sqrt ]), cmap='binary', vmin=0, vmax=1, interpolation='nearest')
image2 = ax2.imshow(np.zeros([ n_input_sqrt, n_input_sqrt ]), cmap='binary', vmin=0, vmax=64, interpolation='nearest')

divider1 = make_axes_locatable(ax1)
divider2 = make_axes_locatable(ax2)
cax1 = divider1.append_axes("right", size="5%", pad=0.05)
cax2 = divider2.append_axes("right", size="5%", pad=0.05)

fig.colorbar(image1, cax=cax1)
fig.colorbar(image2, cax=cax2)

with writer.saving(fig, os.path.join('movies', '_'.join([ model, str(n_files) ]) + '.mp4'), \
						len(activity_files[:n_files])):
	if n_files == -1:
		for activity_file, rates_file in tqdm(zip(activity_files, rates_files)):
			print activity_file, rates_file

			activity = np.load(os.path.join(spikes_dir, activity_file))

			print activity.shape

			activity = activity / float(np.sum(activity))

			rates = np.load(os.path.join(spikes_dir, rates_file))

			print rates.shape

			image1.set_data(activity.reshape([conv_features_sqrt, conv_features_sqrt]))
			image2.set_data(rates)

			writer.grab_frame()
	else:
		for activity_file, rates_file in tqdm(zip(activity_files[:n_files], rates_files[:n_files])):
			activity = np.load(os.path.join(spikes_dir, activity_file))
			activity = activity / float(np.sum(activity))

			rates = np.load(os.path.join(spikes_dir, rates_file))

			image1.set_data(activity.reshape([conv_features_sqrt, conv_features_sqrt]))
			image2.set_data(rates)

			writer.grab_frame()