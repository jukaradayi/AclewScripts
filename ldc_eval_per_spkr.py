#!/usr/bin/env python
#
# author = julien karadayi

import intervaltree as it
import os
import argparse
import ipdb

"""
    After having computed a LDC speech activity detection on a corpus, and
    converted the results to rttm format, take gold rttm with annotation at
    the speaker level, try attributing a speaker label for each detect segment
    in the input.
    After having done that, evaluate the system's output for each speaker,
    to see it's performance per speaker (e.g. see if some speakers are detected
    really well, and others really badly).


    INPUT
    - path to the folder containing the outputs of the SAD system, in RTTM
      format
    - path to the folder containing the gold per speaker.

    The files in the gold and the SAD system output should have their name in
    the following way :
        for a wav file
            wav_name.wav,
        the SAD output folder should contain 1 file named
            wav_name.rttm,
        and the gold should contain 1 or several files
            wav_name_spkr1.rttm, ..., wav_name spkrN.rttm
        where spkr1, spkr2, ..., spkrN are the names of the speakers in the wav
        file.
"""


def parser_rttm(rttm):
    """
    take the path to an rttm file in input,
    and output the list of segments of speech
    for the corresponding speaker/wav in the form
    [ (on1, off1), (on2, off2), ..., (onN, offN)]
    """
    sad_intervals = []
    with open(rttm, 'r') as fin:
        SAD = fin.readlines()

        for line in SAD:
            _, wav, _, on, dur, _, _, SAD, _ = line.split('\t')
            if SAD == "speech":
                sad_intervals.append((float(on), float(on) + float(dur)))
    return sad_intervals


def eval_spkr_in_ldc(ldc_fold, gold_folder, gold_list_files, output):
    """ for each file in the ldc output, get all
    the gold files for each speaker
    """
    # loop over files in ldc folder
    for fin in os.listdir(ldc_fold):
        print(fin)
        # get base name
        basename = fin.split('.')[0]

        # evaluate against transcriptions from Mother (MOT*, or
        # in some cases FA1 if MOT* doesn't exist), and Child (CHI*)
        list_gold_MOT = [gold for gold in gold_list_files
                         if (gold.startswith(basename) and "MOT" in gold)]
        # ipdb.set_trace()
        if len(list_gold_MOT) == 0:
            list_gold_MOT = [gold for gold in gold_list_files
                             if (gold.startswith(basename) and "FA1" in gold)]
        list_gold_CHI = [gold for gold in gold_list_files
                         if (gold.startswith(basename) and "CHI" in gold)]

        list_gold_spkr = list_gold_MOT + list_gold_CHI

        # for each SAD output file, attribute speaker label to the
        # detected speech intervals
        attribute_spkrs_in_ldc(os.path.join(ldc_fold, fin),
                               gold_folder, list_gold_spkr,
                               output, basename)
    return


def attribute_spkrs_in_ldc(fin, gold_folder, list_gold_spkr, output, basename):
    """  for each annotated speaker in the gold, look for the
    intervals detected by the ldc system that overlap,
    and label those detected with the name of the speaker in the gold.
    """

    ldc_seg = parser_rttm(fin)
    ldc_tree = it.IntervalTree.from_tuples(ldc_seg)

    for gold in list_gold_spkr:
        # recover speaker name from gold filename
        spkr_name = os.path.basename(gold).split('.')[0].split('_')[-1]
        gold_seg = parser_rttm(os.path.join(gold_folder, gold))

        # find overlaps between segments in ldc_seg and gold_seg
        # To find overlapping segment, we construct and interval tree
        # with the LDC output, and query with the gold segments to attribute
        # a speaker to the segments

        ov_intervals = set()
        for bg, ed in gold_seg:
            _interv = ldc_tree.search(bg, ed)

            ov_intervals = ov_intervals.union(_interv)
        ldc_spkr_id = [(i[0], i[1]) for i in ov_intervals]

        write_rttm(ldc_spkr_id, output, basename, spkr_name)
    return


def write_rttm(intervals, output, basename, spkr_name):
    """ take a list of intervals of speech for a given
    speaker, and write a rttm file
    """
    output = 'tmp'
    output_file_name = os.path.join(output,  '_'.join([basename, spkr_name]))\
        + '.rttm'

    # don't write any file if it doesn't contain any interval
    if len(intervals) == 0:
        print('did return')
        return

    print('did not return')

    with open(output_file_name, 'w') as fout:
        for i in intervals:
            on, off = i[0], i[1]
            fout.write(u'SPEAKER\t{}\t1\t{}\t{}\t<NA>\t<NA>\tspeech\t<NA>\n'
                       .format(basename, on, off - on))
    return


if __name__ == '__main__':
    command_example = '''example:
    python ldc_eval_per_speaker.py /home/julien/gold /home/julien/ldc
    '''
    parser = argparse.ArgumentParser(epilog=command_example)
    parser.add_argument('gold_folder', metavar='gold',
                        help='gold folder')
    parser.add_argument('SAD_folder', metavar='SAD',
                        help='SAD outputs folder')
    parser.add_argument('output', metavar="output",
                        help='folder in which to write the per-speaker SAD')
    args = parser.parse_args()

    # if output folder doesn't exist, create it
    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    gold_list_files = os.listdir(args.gold_folder)
    eval_spkr_in_ldc(args.SAD_folder, args.gold_folder,
                     gold_list_files, args.output)
