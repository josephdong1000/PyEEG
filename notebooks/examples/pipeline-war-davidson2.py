import os
import sys
from pathlib import Path
import time
import tempfile
import logging
import json

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import mne
from dask_jobqueue import SLURMCluster
from dask.distributed import Client
from django.utils.text import slugify

from pythoneeg import core
from pythoneeg import visualization
from pythoneeg import constants

core.set_temp_directory('/scr1/users/dongjp')

# SECTION 1: Set up clusters
cluster_window = SLURMCluster(
        cores=20,
        memory='100GB',
        walltime='48:00:00',
        interface=None,
        scheduler_options={'interface': 'eth1'}, # Look at `nmcli dev status` to find the correct interface
        job_extra_directives=['--output=/dev/null',
                              '--error=/dev/null']
    )
print(f"\n\n\tcluster_window.dashboard_link: {cluster_window.dashboard_link}\n\n")
cluster_spike = SLURMCluster(
        cores=1,
        memory='100GB',
        processes=1,
        walltime='12:00:00',
        interface=None,
        scheduler_options={'interface': 'eth1'}, # Look at `nmcli dev status` to find the correct interface
        job_extra_directives=['--output=/dev/null',
                              '--error=/dev/null']
    )
print(f"\n\n\tcluster_spike.dashboard_link: {cluster_spike.dashboard_link}\n\n")
cluster_window.scale(10)
cluster_window.wait_for_workers(10)
cluster_spike.adapt(maximum_jobs=10)
# !SECTION

# SECTION 2: Compute windowed analysis
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG, stream=sys.stdout, force=True)
logger = logging.getLogger()

base_folder = Path('/mnt/isilon/marsh_single_unit/PythonEEG')
data_parent_folder = Path('/mnt/isilon/marsh_single_unit/PythonEEG Data Bins')
data_folders_to_animal_ids = {
    "" : ['A5', 'A10', 'F22', 'G25', 'G26', 'N21', 'N22', 'N23', 'N24', 'N25']
    # "" : ['A5']
}
constants.SORTING_PARAMS['freq_min'] = 60
constants.SORTING_PARAMS['freq_max'] = 400

for data_folder, animal_ids in data_folders_to_animal_ids.items():
    for animal_id in animal_ids:

        with Client(cluster_window) as client:
            client.run(lambda: os.system(f"pip install -e {base_folder}"))
            
            # SECTION 1: Find bin files
            ao = visualization.AnimalOrganizer(data_parent_folder / data_folder, animal_id,
                                        mode="concat", 
                                        assume_from_number=True,
                                        skip_days=['bad'],
                                        lro_kwargs={'mode': 'bin',
                                                    'multiprocess_mode': 'dask',
                                                    'overwrite_rowbins': True},
            )
            # !SECTION

            # SECTION 2: Make WAR
            war = ao.compute_windowed_analysis(['all'], multiprocess_mode='dask')
            # !SECTION

        # SECTION 3: Make SARs, save SARs and load into WAR
        with Client(cluster_spike) as client:
            client.run(lambda: os.system(f"pip install -e {base_folder}"))
            
            sars = ao.compute_spike_analysis(multiprocess_mode='dask')
            for sar in sars:
                sar.save_fif_and_json(base_folder / 'notebooks' / 'tests' / 'sars-60-400' / f'{data_folder} {slugify(sar.animal_day, allow_unicode=True)}', overwrite=True) # animal_day not unique for Sox5 rec sessions, so add bin_folder_name
            war.read_sars_spikes(sars)
        # !SECTION

        # SECTION 4: Save WARs and cleanup
        war.save_pickle_and_json(base_folder / 'notebooks' / 'tests' / 'wars-60-400' / f'{data_folder} {animal_id}')
        del war
        del sars
        # !SECTION
# !SECTION

"""
sbatch --mem 200G -c 4 -t 48:00:00 /mnt/isilon/marsh_single_unit/PythonEEG/notebooks/examples/pipeline.sh /mnt/isilon/marsh_single_unit/PythonEEG/notebooks/examples/pipeline-war-davidson2.py
"""