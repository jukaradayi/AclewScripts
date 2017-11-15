# SCRIPTS ACLEW
this folder contains 4 scripts (as of the 13th of november): 

extract_1_minute.py:
====================
This script extracts the 1 minute that was transcribed from the wav 
and the corresponding textgrid. In the textgrid, it changes the timestamps 
to have them in reference to the now 1 minute long wav.

lab2rttm.sh:
============
This script comes from the JSALT Toolbox from Alex Cristia, 
and converts SAD output in .lab format (such as LDC outputs), and converts
them in rttm format (needed for dscore package, to evaluate the Speech activity detection)

merge_folders.py:
================
This script merges the folder ending in "_1" and thos ending in "_2", and corrects
the timestamps in the names of wav files.

textGrid2Rttm.py:
================
Take a text grid and output a rttm file with the annotations.
Several rttm files are in output: 
-One for all speakers with no distinction, indicating speech sections
-One rttm file per speaker with speech sections only for THIS speaker.

####
DECISIONS
####
To write these scripts, I encountered some problems and took arbitrary decisions to overcome them.

- The folders "vanuatu[...]" do not follow the same nomenclature as the other ones for the way
  they are built, so I didn't treat them

- Same goes for the ones that end in "test"

- Some annotation started earlier than the 180s timestamp, and ended after the 240 timestamp. 
  Even if in those cases, I only kept the wavs between 180s and 240s. I took the annotations 
  for these timestamps, and threw out any annotations that was outside (it mainly occured 
  for example when there's a background noise all over the wav and the annotator put the 
  annotation over all the wav)




