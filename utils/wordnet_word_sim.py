__author__ = 'xuxing'

"""
    wordnet_word_sim.py is a simple script to calculate the similarity between different words
"""


from nltk.corpus import wordnet as wn
import numpy as np
import math
import sys

# first give some initial configuration about path, etc
# give some initial configuration
ENV = 1 # 1:laptop  2:desktop

if ENV == 2:
    SRC_DATA_DIR = 'C:\\workspace\\my tools\\git code\\imageclef-proj\\data\\'
    DST_DATA_DIR = SRC_DATA_DIR
else:
    SRC_DATA_DIR = 'D:\\workspace-limu\\image-annotation\\datasets\\imageclef2014\\imageclef-proj\\data\\'
    DST_DATA_DIR = 'D:\\workspace-limu\\cloud disk\\Dropbox\\limu\\submission\\ImageCLEF2014\\'
    WORDNET_IC_DIR = 'C:\\Users\\LIMU\\AppData\\Roaming\\nltk_data\\corpora\\wordnet_ic\\'

SIMILARITY_MEASURE = ['path_similarity', 'lch_similarity', 'wup_similarity', \
                      'res_similarity', 'jcn_similarity', 'lin_similarity']

from nltk.corpus import wordnet_ic
ic = wordnet_ic.ic(WORDNET_IC_DIR+'ic-brown.dat')

# define a structure of each image entry
class ImgEntry:
    def __init__(self):
        self.imgname = ''
        self.imgtags = {} # dict, predict tag with score, tags in overfeat
        self.imgmaptags = {} # dict, mapped tags with score, tags in imageclef

from operator import itemgetter
def sort_dict(d, reverse=False):
    return sorted(d.iteritems(), key=itemgetter(1), reverse=True)

def parse_overfeat_result(res_file):
    """
        parse_overfeat_result(res_file) is a function to parse the output tag results from overfeat lib

        in the res_file, for each image, it is formatted as:
        line1: imagename
        line2: tag(, tag ...) score1
        line3: tag(, tag ...) score2
        line4: tag(, tag ...) score3
        line5: tag(, tag ...) score4
        line6: tag(, tag ...) score5
        line7: tag(, tag ...) score6

        Return:
            A list contains entries, each entry is a ImgEntry object
    """

    DevImgs = []
    fid = open(res_file, 'r')
    STEP = 10 # each image 6 level tags
    count = 0 # count the level of each image
    isNewImage = True
    for line in fid.readlines():
        if isNewImage:
            # create a new image instance
            newImg = ImgEntry()
            # read 1st line image name
            newImg.imgname = line.strip('\n')

            isNewImage = False
        else:
            count += 1
            tags = line.strip('\n')
            d = split_tags(tags)
            newImg.imgtags.update(d)

        # if get end line (6-th line) for each image
        # reset the flags
        if count == STEP:
            isNewImage = True
            count = 0
            DevImgs.append(newImg)

    fid.close()
    return DevImgs

def split_tags(old_tags):
    """
        function split_tags is to split the tag format in overfeat outputfile
            to get (tag, socre) format
    """
    taglist = []

    list1 = old_tags.split(', ')
    # for last entry in list1, split it to get the score
    list2 = list1[-1].split(' ')
    score = list2[-1]

    # if the last tag has space, use _ replace it
    if len(list2) > 2:
        last_tag = '_'.join(list2[:-1])
    else:
        last_tag = list2[0]

    # now get other tags, use _ replace space
    for item in list1[:-1]:
        newtag = item.replace(' ', '_')
        taglist.append(newtag)

    # now add the last tag
    taglist.append(last_tag)

    # now allocate scores to taglist
    scorelist = [score] * len(taglist)

    # construct a dictionary with key = taglist, value = scorelist
    d = {k:v for k, v in zip(taglist, scorelist)}

    return d

def parse_imageclef_concepts_wn(res_file):
    """
        function parse_imageclef_concepts_wn parse the **_dict_wn.txt file, which has the format as:
            # concept	type	sense	wn_offset(3.0)
        and return a big list contains four sub list 'concept (str)', 'type (str)', 'sense (int)', 'wn_offset (str)'
    """
    concept_tag = []
    concept_type = []
    concept_sense = []
    concept_wn_offset = []
    imgNum = 0

    fid = open(res_file, 'r')
    for line in fid.readlines():
        # get the content (4 entries) in each line
        content = line.strip('\n').split('\t')
        imgNum += 1
        # allocate the 4 entries in content to corresponding list
        concept_tag.append(content[0])
        concept_type.append(content[1])
        concept_sense.append(int(content[2]))
        concept_wn_offset.append(content[3])

    # check the content ever correct
    # ??? how to check?

    concepts = [concept_tag, concept_type, concept_sense, concept_wn_offset]
    fid.close()
    return concepts

def parse_imageclef_conceptlists(res_file):
    """
        function parse_imageclef_conceptlists is used to parse **_conceptlists.txt file

        Input:
            res_file is **_conceptlists.txt
        Return:
            A big list contains 2 entries(list), 1st is a list with image_names, 2nd is a list with image_conceptlists
    """
    # initial return values
    image_names = [] # a simple list
    image_concepts = [] # a list contains sub lists

    fid = open(res_file, 'r')

    for line in fid.readlines():
        content = line.strip('\n').split()

        image_names.append(content[0])
        image_concepts.append(content[1:])

        # if 'sunrise/sunset' in list2:
        #     idx = list2.index('sunrise/sunset')
        #     list2.pop(idx)
        #     list2.append('sunrise')
        #     list2.append('sunset')

    image_conceptlists = [image_names, image_concepts]

    fid.close()
    return image_conceptlists


def map_tag_overfeat2imageclef(tag_overfeat, concepts_imageclef, mapping_type=0):
    """
        function map_tag_overfeat2imageclef is to calculate the similarity scores between tag predicted by Overfeat,
            and concepts in Imageclef,
            then use similarity socre sorting to select the most approximate tags in Imageclef as the final tag

        Input:
            tag_overfeat is a dictionayr {tag:score}
            concepts_imageclef is a big list contains 4 sub lists from function parse_imageclef_concepts_wn
            mapping_type is an int index 0,1,2 denotes the type of similarity measure, contains 'path_similarity', 'lch_similarity',
                        wup_similarity
        Return:
            function return a dictionary {tag:score} as the final prediction for one image
    """

    # initial returned mapped dictionary
    map_dict = {}

    # process the input parameters
    concept_tag = concepts_imageclef[0]
    concept_type = concepts_imageclef[1]
    concept_sense = concepts_imageclef[2]

    NumTagImageCLEF = len(concept_tag)
    NumTagOverfeat = len(tag_overfeat.keys())

    sim_score = np.zeros([NumTagOverfeat, NumTagImageCLEF])

    # calculate similarity score for each tag in tag_overfeat with concepts_imageclef
    for idx_old_tag in range(len(tag_overfeat.keys())):
        old_tag = tag_overfeat.keys()[idx_old_tag]
        old_tag_score = tag_overfeat[old_tag]

        # we get the most synset for old_tag
        synsets_old_tag = wn.synsets(old_tag)
        if len(synsets_old_tag) == 0:
            print ' now synsets retireved for Overfeat tag: ' + old_tag
            return -1

        syn_old_tag = synsets_old_tag[0]

        # now calculate similarity score with concepts in Imageclef
        for idx_new_tag in range(len(concept_tag)):
            new_tag = concept_tag[idx_new_tag]
            new_tag_sense = concept_sense[idx_new_tag] - 1 # keep index with list order

            synsets_new_tag = wn.synsets(new_tag)
            syn_new_tag = synsets_new_tag[new_tag_sense]
            # calculate path similarity
            path_sim = synsets_similarity(syn_old_tag, syn_new_tag, mapping_type)
            if path_sim is None:
                path_sim = 0
            sim_score[idx_old_tag][idx_new_tag] = float(old_tag_score) * path_sim

    # after we get the sim_score matrix, we sorted with descending order
    # numpy default sorted is ascending order
    mat = np.sort(sim_score, axis=1)   # axis=1 is column order, 0 is row order
    indices = np.argsort(sim_score, axis=1)

    # we need to fliplr the mat and indices to get the descending order
    sorted_sim_score = np.fliplr(mat)
    sorted_indices = np.fliplr(indices)

    # now we only preserve the 1st socre and indices (in column order)
    pred_sim_score = sorted_sim_score[:, 0]
    pred_indices = sorted_indices[:, 0]

    # then we get the concept tag in Imageclef from pred_indices, filling the final dictionary
    num_indices = np.size(pred_indices)

    for i in range(num_indices):
        tag_imageclef = concept_tag[pred_indices[i]]

        if tag_imageclef in map_dict.keys():
            map_dict[tag_imageclef] += pred_sim_score[i]
        else:
            map_dict[tag_imageclef] = pred_sim_score[i]

    # process for sunrise and sunset tags, merge it in map_dict
    map_dict['sunrise/sunset'] = 0
    if 'sunrise' in map_dict.keys():
        map_dict['sunrise/sunset'] += map_dict['sunrise']
        del map_dict['sunrise']
    if 'sunset' in map_dict.keys():
        map_dict['sunset'] += map_dict['sunset']
        del map_dict['sunset']

    return map_dict

def synsets_similarity(synset1, synset2, mapping_type):
    """
        synsets_similarity is a sub function to calculate similarity between 2 synsets using different mapping type
    """

    simi = 0
    try:
        if 0 == mapping_type:
            simi = synset1.path_similarity(synset2)
        elif 1 == mapping_type:
            simi = synset1.lch_similarity(synset2)
        elif 2 == mapping_type:
            simi = synset1.wup_similarity(synset2)
        elif 3 == mapping_type:
            simi = synset1.res_similarity(synset2, ic)
        elif 4 == mapping_type:
            simi = synset1.jcn_similarity(synset2, ic)
        elif 5 == mapping_type:
            simi = synset1.lin_similarity(synset2, ic)
        else:
            print 'error mapping_type, it should be an integer 0,1,2'
            return -1
    except Exception, e:
        simi = 0

    if simi is None:
        simi = 0
    return simi

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
    for newEntry in res_ImgEntries:
        # each item is a dictionary type
        image_name = newEntry.imgname # a str
        image_map_tags = newEntry.imgmaptags # a dict


        outputformatList = []
        # if this image exists, then output it using standard format
        if image_name in imgNames:
            this_imgIdx = imgNames.index(image_name)
            this_imgConcepts = imgConcepts[this_imgIdx]
            outputformatList.append(image_name)

            # loop for the concepts for this image
            for concept_name in this_imgConcepts:
                score_for_concept = 0
                decision_for_concept = 0
                if concept_name in image_map_tags.keys():
                    score_for_concept = image_map_tags[concept_name]
                    decision_for_concept = 1

                # set the output format
                this_concept_str = ('%f %d' % (score_for_concept, decision_for_concept))
                outputformatList.append(this_concept_str)

            # now merge the outputformatList to get a final output string
            outputformatStr = ' '.join(outputformatList)

            # write it to file
            fid.write(outputformatStr + '\n')

    fid.close()



if __name__ == '__main__':
    # intial variables

    # read ImgEntry in overfeat_dev_results.txt file
    DevImgs = parse_overfeat_result(SRC_DATA_DIR + 'overfeat_dev_results.txt')

    Num_devImgs = len(DevImgs)
    print ' There are %d images from overfeat result. ' % Num_devImgs
    # read wordnet concetps from devel_dict_wn.txt file
    Imageclef_concepts = parse_imageclef_concepts_wn(SRC_DATA_DIR + 'devel_dict_wn.txt')

    # map the overfeat tags to imageclef tags
    count = 0
    mapping_type = [0,1,2,3,4,5]
    for eachImg in DevImgs:
        tag_overfeat = eachImg.imgtags

        for item in mapping_type:
            image_maptags = map_tag_overfeat2imageclef(tag_overfeat, Imageclef_concepts, item)
            print 'for image %s, using measure %s' % (eachImg.imgname, SIMILARITY_MEASURE[item])
            sorted_maptags = sort_dict(image_maptags)
            for eachitem in sorted_maptags:
                print str(eachitem),


        eachImg.imgmaptags.update(image_maptags)
        count += 1

        # if 0 == math.fmod(count, 100):
        print '...finished %d-th image, mapping tag from overfeat to imageclef ...' % count

    # read Image_conceptlists in devel_conceptlists.txt file
    Image_conceptlists = parse_imageclef_conceptlists(SRC_DATA_DIR + 'devel_conceptlists.txt')

    # now generate the final predict result
    generate_predict_results(DevImgs, Image_conceptlists, (DST_DATA_DIR + 'devel_predict_results.txt'))


    print 'finished predict tags for dev set -:)'