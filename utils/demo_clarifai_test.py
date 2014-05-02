__author__ = 'xuxing'

"""
    demo_clarifai_test.py is a demo script to run clarifai prediction result on ImageCLEF2014 test data.
        This script show full steps of utilizing the output from clarifai, and mapped the results from overfeat to imageclef
        output.
"""


import imageclef_settings as settings
import imageclef_fileparser as fileparser
import math
import imageclef_evaluation as evaluation

if __name__ == '__main__':

    # read Image_conceptlists in test_conceptlists.txt file
    Image_conceptlists = fileparser.parse_imageclef_conceptlists(settings.SRC_DATA_DIR + 'test_conceptlists.txt')
    print ('There are total %d samples (including replicates) in ImageCLEF2014 test set!' % len(Image_conceptlists[0]))

    # read ImgEntry in overfeat_test_results.txt file
    DevImgs = fileparser.parse_clarifai_result(settings.SRC_DATA_DIR + 'clarifai_test_predict_results.txt')
    print ('There are total %d unique samples in ImageCLEF2014 test set!' % len(DevImgs))

    # map the unique samples to replicate samples
    newDevImgs = fileparser.generate_replicate_clarifai_ImgEntries(DevImgs, settings.SRC_DATA_DIR + 'test_imglist.txt')

    Num_devImgs = len(newDevImgs)
    if Num_devImgs != len(Image_conceptlists[0]):
        print 'Number of samples not match !'

    # read wordnet concetps from devel_dict_wn.txt file
    Imageclef_concepts = fileparser.parse_imageclef_concepts_wn(settings.SRC_DATA_DIR + 'test_dict_wn.txt')

    # # read Image_conceptlists in devel_conceptlists.txt file
    # Image_conceptlists = fileparser.parse_imageclef_conceptlists(settings.SRC_DATA_DIR + 'devel_conceptlists.txt')

    # new a filter object
    tagFilter = fileparser.ClarifaiTagFilter(settings.SRC_DATA_DIR + 'mapping_tag_pairs_devel.txt')

    # map the overfeat tags to imageclef tags

    mapping_type = [0]
    # K = [4,6,7,8,9]
    K = [6]
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

        # now generate the final predict result
        pred_file = ('clef_test_predict_results_K%d.txt' % eachK)
        fileparser.generate_predict_results(newDevImgs, Image_conceptlists, \
                                            (settings.DST_DATA_DIR + pred_file))

        # generate the adaptive files for evaluation used
        dec_file = ('clef_test_predict_decision_K%d.txt' % eachK )
        score_file = ('clef_test_predict_scores_K%d.txt' % eachK )

        evaluation.generate_imageclef_evalfiles((settings.SRC_DATA_DIR+'test_dict.txt'), newDevImgs, \
            (settings.SRC_DATA_DIR+dec_file), (settings.SRC_DATA_DIR+score_file))

        print 'finished predict tags for dev set -:) with K %d' % eachK

