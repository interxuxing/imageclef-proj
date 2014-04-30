__author__ = 'xuxing'


"""
    find_nearest_synset.py is a demo script to find the nearest synset (most similar) in ImageCLEF2014, given an input tag
"""


import imageclef_fileparser as fileparser
import imageclef_settings as settings
import numpy as np
from nltk.corpus import wordnet as wn
from itertools import product

def compare(word1, word2):
    ss1 = wn.synsets(word1)
    ss2 = wn.synsets(word2)

    if len(ss1) == 0 or len(ss2) == 0:
        return 0
    else:
        return max(s1.path_similarity(s2) for (s1, s2) in product(ss1, ss2))


def find_nearest_synset(in_tag, in_taglist):
    """
        function find_nearest_synset
          for given in_tag, find its nearest (most similar) tag in in_taglist, return its tag name

        in_tag is a string
        in_taglist is a big list which is produced from   fileparser.parse_imageclef_concepts_wn
    """

    # process the input parameters
    concept_tag = in_taglist[0]
    concept_type = in_taglist[1]
    concept_sense = in_taglist[2]

    numConcepts = len(concept_tag)

    # new a distance matrix
    dist_score = np.zeros([1, numConcepts])

    #loop to calculate the distance between in_tag and each concept
    syn_in_tag = wn.synsets(in_tag)[0]
    for idx in range(numConcepts):
        offset = concept_sense[idx] - 1
        syn_concept = wn.synsets(concept_tag[idx])[offset]

        path_sim = syn_in_tag.path_similarity(syn_concept)
        if path_sim == None:
            path_sim = 0
        # path_sim = compare(in_tag, concept_tag[idx])
        dist_score[0][idx] = path_sim
    # sort in column and flip to descending order
    indices = np.argsort(dist_score, axis=1)
    sorted_indices = np.fliplr(indices)

    return concept_tag[sorted_indices[0][0]]


if __name__ == '__main__':
    # load imageclef2014 tag set
    # read wordnet concetps from devel_dict_wn.txt file
    Imageclef_concepts = fileparser.parse_imageclef_concepts_wn(settings.SRC_DATA_DIR + 'devel_dict_wn.txt')

    while True:
        in_tag = raw_input('please input a tag: ')
        if in_tag == 'q':
            break

        out_tag = find_nearest_synset(in_tag, Imageclef_concepts)
        print 'For input tag: %s, its similar tag in Imageclef is %s' % (in_tag, out_tag)


    print 'finished!'