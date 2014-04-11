__author__ = 'xuxing'

"""
    This is a script to check the program I have written.
"""

import cPickle
import numpy as np


class ImgEntry:
    def __init__(self):
        self.imgname = ''
        self.imgtags = {} # dict, predict tag with score, tags in overfeat
        self.imgmaptags = {} # dict, mapped tags with score, tags in imageclef


def generate_predict_results(res_ImgEntries, res_clef_conceptlists, out_predict_filename):
    """
        function generate_predict_results generates the standard fileformat which can be directly parsed by Imageclef
            community.

        The output file format is (in each line):
        [image_identifier] [score_for_concept_1] [decision_for_concept_1] ... [score_for_concept_M] [decision_for_concept_M]

        Input:
            res_ImgEntries is a list, each entry is a dictionary, with the mapped tags in Imageclef concepts, {tag:score}
            res_clef_conceptlists is a [[imagenames], [imageconceptlists]] list type, parsed from ***_conceptlists.txt file
            out_predict_filename is the final output file need to be stored

        Return:
            None

    """

    # intialnize
    fid = open(out_predict_filename, 'w')

    imgNames = res_clef_conceptlists[0] # a simple list
    imgConcepts = res_clef_conceptlists[1] # a list contains sub lists

    # for each image in res_clef_conceptlists, we search it in res_map_tags
    #   if the concept of conceptlists exists in res_map_tags, give score and mask to it

    for this_imgIdx in range(len(imgNames)):
        this_imgName = imgNames[this_imgIdx]
        this_imgConcepts = imgConcepts[this_imgIdx]

        outputformatList = [this_imgName]

        this_imgEntry = res_ImgEntries[this_imgIdx] #ImgEntry
        img_map_tags = this_imgEntry.imgmaptags

        # loop for the concepts for this image
        for concept_name in this_imgConcepts:
            score_for_concept = 0
            decision_for_concept = 0
            if concept_name in img_map_tags.keys():
                score_for_concept = img_map_tags[concept_name]
                if score_for_concept > 0: # remove the 0 score for sunrise/sunset
                    decision_for_concept = 1

            # set the output format
            this_concept_str = ('%f %d' % (score_for_concept, decision_for_concept))
            outputformatList.append(this_concept_str)

        # now merge the outputformatList to get a final output string
        outputformatStr = ' '.join(outputformatList)

        # write it to file
        fid.write(outputformatStr + '\n')

    fid.close()


def generate_imageclef_evalfiles(in_dict_file, in_ImgEntries, \
                                 out_dec_file, out_score_file):
    """
        function generate_imageclef_evalfiles is to produce 2 evaluation txt files for the matlab script
            evalannotat.m used.

        Input:
            in_dic_file is the dev_dict.txt or test_dict_txt, which contains the tags in dev/test set
            in_ImgEntries contains all ImgEntry objects for image in dev/test set
            out_dec_file is the fullpath output decision file, only contains 0/1 values
            out_score_file is the fullpath output score file, contains confidence scores for each tag to each image
    """

    fid_dict = open(in_dict_file, 'r')
    fid_dec = open(out_dec_file, 'w')
    fid_score = open(out_score_file, 'w')

    # construct the groundtruth taglist
    Tags = []
    for line in fid_dict.readlines():
        Tags.append(line.strip('\n'))

    # initial 2 matrix for dec and score
    NumTags = len(Tags)
    NumImgs = len(in_ImgEntries)
    matDec = np.zeros((NumImgs, NumTags))
    matScores = np.zeros((NumImgs, NumTags))

    # for each entry in ImgEntries, write to dec/score files
    for entry_idx in range(NumImgs):
        entry = in_ImgEntries[entry_idx]
        map_tags = entry.imgmaptags

        for tag_idx in range(NumTags):
            tag_name = Tags[tag_idx]
            tag_dec = 0
            tag_score = 0

            if tag_name in map_tags.keys():
                tag_score = map_tags[tag_name]
                if tag_score > 0:
                    tag_dec = 1

            matDec[entry_idx][tag_idx] = tag_dec
            matScores[entry_idx][tag_idx] = tag_score

    # write 2 mat to txt files
    np.savetxt(fid_dec, matDec, fmt='%d')
    np.savetxt(fid_score, matScores, fmt='%f')

    fid_dict.close()
    fid_dec.close()
    fid_score.close()







if __name__ == '__main__':
    SRC_DATA_DIR = 'C:\\workspace\\my tools\\git code\\imageclef-proj\\data\\'
    DST_DATA_DIR = SRC_DATA_DIR


    f = open(SRC_DATA_DIR + 'temp.data')
    obj = cPickle.load(f)

    ImgEntries = obj[0]
    Clef_conceptslist = obj[1]

    # generate the predict results
    # generate_predict_results(ImgEntries, Clef_conceptslist, (DST_DATA_DIR+'devel_predict_results.txt'))

    # generate the adaptive files for evaluation used
    dec_file = 'devel_predict_decision.txt'
    score_file = 'devel_predict_scores.txt'

    generate_imageclef_evalfiles((SRC_DATA_DIR+'devel_dict.txt'), ImgEntries, \
        (SRC_DATA_DIR+dec_file), (SRC_DATA_DIR+score_file))

    print 'finished!'


