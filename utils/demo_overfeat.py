__author__ = 'xuxing'

"""
    demo_overfeat.py is a demo script which utilizes the output from overfeat, and mapped the results from overfeat to imageclef
        output.
"""


import imageclef_settings as settings
import imageclef_fileparser as fileparser
import math
import sys

if __name__ == '__main__':

    # read ImgEntry in overfeat_dev_results.txt file
    DevImgs = fileparser.parse_overfeat_result(settings.SRC_DATA_DIR + 'overfeat_dev_results.txt')

    Num_devImgs = len(DevImgs)
    print ' There are %d images from overfeat result. ' % Num_devImgs
    # read wordnet concetps from devel_dict_wn.txt file
    Imageclef_concepts = fileparser.parse_imageclef_concepts_wn(settings.SRC_DATA_DIR + 'devel_dict_wn.txt')

    # map the overfeat tags to imageclef tags
    count = 0
    mapping_type = [0,1,2,3,4,5]
    for eachImg in DevImgs:
        tag_overfeat = eachImg.imgtags

        for item in mapping_type:
            image_maptags = fileparser.map_tag_overfeat2imageclef(tag_overfeat, Imageclef_concepts, item)
            print 'for image %s, using measure %s' % (eachImg.imgname, settings.SIMILARITY_MEASURE[item])
            sorted_maptags = fileparser.sort_dict(image_maptags)
            for eachitem in sorted_maptags:
                print str(eachitem),


        eachImg.imgmaptags.update(image_maptags)
        count += 1

        # if 0 == math.fmod(count, 100):
        print '...finished %d-th image, mapping tag from overfeat to imageclef ...' % count

    # read Image_conceptlists in devel_conceptlists.txt file
    Image_conceptlists = fileparser.parse_imageclef_conceptlists(settings.SRC_DATA_DIR + 'devel_conceptlists.txt')

    # now generate the final predict result
    fileparser.generate_predict_results(DevImgs, Image_conceptlists, (settings.DST_DATA_DIR + 'devel_predict_results.txt'))


    print 'finished predict tags for dev set -:)'