__author__ = 'xuxing'

"""
    demo_overfeat.py is a demo script which utilizes the output from overfeat, and mapped the results from overfeat to imageclef
        output.
"""


import imageclef_settings as settings
import imageclef_fileparser as fileparser
import math
import sys
import imageclef_evaluation as evaluation


if __name__ == '__main__':

    # read ImgEntry in overfeat_dev_results.txt file
    DevImgs = fileparser.parse_clarifai_result(settings.SRC_DATA_DIR + 'clarifai_predict_results.txt')

    newDevImgs = fileparser.generate_replicate_clarifai_ImgEntries(DevImgs, settings.SRC_DATA_DIR + 'devel_imglist.txt')

    Num_devImgs = len(newDevImgs)
    print ' There are %d images from overfeat result. ' % Num_devImgs
    # read wordnet concetps from devel_dict_wn.txt file
    Imageclef_concepts = fileparser.parse_imageclef_concepts_wn(settings.SRC_DATA_DIR + 'devel_dict_wn.txt')

    # map the overfeat tags to imageclef tags
    count = 0
    mapping_type = [0]
    for eachImg in newDevImgs:
        tag_clarifai = eachImg.imgtags
        # now only select the top K values in tag_clarifai
        tag_clarifai_K = fileparser.select_topK_dict(tag_clarifai, 5)
        for item in mapping_type:
            image_maptags = fileparser.map_tag_overfeat2imageclef(tag_clarifai_K, Imageclef_concepts, item)
            print 'for image %s, using measure %s' % (eachImg.imgname, settings.SIMILARITY_MEASURE[item])
            try:
                sorted_maptags = fileparser.sort_dict(image_maptags)
            except Exception, er:
                print 'meet error!'
            for eachitem in sorted_maptags:
                print str(eachitem),
        print ''

        eachImg.imgmaptags.update(image_maptags)
        count += 1

        # if 0 == math.fmod(count, 100):
        # print '...finished %d-th image, mapping tag from overfeat to imageclef ...' % count

    # read Image_conceptlists in devel_conceptlists.txt file
    Image_conceptlists = fileparser.parse_imageclef_conceptlists(settings.SRC_DATA_DIR + 'devel_conceptlists.txt')

    # now generate the final predict result
    fileparser.generate_predict_results(newDevImgs, Image_conceptlists, \
                                        (settings.DST_DATA_DIR + 'clarifai_devel_predict_results.txt'))


    # generate the adaptive files for evaluation used
    dec_file = 'clarifai_devel_predict_decision.txt'
    score_file = 'clarifai_devel_predict_scores.txt'

    evaluation.generate_imageclef_evalfiles((settings.SRC_DATA_DIR+'devel_dict.txt'), newDevImgs, \
        (settings.SRC_DATA_DIR+dec_file), (settings.SRC_DATA_DIR+score_file))



    print 'finished predict tags for dev set -:)'