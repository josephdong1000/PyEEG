import os
import sys
from pathlib import Path
import time
import tempfile
import logging

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import mne
from dask_jobqueue import SLURMCluster
from dask.distributed import Client

packageroot = Path('/home/dongjp/source-code/PyEEG').resolve()
sys.path.append(str(packageroot))

from pythoneeg import core
from pythoneeg import visualization
from pythoneeg import constants

core.set_temp_directory('/scr1/users/dongjp')

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger()


animal_ids = ['A5', 'A10', 'F22', 'G25', 'G26', 'N21', 'N22', 'N23', 'N24', 'N25']
# animal_ids = ['A5', 'A10']
base_folder = Path('/mnt/isilon/marsh_single_unit/PythonEEG Data Bins').resolve()

# TODO reject all the bad channels by eye when constructing EP
wars = []
for animal_id in animal_ids:
    war = visualization.WindowAnalysisResult.load_pickle_and_json(Path(f'/home/dongjp/source-code/PyEEG/notebooks/tests/test-wars-full/{animal_id}').resolve())
    if animal_id == 'F22':
        war.filter_all(reject_channels=['LMot', 'RBar', 'RVis', 'RAud'])
    elif animal_id == 'N21':
        war.filter_all(reject_channels=['RBar'])
    elif animal_id == 'G25':
        war.filter_all(reject_channels=['LAud', 'LHip'])

    wars.append(war)
ep = visualization.ExperimentPlotter(wars)

catplot_params = {'showfliers': False}
kinds = ['box', 'bar']
save_folder = Path('/home/dongjp/Downloads/4-3-25/remake').resolve()

# SECTION CATPLOTS

# g = ep.plot_catplot('rms', groupby='animal', kind='box', catplot_params={'showfliers': False, 'aspect': 4})
# g.savefig(save_folder / 'AAAA every animal box.png', dpi=300)
# for feature in constants.LINEAR_FEATURE:
#     for kind in kinds:
#         for groupby in ['genotype', ['genotype', 'isday']]:
#             for collapse in [False, True]:
#                 g = ep.plot_catplot(feature, groupby=groupby, kind=kind, collapse_channels=collapse, catplot_params=catplot_params if kind == 'box' else None)
#                 g.savefig(save_folder / f'{feature}-{groupby}-{kind}-{collapse}.png', dpi=300)
# for kind in kinds:
#     g = ep.plot_catplot('psdband', groupby=['genotype', 'isday'], 
#                     x='genotype',
#                     col='isday',
#                     hue='band',
#                     kind=kind, collapse_channels=True, catplot_params=catplot_params if kind == 'box' else None)
#     g.savefig(save_folder / f'psdband-genotype-isday-{kind}-True.png', dpi=300)
#     g = ep.plot_catplot('psdband', groupby=['genotype'], 
#                     x='genotype',
#                     hue='band',
#                     kind=kind, collapse_channels=True, catplot_params=catplot_params if kind == 'box' else None)
#     g.savefig(save_folder / f'psdband-genotype-{kind}-True.png', dpi=300)

# SECTION MATRIX PLOTS

g = ep.plot_matrixplot('pcorr', groupby='animal')
g.savefig(save_folder / 'AAAA every animal pcorr.png', dpi=300)
g = ep.plot_matrixplot('cohere', groupby='animal')
g.savefig(save_folder / 'AAAA every animal cohere.png', dpi=300)

for feature in constants.MATRIX_FEATURE:
    for kind in kinds:
        for groupby in [['genotype', 'isday'], 'genotype']:
            g = ep.plot_catplot(feature, groupby=groupby, kind=kind, collapse_channels=True, catplot_params=catplot_params if kind == 'box' else None)
            g.savefig(save_folder / f'{feature}-{groupby}-{kind}-True.png', dpi=300)

g = ep.plot_matrixplot('cohere', groupby=['genotype', 'isday'])
g.savefig(save_folder / 'cohere-genotype-isday-matrix-False.png', dpi=300)
g = ep.plot_matrixplot('cohere', groupby='genotype', col='band', row='genotype')
g.savefig(save_folder / 'cohere-genotype-band-matrix-False.png', dpi=300)

g = ep.plot_matrixplot('pcorr', groupby=['genotype', 'isday'])
g.savefig(save_folder / 'pcorr-genotype-isday-matrix-False.png', dpi=300)
g = ep.plot_matrixplot('pcorr', groupby='genotype')
g.savefig(save_folder / 'pcorr-genotype-matrix-False.png', dpi=300)

# SECTION QQ PLOTS

# for log in [True, False]:
#     for feature in ['rms', 'ampvar', 'psdtotal']:
#         g = ep.plot_qqplot(feature, ['animal'], row='animal', col='channel', height=3, log=log)
#         g.savefig(save_folder / f'qq-{feature}-animal-channel-{log}.png', dpi=300)
#         g = ep.plot_qqplot(feature, ['genotype'], row='genotype', col='channel', height=3, log=log)
#         g.savefig(save_folder / f'qq-{feature}-genotype-channel-{log}.png', dpi=300)

"""
sbatch --mem 100G -c 8 -t 24:00:00 ./notebooks/examples/pipeline-warfig.sh
"""