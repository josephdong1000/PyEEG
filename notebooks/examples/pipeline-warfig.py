import sys
from pathlib import Path
import logging
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import mne

from pythoneeg import core
from pythoneeg import visualization
from pythoneeg import constants

core.set_temp_directory('/scr1/users/dongjp')

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger()

base_folder = Path('/mnt/isilon/marsh_single_unit/PythonEEG')
# animal_ids = ['A5', 'A10', 'F22', 'G25', 'G26', 'N21', 'N22', 'N23', 'N24', 'N25']
# animal_ids = ['A5', 'A10']
animal_ids = [p.name for p in (base_folder / 'notebooks' / 'tests' / 'test-wars-sox5-2').glob('*') if p.is_dir()]
# animal_ids = [
#     '081922_cohort10_group4_2mice_FMut_FHet FHET',
#     '062921_Cohort 3_AM3_AM5_CM9_BM6_CM5_CF2_IF5_BF3 CF2',
# ]

def load_war(animal_id):
    logger.info(f'Loading {animal_id}')
    war = visualization.WindowAnalysisResult.load_pickle_and_json(
        Path(base_folder / 'notebooks' / 'tests' / 'test-wars-sox5-2' / f'{animal_id}').resolve()
    )
    if war.genotype == 'Unknown': # Remove pathological recordings
        logger.info(f'Skipping {animal_id} because genotype is Unknown')
        return None
    
    war.filter_all()
    war.aggregate_time_windows()
    war.add_unique_hash()
    war.reorder_and_pad_channels(['LMot', 'RMot', 'LBar', 'RBar', 'LAud', 'RAud', 'LVis', 'RVis', 'LHip', 'RHip'], use_abbrevs=True)

    return war

# Use multiprocessing to load WARs in parallel
num_cores = 10
with Pool(num_cores) as pool:
    wars = []
    for war in tqdm(pool.imap(load_war, animal_ids), total=len(animal_ids), desc="Loading WARs"):
        if war is not None:
            wars.append(war)


logger.info(f'{len(wars)} wars loaded')
exclude = ['nspike', 'lognspike']
ep = visualization.ExperimentPlotter(wars, exclude=exclude)

# SECTION Define parameters
catplot_params = {'showfliers': False}
kinds = ['box']
save_folder = Path('/home/dongjp/Downloads/6-9 sox5 swarm marked').resolve()
if not save_folder.exists():
    save_folder.mkdir(parents=True)
# !SECTION

# SECTION CATPLOTS
logger.info("Generating box plot for rms for every animal")
g = ep.plot_catplot('rms', groupby='animal', kind='box', catplot_params={'showfliers': False, 'aspect': 4})
g.savefig(save_folder / 'AAAA every animal box.png', dpi=300)

# for feature in [x for x in constants.LINEAR_FEATURES if x not in exclude]:
#     for kind in kinds:
#         for groupby in ['genotype', ['genotype', 'isday']]:
#             for collapse in [False, True]:
#                 logger.info(f"Generating {kind} plot for {feature} with {groupby} grouping, collapse={collapse}")
#                 g = ep.plot_catplot(feature, groupby=groupby, kind=kind, collapse_channels=collapse, catplot_params=catplot_params if kind == 'box' else None)
#                 g.savefig(save_folder / f'{feature}-{groupby}-{kind}-{collapse}.png', dpi=300)

# for kind in kinds:
#     logger.info(f"Generating {kind} plot for psdband with genotype and isday grouping")
#     g = ep.plot_catplot('psdband', groupby=['genotype', 'isday'], 
#                     x='genotype',
#                     col='isday',
#                     hue='band',
#                     kind=kind, collapse_channels=True, catplot_params=catplot_params if kind == 'box' else None)
#     g.savefig(save_folder / f'psdband-genotype-isday-{kind}-True.png', dpi=300)
    
#     logger.info(f"Generating {kind} plot for psdband with genotype grouping")
#     g = ep.plot_catplot('psdband', groupby=['genotype'], 
#                     x='genotype',
#                     hue='band',
#                     kind=kind, collapse_channels=True, catplot_params=catplot_params if kind == 'box' else None)
#     g.savefig(save_folder / f'psdband-genotype-{kind}-True.png', dpi=300)

# for feature in [x for x in constants.MATRIX_FEATURES if x not in exclude]:
#     for kind in kinds:
#         for groupby in [['genotype', 'isday'], 'genotype']:
#             logger.info(f"Generating {kind} plot for {feature} with {groupby} grouping")
#             g = ep.plot_catplot(feature, groupby=groupby, kind=kind, collapse_channels=True, catplot_params=catplot_params if kind == 'box' else None)
#             g.savefig(save_folder / f'{feature}-{groupby}-{kind}-True.png', dpi=300)
# !SECTION

# SECTION CATPLOTS, AVERAGE GROUPBY
for kind in ['swarm', 'point']:
    for feature in [x for x in constants.LINEAR_FEATURES if x not in exclude]:
        logger.info(f"Generating {kind} plot for {feature} with genotype grouping")
        for collapse in [False, True]:
            g = ep.plot_catplot(feature, groupby=['animal', 'genotype'], x='genotype', hue='channel', kind=kind, average_groupby=True, collapse_channels=collapse, 
                                catplot_params={'dodge': (kind == 'swarm' or not collapse), 'col': None, 'errorbar': 'ci'})
            g.savefig(save_folder / f'{kind}-{feature}-genotype-{"avgch" if collapse else "no avgch"}.png', dpi=300)
        for collapse in [False, True]:
            logger.info(f"Generating {kind} plot for {feature} with genotype and isday grouping")
            g = ep.plot_catplot(feature, groupby=['animal', 'genotype', 'isday'], x='genotype', col='isday', hue='channel', kind=kind, average_groupby=True, collapse_channels=collapse, 
                                catplot_params={'dodge': (kind == 'swarm' or not collapse), 'errorbar': 'ci'})
            g.savefig(save_folder / f'{kind}-{feature}-genotype-isday-{"avgch" if collapse else "no avgch"}.png', dpi=300)
    
    for feature in [x for x in constants.BAND_FEATURES if x not in exclude]:
        logger.info(f"Generating {kind} plot for {feature} with genotype grouping")
        g = ep.plot_catplot(feature, groupby=['animal', 'genotype'], 
                            x='genotype',
                            hue='band',
                            kind=kind, collapse_channels=True, average_groupby=True, 
                            catplot_params={'dodge': True, 'col': None, 'errorbar': 'ci'})
        g.savefig(save_folder / f'{kind}-{feature}-genotype-avgch.png', dpi=300)
        logger.info(f"Generating {kind} plot for {feature} with genotype and isday grouping")
        g = ep.plot_catplot(feature, groupby=['animal', 'genotype', 'isday'], 
                            x='genotype',
                            col='isday',
                            hue='band',
                            kind=kind, collapse_channels=True, average_groupby=True, 
                            catplot_params={'dodge': True, 'errorbar': 'ci'})
        g.savefig(save_folder / f'{kind}-{feature}-genotype-isday-avgch.png', dpi=300)

    logger.info(f"Generating {kind} plot for cohere with genotype grouping")
    g = ep.plot_catplot('cohere', groupby=['animal', 'genotype'], x='genotype', hue='band', kind=kind, collapse_channels=True, average_groupby=True, 
                        catplot_params={'dodge': True, 'col': None, 'errorbar': 'ci'})
    g.savefig(save_folder / f'{kind}-cohere-genotype-avgch.png', dpi=300)
    logger.info(f"Generating {kind} plot for cohere with genotype and isday grouping")
    g = ep.plot_catplot('cohere', groupby=['animal', 'genotype', 'isday'], x='genotype', col='isday', hue='band', kind=kind, collapse_channels=True, average_groupby=True, 
                        catplot_params={'dodge': True, 'errorbar': 'ci'})
    g.savefig(save_folder / f'{kind}-cohere-genotype-isday-avgch.png', dpi=300)
    logger.info(f"Generating {kind} plot for pcorr with genotype grouping")
    g = ep.plot_catplot('pcorr', groupby=['animal', 'genotype'], x='genotype', kind=kind, collapse_channels=True, average_groupby=True, 
                        catplot_params={'dodge': kind == 'swarm', 'col': None, 'errorbar': 'ci'})
    g.savefig(save_folder / f'{kind}-pcorr-genotype-avgch.png', dpi=300)
    logger.info(f"Generating {kind} plot for pcorr with genotype and isday grouping")
    g = ep.plot_catplot('pcorr', groupby=['animal', 'genotype', 'isday'], x='genotype', col='isday', kind=kind, collapse_channels=True, average_groupby=True, 
                        catplot_params={'dodge': kind == 'swarm', 'errorbar': 'ci'})
    g.savefig(save_folder / f'{kind}-pcorr-genotype-isday-avgch.png', dpi=300)
# !SECTION

# SECTION HEATMAP PLOTS
# logger.info("Generating heatmap for pcorr with animal grouping")
# g = ep.plot_heatmap('pcorr', groupby='animal')
# g.savefig(save_folder / 'AAAA every animal pcorr.png', dpi=300)
# logger.info("Generating heatmap for cohere with animal grouping")
# g = ep.plot_heatmap('cohere', groupby='animal')
# g.savefig(save_folder / 'AAAA every animal cohere.png', dpi=300)

# logger.info("Generating heatmap for cohere with genotype and isday grouping")
# g = ep.plot_heatmap('cohere', groupby=['genotype', 'isday'])
# g.savefig(save_folder / 'cohere-genotype-isday-matrix-False.png', dpi=300)
# logger.info("Generating heatmap for cohere with genotype and band grouping")
# g = ep.plot_heatmap('cohere', groupby='genotype', col='band', row='genotype')
# g.savefig(save_folder / 'cohere-genotype-band-matrix-False.png', dpi=300)

# logger.info("Generating heatmap for pcorr with genotype and isday grouping")
# g = ep.plot_heatmap('pcorr', groupby=['genotype', 'isday'])
# g.savefig(save_folder / 'pcorr-genotype-isday-matrix-False.png', dpi=300)
# logger.info("Generating heatmap for pcorr with genotype grouping")
# g = ep.plot_heatmap('pcorr', groupby='genotype')
# g.savefig(save_folder / 'pcorr-genotype-matrix-False.png', dpi=300)
# !SECTION

# SECTION DIFF HEATMAP PLOTS
# for feature in [x for x in constants.MATRIX_FEATURES if x not in exclude]:
#     logger.info(f"Generating diff heatmap for {feature} with WT-day baseline")
#     g = ep.plot_diffheatmap(feature, groupby=['genotype', 'isday'], baseline_key=('MWT', True))
#     g.savefig(save_folder / f'diff-{feature}-WT-day.png', dpi=300)
#     logger.info(f"Generating diff heatmap for {feature} with WT baseline")
#     g = ep.plot_diffheatmap(feature, groupby=['genotype', 'isday'], baseline_key='MWT', baseline_groupby='genotype')
#     g.savefig(save_folder / f'diff-{feature}-WT.png', dpi=300)
#     logger.info(f"Generating diff heatmap for {feature} with day baseline")
#     g = ep.plot_diffheatmap(feature, groupby=['genotype', 'isday'], baseline_key=(True,), baseline_groupby='isday')
#     g.savefig(save_folder / f'diff-{feature}-day.png', dpi=300)

# logger.info("Generating diff heatmap for cohere with WT baseline and day grouping")
# g = ep.plot_diffheatmap('cohere', groupby=['genotype', 'isday'], baseline_key='MWT', baseline_groupby='genotype', col='band', row='isday', remove_baseline=True)
# g.savefig(save_folder / 'diff-band-cohere-WT-day.png', dpi=300)
# logger.info("Generating diff heatmap for cohere with WT baseline")
# g = ep.plot_diffheatmap('cohere', groupby='genotype', baseline_key='MWT', baseline_groupby='genotype', col='band', row='genotype', remove_baseline=True)
# g.savefig(save_folder / 'diff-band-cohere-WT.png', dpi=300)
# !SECTION

# SECTION QQ PLOTS
# for feature in [x for x in constants.LINEAR_FEATURES if x not in exclude]:
#     # logger.info(f"Generating QQ plot for {feature} with animal and channel grouping")
#     # g = ep.plot_qqplot(feature, ['animal'], row='animal', col='channel', height=3)
#     # g.savefig(save_folder / f'qq-{feature}-animal-channel.png', dpi=300)
#     logger.info(f"Generating QQ plot for {feature} with genotype and channel grouping")
#     g = ep.plot_qqplot(feature, ['genotype'], row='genotype', col='channel', height=3)
#     g.savefig(save_folder / f'qq-{feature}-genotype-channel.png', dpi=300)
# !SECTION

"""
sbatch --mem 200GB -c 10 -t 24:00:00 ./notebooks/examples/pipeline.sh ./notebooks/examples/pipeline-warfig.py
"""