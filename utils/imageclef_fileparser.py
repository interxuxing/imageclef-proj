__author__ = 'xuxing'

"""
    wordnet_word_sim.py is a simple script to calculate the similarity between different words
"""


from nltk.corpus import wordnet as wn
import numpy as np
import re

import imageclef_settings as settings
import copy as cp

# first give some initial configuration about path, etc
# give some initial configuration
# ENV = 1 # 1:laptop  2:desktop
#
# if ENV == 1:
#     SRC_DATA_DIR = 'C:\\workspace\\my tools\\git code\\imageclef-proj\\data\\'
#     DST_DATA_DIR = SRC_DATA_DIR
#     WORDNET_IC_DIR = 'C:\\Users\\xuxing\\AppData\\Roaming\\nltk_data\\corpora\\wordnet_ic\\'
# else:
#     SRC_DATA_DIR = 'D:\\workspace-limu\\image-annotation\\datasets\\imageclef2014\\imageclef-proj\\data\\'
#     DST_DATA_DIR = 'D:\\workspace-limu\\cloud disk\\Dropbox\\limu\\submission\\ImageCLEF2014\\'
#     WORDNET_IC_DIR = 'C:\\Users\\LIMU\\AppData\\Roaming\\nltk_data\\corpora\\wordnet_ic\\'

from nltk.corpus import wordnet_ic
ic = wordnet_ic.ic(settings.WORDNET_IC_DIR+'ic-brown.dat')

# define a structure of each image entry
class ImgEntry:
    def __init__(self):
        self.imgname = ''
        self.imgtags = {} # dict, predict tag with score, tags in overfeat
        self.imgmaptags = {} # dict, mapped tags with score, tags in imageclef

from operator import itemgetter
def sort_dict(d, reverse=False):
    # sort the dict based on values, for descending order, return a list with item [(key, value), ..., (key, value)]
    return sorted(d.iteritems(), key=itemgetter(1), reverse=True)


def select_topK_dict(in_dict, K):
    """
        function select_topK_dict is to select the top K entries (with values) in in_dict

        Input:
            in_dict: a dict
            K: an int number < 10

        Return:
            out_dict: a dict with topK entries in in_dict
    """

    sorted_list = sort_dict(in_dict, reverse=True) # descending order
    num1 = len(sorted_list)

    if num1 < K:
        print 'number of entries in in_dict should be larger than %d, but it is %d' % (K, num1)
        return None

    out_dict = {}
    # now fill the topK entries with values to out_dict
    for idx in range(num1):
        if idx <= K:
            item = sorted_list[idx]
            key = item[0]
            value = item[1]
            out_dict[key] = value
        else:
            break

    return out_dict

def select_dominant_topK_dict(in_dict, sigma=0.9):
    """
        function select_dominant_topK can be called after function select_topK_dict
            since we first select topK from 10 tags predicted by Clarifai,
                we then further select dominant tags from the top-K tags based on the threshold value sigma (default 0.9)

        Input:
            in_dict, a non-order dict structure of K (key, value) pairs
            sigma, a threshold value, default 0.9

        Return:
            out_dict: a dict with dominant entries in in_dict, number of items should be no larger than K
    """
    sorted_list = sort_dict(in_dict, reverse=True) # descending order
    out_dict = {}

    # get only the scores
    scores = []
    for item1, item2 in sorted_list:
        scores.append(item2)

    # get dominant indice where cumsum greater than sigma
    array_scores = np.array(scores)
    cum = np.cumsum(array_scores)
    cum_norm = cum / cum[-1]
    flag = cum_norm <= sigma
    indice = np.sum(flag)
    if indice == 0: # when 1st value is large enough, flag are all false, we need to preserve the 1st one
        indice = 1
    # then copy the 0~indices from in_dict to out_dict
    for idx in range(indice):
        item = sorted_list[idx]
        key = item[0]
        value = item[1]
        out_dict[key] = value

    return out_dict

def parse_overfeat_result(res_file, step=10):
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
    STEP = step # each image 6 level tags
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
            d = split_tags_overfeat(tags)
            newImg.imgtags.update(d)

        # if get end line (6-th line) for each image
        # reset the flags
        if count == STEP:
            isNewImage = True
            count = 0
            DevImgs.append(newImg)

    fid.close()
    return DevImgs

def split_tags_overfeat(old_tags):
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


def parse_clarifai_result(res_file, step=10):
    """
        parse_clarifai_result(res_file) is a function to parse the output tag results from clarifai

        in the res_file, for each image, it is formatted as:
        line1: imagename
        line2: tag(score1%)
        line3: tag(score2%)
        line4: tag(score3%)
        line5: tag(score4%)
        line6: tag(score5%)
        line7: tag(score6%)
        line8: tag(score7%)
        line9: tag(score8%)
        line10: tag(score9%)
        line11: tag(score10%)
        Return:
            A list contains entries, each entry is a ImgEntry object
    """

    DevImgs = []
    fid = open(res_file, 'r')
    STEP = 10 # each image 6 level tags
    count = 0 # count the level of each image
    line_count = 0
    isNewImage = True
    for line in fid.readlines():
        # the first 2 bytes in 1st line of 'clarifai_predict_results.txt' need to be removed!
        line_count += 1
        # if line_count == 1:   # this is for utf-8 coding file, if ascii coding, no need!
        #     line = line[3:]

        if isNewImage:
            # create a new image instance
            newImg = ImgEntry()
            # read 1st line image name
            newImg.imgname = line.strip('\n')

            isNewImage = False
        else:
            count += 1
            tags = line.strip('\n')
            d = split_tags_clarifai(tags)
            newImg.imgtags.update(d)

        # if get end line (6-th line) for each image
        # reset the flags
        if count == STEP:
            isNewImage = True
            count = 0
            DevImgs.append(newImg)

    fid.close()
    return DevImgs

def split_tags_clarifai(old_tags):
    """
        function split_tags is to split the tag format in overfeat outputfile
            to get (tag, socre) format

        input old_tags is a string
        return a dict contains {tag:score}, only one instance
    """
    pattern = re.compile(r'(\w+)\((\d+.\d+)%\)')
    p = pattern.findall(old_tags)

    if len(p) != 1:
        print 'no tag and score found in input %s, check the pattern again!' % old_tags
        return -1

    tag = p[0][0]
    score = float(p[0][1]) / 100

    d = {tag:score}
    return d


def generate_replicate_clarifai_ImgEntries(in_ImgEntries, in_Imglistfile):
    """
        function generate_replicate_clarifai_ImgEntries is to produce the replicated ImgEntries data as listed in dev_imglist.txt
            file.
        Since function parse_clarifai_result only produces unique ImgEntries, but we need replicated ones

        Input:
            in_ImgEntries is the unique ImgEntries
            in_Imglistfile is the dev_imglist.txt file

        Return:
            replicated_ImgEntries, a list of replicated ImgEntries
    """

    unique_Imglist = []
    replicate_Imglist = []
    replicate_ImgEntries = []

    fid_Imglist = open(in_Imglistfile, 'r')
    for line in fid_Imglist.readlines():
        replicate_Imglist.append(line.strip('\n'))

    for entry in in_ImgEntries:
        unique_Imglist.append(entry.imgname)

    # now copy the unique ones to the relpicated oupputlist
    for item in replicate_Imglist:
        unique_idx = unique_Imglist.index(item)
        replicate_ImgEntries.append(in_ImgEntries[unique_idx])

    fid_Imglist.close()
    return replicate_ImgEntries

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
            print ' no synsets retireved for Clarifai tag: ' + old_tag
            continue

        syn_old_tag = synsets_old_tag[0]

        # now calculate similarity score with concepts in Imageclef
        for idx_new_tag in range(len(concept_tag)):
            new_tag = concept_tag[idx_new_tag]

            if new_tag == old_tag: # if tag from clarifai is in Clef tag sets, set path_sim = 1
                path_sim = 1
                sim_score[idx_old_tag][idx_new_tag] = float(old_tag_score) * path_sim
            else:
                new_tag_sense = concept_sense[idx_new_tag] - 1 # keep index with list order

                synsets_new_tag = wn.synsets(new_tag)
                syn_new_tag = synsets_new_tag[new_tag_sense]
                # calculate path similarity
                path_sim = synsets_similarity(syn_old_tag, syn_new_tag, mapping_type)
                if path_sim is None:
                    path_sim = 0
                sim_score[idx_old_tag][idx_new_tag] = float(old_tag_score) * path_sim
                # sim_score[idx_old_tag][idx_new_tag] = path_sim
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
            # map_dict[tag_imageclef] += tag_overfeat.values()[i]
        else:
            map_dict[tag_imageclef] = pred_sim_score[i]
            # map_dict[tag_imageclef] = tag_overfeat.values()[i]

    # process for sunrise and sunset tags, merge it in map_dict
    map_dict['sunrise/sunset'] = 0
    if 'sunrise' in map_dict.keys():
        map_dict['sunrise/sunset'] += map_dict['sunrise']
        del map_dict['sunrise']
    if 'sunset' in map_dict.keys():
        map_dict['sunrise/sunset'] += map_dict['sunset']
        del map_dict['sunset']

    if 0 == map_dict['sunrise/sunset']:
        del map_dict['sunrise/sunset']

    if len(map_dict) == 0:
        print '... ... no map_dict obtained for current image!'
        return -1
    else:
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
    #   here we need to ensure that entry in res_ImgEntries and imgNames has the same order
    # for newEntry in res_ImgEntries:
    for entryIdx in range(len(res_ImgEntries)):
        newEntry = res_ImgEntries[entryIdx]
        # each item is a dictionary type
        image_name = newEntry.imgname # a str
        image_map_tags = newEntry.imgmaptags # a dict

        if image_name != imgNames[entryIdx]:
            print 'for entry %s in res_ImgEntries is not matched with %s in res_clef_conceptlists! ' % (image_name, imgNames[entryIdx])
            raise IOError, 'error with name matching'

        outputformatList = []
        # if this image exists, then output it using standard format
        this_imgConcepts = imgConcepts[entryIdx]
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

        """
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
        """
    fid.close()


def generate_unique_imglist(in_listfile, out_listfile):
    """
        function generate_unique_imglist generates the unique image ids to a file

        Input:
            in_listfile,  a txt file contains the replicate image ids
            out_listfile, a txt file contains only unique image ids
    """

    fid_in = open(in_listfile, 'r')
    fid_out = open(out_listfile, 'w')

    # construct the replicate image list
    list_img_replicate = []

    for line in fid_in.readlines():
        list_img_replicate.append(line.strip('\n'))

    print 'there are %d instances in relicate image list %s' % (len(list_img_replicate), in_listfile)

    list_img_unique = list(set(list_img_replicate))
    for line in list_img_unique:
        fid_out.write(line + '.jpg' + '\n') # add .jpg or not    fid_out.write(line + '.jpg' + '\n')

    print 'there are %d instances in unique image list %s' % (len(list_img_unique), out_listfile)


    fid_in.close()
    fid_out.close()




class ClarifaiTagFilter(object):
    """
        class TagFilter is a class to map the original tags predicted by Clarifai to the tags used in CLEF.
            There are mainly two parts of filtering process: (1) transform the tags predicted by Clarifai, which can not be
                parsed in wordnet, to the tags in CLEF. (2) add some CLEF tags (which are hardly recalled) based on the
                co-occurrence.
    """
    mapping_tag_pairs = {}
    def __init__(self, in_mapping_file):
        """
            when initial a ClarifaiTagFilter object, parse the mapping file, get mapping tag pairs (a dict)
        """
        self.mapping_tag_pairs = self.parse_mapping_file(in_mapping_file)

    def parse_mapping_file(self, in_mapping_file):
        """
            parse the mapping file

            Input:
                in_mapping_file
            Output:
                a dict structure contains the {'clarifai_tag':'clef_tag', ...} pairs
        """
        fid = open(in_mapping_file, 'r')
        dict_tag_pairs = {}
        for line in fid.readlines():
            content = line.strip('\n').split('\t')
            # put the content[0] (clarifai_tag) and content[1] (clef_tag) to dict
            try:
                clarifai_tag = content[0]
                clef_tag = content[1]
                dict_tag_pairs[clarifai_tag] = clef_tag
            except IndexError, err:
                print 'Index Error'

        fid.close()
        return dict_tag_pairs

    def filtering_tag(self, ori_tag_dict):
        """
            function filtering_tag is to mapping the tags in in_orig_tag_dict based on mapping_tag_pairs,
                returns a new dict whose keys are in CLEF set
        """
        dst_tag_dict = {}

        # first process the condition for tricycle
        list_keys = ori_tag_dict.keys()
        if 'kid' in  list_keys and 'bike' in list_keys:
            dst_value = max(ori_tag_dict['kid'], ori_tag_dict['bike'])
            dst_tag_dict['tricycle'] = dst_value
            # delete the item bike
            del ori_tag_dict['bike']

        # for mapping tag pairs
        for key in ori_tag_dict:
            ori_value = ori_tag_dict[key]
            # whether this key is in mapping_tag_pairs
            try:
                new_value = self.mapping_tag_pairs[key]
                # now delete the ori_key and assign new key
                dst_tag_dict[new_value] = ori_value
            except KeyError, args:
                # if this key is not in mapping_tag_pairs, preserve it
                dst_tag_dict[key] = ori_value

        return dst_tag_dict

    def add_cooccur_tags(self, ori_tag_dict):
        """
            add co-occurred tags to the ori_tag_dict, e.g. if ori_tag_dict contains cloud, add 'overcast' with some confidence socre

                for devel set, we consider word pairs (overcast, cloud), (cloudless, sky), (unpaved, road), (underwater, water)
        """
        dst_tag_dict =  cp.deepcopy(ori_tag_dict)
        for key in ori_tag_dict:
            if key == 'cloud':
                ori_value = ori_tag_dict[key]
                dst_value = ori_value * (128.0 / 478.0)
                # add overcast
                dst_tag_dict['overcast'] = dst_value

            if key == 'sky':
                ori_value = ori_tag_dict[key]
                dst_value = ori_value * (79.0 / 194.0)
                # add cloudless
                dst_tag_dict['cloudless'] = dst_value

            if key == 'road':
                ori_value = ori_tag_dict[key]
                dst_value = ori_value * (26.0 / 244.0)
                # add unpaved
                dst_tag_dict['unpaved'] = dst_value

            if key == 'water':
                ori_value = ori_tag_dict[key]
                dst_value = ori_value * (24.0 / 288.0)
                # add underwater
                dst_tag_dict['underwater'] = dst_value

            if key == 'train':
                ori_value = ori_tag_dict[key]
                dst_value = ori_value / 2.0
                # add vehicle
                dst_tag_dict['vehicle'] = dst_value

            if key == 'boat':
                ori_value = ori_tag_dict[key]
                dst_value = ori_value * (118.0 / 288.0)
                # add water
                dst_tag_dict['water'] = dst_value

            # for canidae
            if key in ['wolf', 'fox']:
                ori_value = ori_tag_dict[key]
                dst_value = ori_value * (1.0 / 9.0)
                # add canidae
                dst_tag_dict['canidae'] = dst_value

            # for tubers
            if key == 'yam':
                ori_value = ori_tag_dict[key]
                dst_value = ori_value * (1.0 / 5.0)
                # add tubers
                dst_tag_dict['tubers'] = dst_value

            # for equidae
            if key in ['horse', 'donkey', 'zebra']:
                ori_value = ori_tag_dict[key]
                dst_value = ori_value * (1.0 / 9.0)
                # add equidae
                dst_tag_dict['equidae'] = dst_value

            if key == 'asparagus':
                ori_value = ori_tag_dict[key]
                dst_value = ori_value  * (1.0 / 9.0)
                # add lettuce
                dst_tag_dict['lettuce'] = dst_value

        # for pair-wise tags condition, if 2 tags occurs, add the 3rd tag
        list_keys = ori_tag_dict.keys()
        # if fruit and red co-occur, add apple
        if 'fruit' in list_keys and 'red' in list_keys:
            dst_value = max(ori_tag_dict['fruit'], ori_tag_dict['red'])
            dst_tag_dict['apple'] = dst_value
        # for bottle condition
        if ('drink' in list_keys and 'glass' in list_keys) or \
                ('drink' in list_keys and 'water' in list_keys):
            dst_value = ori_tag_dict['drink'] * (1.0 / 2.0)
            dst_tag_dict['bottle'] = dst_value

        return dst_tag_dict





if __name__ == '__main__':
    # intial variables
    imglist_replicate = 'devel_imglist.txt'
    imglist_unique = 'devel_imglist_unique.txt'

    generate_unique_imglist(settings.SRC_DATA_DIR+imglist_replicate, settings.SRC_DATA_DIR+imglist_unique)



