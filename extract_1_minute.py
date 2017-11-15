#!/usr/bin/env python
#
# author = julien karadayi
# extract the minute that is transcribed from the text grids and 
# the wav. Do this using sox and praatio.

import os
from praatio import tgio
import subprocess
import shlex
import argparse
import sys
import ipdb

def extract_from_tg(input_folder, output_folder):
    # create output directory
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    
    for fin in os.listdir(input_folder):
        if fin.startswith('vanuatu'):
            continue
        if not fin.endswith('_m1.TextGrid'):
            continue
        print 'treating file {}'.format(fin)
        # output name
        child, date, time, m1 = fin.split('.')[0].split('_')
        fout = '_'.join([child, date, str( int(time) + 180), m1]) + ".TextGrid"

        # read text grid
        tg = tgio.openTextgrid( os.path.join(input_folder, fin) )
        
        # shift all timestamps from 180 s
        copy_of_tg = tg.editTimestamps(-180)

        # edit maxTimestamps for cut at 60 seconds
        copy_of_tg.maxTimestamp = 60

        # write TextGrid
        #try:
        copy_of_tg.save( os.path.join(output_folder, fout))
        #except:
        #    #ipdb.set_trace()
        #    for key in copy_of_tg.tierNameList:
        #        for intervals in copy_of_tg.tierDict[key].entryList:
        #            
        #            #if intervals[1] > 60:
        #            #    ipdb.set_trace()
        #            #    #intervals[1] = 60
        #            print intervals
        #    ipdb.set_trace()
        # extract minute from wav 
        # remove suffix and " _m1", add .wav
        _wav_in  = fin.split('.')[0][:-3] + '.wav'
        wav_in = os.path.join(input_folder, _wav_in)
        
        child, date,  time = _wav_in.split('.')[0].split('_')
        #_wav_out = fin.split('.')[0][:-3] + '_trimmed.wav'
        _wav_out = '_'.join([child, date, str(int(time) + 180)])
        wav_out = os.path.join(output_folder, _wav_out) + '.wav'
        
        # export command via subprocess
        command = ' '.join(['sox', wav_in, wav_out, 'trim 180 60'])
        print command
        process = subprocess.Popen( shlex.split(command),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        
        stdout,stderr=process.communicate()


#print " befor extract"
#extract_from_tg( inp )
if __name__ == '__main__':
    
    command_example = '''example:
    
    python merge_folders.py /home/julien/en_cours /home/julien/output

    '''
    parser = argparse.ArgumentParser(epilog=command_example)
    parser.add_argument('input_folder', metavar='input', 
            help='Input folder')
    parser.add_argument('output_folder', metavar='output',
            help='output folder')
    args = parser.parse_args()
    
    if not os.path.isdir(args.output_folder):
        os.makedirs(args.output_folder)
    for fold in os.listdir(args.input_folder):
        extract_from_tg( os.path.join(args.input_folder, fold), os.path.join( args.output_folder, fold ) )

