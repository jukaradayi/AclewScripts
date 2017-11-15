#!/usr/bin/env python
#
# author = Julien Karadayi
#
# This script takes as input the path to the namibian corpus,
# merges the folders "_1" and "_2" (which correspond to the same speaker)
# and corrects the times in "_2" folders by adding
# the duration of the half day from "_1"

import os
import sys
import argparse
import ConfigParser
import subprocess
import shutil
import progressbar

def merge_folders(input_folder, output_folder):
    """
        This function takes as input the "en_cours" folder and merges 
        _1 and _2 folders, and adjusts the timestamps in the names of _2 folders' files.
        First : loop over all folders in input_folder, if folder ends by _1, copy as is 
        in output_folder, without the "_1", if it ends by "_2", copy in same folder, but add 
        52200 (mid day) + 3000 (5 minutes) + 1800 (3 minutes) to the timestamps in the names of all files.
    """

    # loop over content
    nb_files = len(os.listdir(input_folder))
    for ind, _fold in enumerate(os.listdir(input_folder)):
        print _fold
        if nb_files % max(1,ind) == 0:
            print "{} on {}".format(ind, nb_files)

        #input
        fold = os.path.join(input_folder, _fold)
        #output
        out_fold = os.path.join(output_folder, _fold[:-2])
        #if not (_fold.endswith('_1') or _fold.endswith('_2')):
        if not os.path.isdir(fold):
            # continue if not a folder
            continue
        if fold.endswith('test'):
            continue

        if fold.endswith('_1'):
            adjust_times(fold, out_fold, '_1')
        elif fold.endswith('_2'):
            adjust_times(fold, out_fold, '_2')
        else:
            out_fold = os.path.join(output_folder, _fold)
            shutil.copytree(fold, out_fold)

    return

def adjust_times(fold, output_fold, timePeriod):
    """
        take as input a folder that ends with '_2' and adjust the names of the files
    """
    
    # create output_fold if it doesn't exist
    if not os.path.isdir(output_fold):
        os.makedirs(output_fold)
    print output_fold 
    m_flag = 0
    for _fin in os.listdir(fold):
        
        if _fin == "CHI":
            # treating CHI folder afterwards
            continue
        # path to file
        fin = os.path.join(fold, _fin)

        # get timestamps
        name, suffix = _fin.split('.')
        try:
            child, date, _, time = name.split('_')
        except:
            m_flag = 1
            child, date, _, time, m = name.split('_')
        
        if timePeriod == "_1":
            new_time = time
        elif timePeriod == "_2":
            # cast to int and not float to avoid ".0"
            new_time =  str(int(time) + OFFSET)
        
        # new filename without suffix
        if m_flag == 0:
            new_name = "_".join([child, date, new_time])
        else:
            m_flag = 0
            new_name =  "_".join([child, date, new_time, m])
        
        # path to new file
        fout = os.path.join(output_fold, ".".join([new_name,suffix]))

        # finally copy file
        shutil.copy(fin, fout)
    
    # treat CHI folder
    if not os.path.isdir( os.path.join(output_fold, "CHI") ): # check if output CHI exists
        os.makedirs(os.path.join(output_fold, "CHI"))

    CHI_fold = os.path.join(output_fold, "CHI")
    for _fin in os.listdir(os.path.join(fold, 'CHI')):
        # path to file
        fin = os.path.join(fold, "CHI", _fin)

        # get timestamps
        name, suffix = _fin.split('.')
        
        if timePeriod == "_1":
            new_name = name
        elif timePeriod == "_2":
            new_name = str(int(name) + OFFSET)
 
        # path to new file
        fout = os.path.join(CHI_fold, ".".join([new_name,suffix]))
        
        # finally copy file
        shutil.copy(fin, fout)
       
    return
    

if __name__ == '__main__':
    
    command_example = '''example:
    
    python merge_folders.py /home/julien/en_cours /home/julien/output

    '''
    parser = argparse.ArgumentParser(epilog=command_example)
    parser.add_argument('input_folder', metavar='input', 
            help='Input folder')
    parser.add_argument('output_folder', metavar='output', 
            help='Output folder')
    args = parser.parse_args()

    # GLOBAL PARAMETERS
    OFFSET = 52200 + 300 + 1800 # offset to add to the names of the files
    # TODO: check file
    merge_folders(args.input_folder, args.output_folder)
