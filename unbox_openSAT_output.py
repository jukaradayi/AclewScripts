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
"""

import pickle
import numpy 

with open('confidence.pkl', 'rb') as fin:
    u = pickle._Unpickler(fin)
    u.encoding = 'latin1'
    p = u.load()
    
for key in p.keys():
    post = p[key]
