__author__ = 'xuxing'

"""
    demo_clarifai.py is a demo script which utilizes the output from clarifai, and mapped the results from clarifai to imageclef
        output.
"""


import imageclef_settings as settings
import imageclef_fileparser as fileparser
import math
import sys
import imageclef_evaluation as evaluation
import cPickle

if __name__ == '__main__':

    """
    # generate baseline results for 'baseline_predict_decision.txt' and 'baseline_predict_scores.txt'
    # read Image_conceptlists in devel_conceptlists.txt file
    Image_conceptlists = fileparser.parse_imageclef_conceptlists(settings.SRC_DATA_DIR + 'devel_conceptlists.txt')

    dec_file = 'baseline_random_predict_decision.txt'
    score_file = 'baseline_random_predict_scores.txt'
    dict_file = 'devel_dict.txt'
    res_file = 'baseline_occurrence_devel_sift.res'
    evaluation.generate_imageclef_baselines(settings.SRC_DATA_DIR+dict_file, settings.SRC_DATA_DIR+res_file, \
                                            Image_conceptlists, settings.DST_DATA_DIR+dec_file, settings.DST_DATA_DIR+score_file)

    """

    # read ImgEntry in overfeat_dev_results.txt file
    DevImgs = fileparser.parse_clarifai_result(settings.SRC_DATA_DIR + 'clarifai_predict_results.txt')

    newDevImgs = fileparser.generate_replicate_clarifai_ImgEntries(DevImgs, settings.SRC_DATA_DIR + 'devel_imglist.txt')

    Num_devImgs = len(newDevImgs)
    print ' There are %d images from clarifai result. ' % Num_devImgs
    # read wordnet concetps from devel_dict_wn.txt file
    Imageclef_concepts = fileparser.parse_imageclef_concepts_wn(settings.SRC_DATA_DIR + 'devel_dict_wn.txt')

    # read Image_conceptlists in devel_conceptlists.txt file
    Image_conceptlists = fileparser.parse_imageclef_conceptlists(settings.SRC_DATA_DIR + 'devel_conceptlists.txt')

    # new a filter object
    tagFilter = fileparser.ClarifaiTagFilter(settings.SRC_DATA_DIR + 'mapping_tag_pairs_test.txt')

    # map the overfeat tags to imageclef tags

    mapping_type = [0]
    K = [2,3,4,6,7,8,9]
    # K = [6]
    for eachK in K:
        print 'predict with K %d' % eachK
        count = 0
        for eachImg in newDevImgs:
            count += 1
            tag_clarifai = eachImg.imgtags
            # now only select the top K values in tag_clarifai
            tag_clarifai_K = fileparser.select_topK_dict(tag_clarifai, eachK)
            # filter tag_clarifai_K
            tag_clarifai_K1 = tagFilter.filtering_tag(tag_clarifai_K)
            tag_clarifai_K2 = tagFilter.add_cooccur_tags(tag_clarifai_K1)
            for item in mapping_type:
                image_maptags = fileparser.map_tag_overfeat2imageclef(tag_clarifai_K2, Imageclef_concepts, item)
                image_maptags_K0 = fileparser.select_dominant_topK_dict(image_maptags, 0.95)
                print '... for %d-th image %s, using measure %s' % (count, eachImg.imgname, settings.SIMILARITY_MEASURE[item])
                try:
                    sorted_maptags = fileparser.sort_dict(image_maptags_K0)

                except Exception, er:
                    print 'meet error!'
                for eachitem in sorted_maptags:
                    print str(eachitem),
            print ''

            eachImg.imgmaptags.update(image_maptags_K0)


            # if 0 == math.fmod(count, 100):
            # print '...finished %d-th image, mapping tag from overfeat to imageclef ...' % count


        # f = open('test1.data', 'r')
        # newDevImgs = cPickle.load(f)
        # f.close()

        # now generate the final predict result
        pred_file = ('clef_devel_predict_results_K%d.txt' % eachK)
        fileparser.generate_predict_results(newDevImgs, Image_conceptlists, \
                                            (settings.DST_DATA_DIR + pred_file))

        # generate the adaptive files for evaluation used
        dec_file = ('clef_devel_predict_decision_K%d.txt' % eachK )
        score_file = ('clef_devel_predict_scores_K%d.txt' % eachK )

        evaluation.generate_imageclef_evalfiles((settings.SRC_DATA_DIR+'devel_dict.txt'), newDevImgs, \
            (settings.SRC_DATA_DIR+dec_file), (settings.SRC_DATA_DIR+score_file))

        print 'finished predict tags for dev set -:) with K %d' % eachK

