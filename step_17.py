# -*- coding: utf-8 -*-

import argparse
import os
import pandas as pd
import numpy as np
import copy
from tqdm import tqdm

from utils.utils import check_filesize


def define_alter_chr(drivers, primary):
    if drivers == 'DCL' and primary == -1.:
        return 'DCL'
    elif drivers == 'DCG' and primary == 1.:
        return 'DCG'
    else:
        return None


def step17(input_dir: str = 'data', output_folder_path: str = 'data'):

    print('Step 17', end='\t')

    primary_path = os.path.join(input_dir, 'Primary_whitelisted_chromosomes.tsv')
    drivers_path = os.path.join(input_dir, 'Chromosome_drivers_FDR5_cohorts.tsv')

    output_file_path = os.path.join(output_folder_path, 'Chromosome_drivers_FDR5.tsv')

    if not os.path.isdir(output_folder_path):
        os.makedirs(output_folder_path)

    if not os.path.isfile(output_file_path):

        primary_df = pd.read_csv(primary_path, sep='\t')
        drivers_df = pd.read_csv(drivers_path, sep='\t')

        drivers_df.index = drivers_df['Cancer_type']
        drivers_df = drivers_df.drop(columns=['Cancer_type'])

        primary_df_copy = copy.deepcopy(primary_df)

        print('this action could take 2-3 minutes')
        for ix, row in tqdm(primary_df.iterrows()):
            cohort_id = row['Type']
            primary_df_copy.iloc[ix, 3:] = list(map(lambda x, y: define_alter_chr(x, y),
                                                    drivers_df.loc[cohort_id], primary_df.iloc[ix, 3:]))

        primary_df_copy = primary_df_copy.drop(columns=['Type', 'Aneuploidy Score'])

        primary_df_copy['DCGs'] = (primary_df_copy.iloc[:, 1:] == 'DCG').sum(axis=1)
        primary_df_copy['DCLs'] = (primary_df_copy.iloc[:, 1:] == 'DCL').sum(axis=1)
        primary_df_copy['TCDs'] = primary_df_copy['DCGs'] + primary_df_copy['DCLs']

        primary_df_copy.to_csv(output_file_path, sep='\t', index=None)

    # Check for filesize
    size_pass = check_filesize(output_file_path)
    if not size_pass:
        raise Exception(f'file: {output_file_path} has wrong size, please check input file and do this step again')

    print('OK')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script takes ' +
                                                 'Primary_whitelisted_chromosomes.tsv and Chromosome_drivers_FDR5_cohorts.tsv files,'+ '\n' +
                                                 'defines driver events on chromosome level' + '\n' +
                                                 'and save the result in Chromosome_drivers_FDR5.tsv file' +
                                                 '\n' + 'if output folder does not exist, script will create it.')

    parser.add_argument('-i', '--input_dir', type=str, help='full path to input folder', default='data')
    parser.add_argument('-o', '--output_folder', type=str, help='full path to output folder', default='data')

    args = parser.parse_args()

    step17(args.input_dir, args.output_folder)
