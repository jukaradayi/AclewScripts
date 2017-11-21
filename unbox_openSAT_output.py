#!/usr/bin/env python
#
# author = julien karadayi

"""
    read OpenSAT output.

    OpenSAT classifies the wav in 18 classes:
        0   background  6   music   12  noise_ongoing
        1   speech      7   human   13  noise_pulse
        2   speech_ne   8   cheer   14  noise_tone
        3   mumble      9   crowd   15  noise_nature
        4   singing     10  animal  16  white_noise
        5   music_sing  11  engine  17  radio
    and writes the output in a pickle.
"""

import pickle
import numpy
import ipdb
import subprocess
import shlex
import argparse
import os


def open_pickle(folder):
    """Open pickle file found in folder
    and output its content.
    """
    # if file ends in .gz, unzip it, else read it directly
    if os.path.isfile(os.path.join(folder, 'confidence.pkl.gz')):
        cmd = "gunzip {}".format(os.path.join(folder, 'confidence.pkl.gz'))
        subprocess.call(shlex.split(cmd))

    with open(os.path.join(folder, 'confidence.pkl'), 'rb') as fin:
        u = pickle._Unpickler(fin)
        u.encoding = 'latin1'
        p = u.load()
    return p


def speech_activity_detection(classif):
    """Take OpenSat output matrix and
    retreive Speech Activity Detection from the
    column 1 and 2 (which correspond to english and non english)
    """

    # get the name of the speaker by getting the name 
    # of the folder.
    # TODO : check if there's a prettier way of doing this ? 
    # instead of checking if last char is "/"
    # if folder.endswith('/'):
    #     basename = os.path.basename(folder[:-1])
    # else:
    #     basename = os.path.basename(folder)
    # assert basename != '', 'ERROR, basename is empty'

    for key in classif.keys():
        # there should be only 1 key per file
        post = classif[key]

    # find out best classes
    best_classes = numpy.zeros((post.shape[0],2))

    # first column is for timestamps
    best_classes[:,0] = numpy.linspace(-2, 59.9, 620)

    # at each timestamp, take class with highest probability.
    # TODO : should refine this with a threshold
    # to see for cases where there's not much sound
    best_classes[:,1] = numpy.argmax(post, axis=1)
    # ipdb.set_trace()
    # keep only 5 first classes and class 7 human
    # reminder : 
    #    0   background 
    #    1   speech 
    #    2   speech_ne 
    #    3   mumble 
    #    4   singing 
    #    7   human 

    best_classes[
        numpy.logical_and(best_classes[:,1] > 4,
                          best_classes[:,1] != 7),1] = 0
    return best_classes

def classes2rttm(best_classes, basename, output_folder):
    """
    Input : 
        array containing, for each timestamp, the best class
    Output: 
        a text file, in rttm format, indicating speech sections
    """

    out_file = os.path.join(output_folder, basename + '.rttm')
    with open(out_file, 'w') as fout:
        prev_class = -10
        for time, classes in best_classes:
            classes = max(0, min(1, classes))

            # 3 cases: first window, window in the middle, last window
            if numpy.isclose(time, 0):
                # keep track of classes only as 1 for speech or 
                # 0 for non speech
                prev_class = classes
                if prev_class == 1:
                    prev_onset = time
            elif time > 0:
                if (prev_class == 1 and classes == 0):
                    fout.write(u'SPEAKER\t{}\t1\t{}\t{}\t'
                           '<NA>\t<NA>\tspeech\t<NA>\n'.format(
                               basename, prev_onset, time - prev_onset))
                elif (prev_class == 0 and classes == 1):
                    prev_onset = time
                    prev_class = classes
                else:
                    prev_class = classes


            elif time == best_classes[-1,0]:
                # check if treating last window, and if 
                # it's the case, write output if needed
                 if (prev_class == 1 and classes == 0):
                    fout.write(u'SPEAKER\t{}\t1\t{}\t{}\t'
                           '<NA>\t<NA>\tspeech\t<NA>\n'.format(
                               basename, prev_onset, time - prev_onset))

                 elif (prev_class == 0 and classes == 1):
                     # weird case, should not happen but just in case :
                     # if speech is detected ONLY in the last frame, write it
                     fout.write(u'SPEAKER\t{}\t1\t{}\t{}\t'
                           '<NA>\t<NA>\tspeech\t<NA>\n'.format(
                               basename, time, 0.1))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input',
                        help='input folder')
    parser.add_argument('output', metavar='input',
                        help='output folder in which we write the RTTM')
    args = parser.parse_args()
    
    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    # tree is input_folder/
    #            spkr_names/
    #                wav_names/
    #                    confidence.pkl.gz
    for speakers in os.listdir(args.input):
        for wav_name in os.listdir(os.path.join(args.input, speakers)):
            # open pickles
            matrix_fold = os.path.join(args.input, speakers, wav_name)
            post = open_pickle(matrix_fold)
            
            # go from post to classes
            classes = speech_activity_detection(post)
    
            # write RTTM indicating speech/non speech
            classes2rttm(classes, wav_name, args.output)
