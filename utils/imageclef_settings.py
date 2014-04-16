__author__ = 'xuxing'

"""
    imageclef_settings.py is a file include all kinds of settings in my Imageclef project
"""


# first give some initial configuration about path, etc
# give some initial configuration
ENV = 1 # 1:laptop  2:desktop
SET = 1 # 1:develop 2:test


if ENV == 1: # laptop
    SRC_DATA_DIR = 'C:\\workspace\\my tools\\git code\\imageclef-proj\\data\\'
    if SET == 1:
        DST_DATA_DIR = 'C:\\workspace\\my tools\\git code\\imageclef-proj\\data\\devel_result\\'
    else:
        DST_DATA_DIR = 'C:\\workspace\\my tools\\git code\\imageclef-proj\\data\\test_result\\'
    WORDNET_IC_DIR = 'C:\\Users\\xuxing\\AppData\\Roaming\\nltk_data\\corpora\\wordnet_ic\\'
else: # desktop
    SRC_DATA_DIR = 'D:\\workspace-limu\\image-annotation\\datasets\\imageclef2014\\imageclef-proj\\data\\'
    if SET == 1:
        DST_DATA_DIR = 'D:\\workspace-limu\\image-annotation\\datasets\\imageclef2014\\imageclef-proj\\data\\devel_result\\'
    else:
        DST_DATA_DIR = 'D:\\workspace-limu\\image-annotation\\datasets\\imageclef2014\\imageclef-proj\\data\\test_result\\'
    WORDNET_IC_DIR = 'C:\\Users\\LIMU\\AppData\\Roaming\\nltk_data\\corpora\\wordnet_ic\\'


SIMILARITY_MEASURE = ['path_similarity', 'lch_similarity', 'wup_similarity', \
                      'res_similarity', 'jcn_similarity', 'lin_similarity']