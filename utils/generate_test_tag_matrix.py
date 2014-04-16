__author__ = 'xuxing'

"""
    generate_test_tag_matrix.py is a script to produce the tag matrix file which can be used in matlab platform from given file.

    Especially, for imageclef2014 dataset, we transform original '[dev/test]_allconcepts.txt' file into 3 files.
    (1) '[test]_dict.txt' file, which includes all concepts with each in each row.
    (2) '[test]_imglist.txt', which includes all images with each in each row.
    (3) '[test]_tagmask.txt', which is a tag mask matrix for each image, generated from '[dev/test]_conceptlists.txt' file
"""


import numpy as np
import imageclef_settings as settings
import imageclef_fileparser as fileparser

# define a structure of each image entry
class img:
    def __init__(self):
        self.imgname = ''
        self.imgtags = []
        self.imgtagmasks = []


if __name__ == '__main__':

    """
    # this section use to generate test_imglist.txt (replicated) and test_tagmask.txt files


    test_conceptlistsfile = 'test_conceptlists.txt'
    test_dicfile = 'test_dict.txt'

    Imgs = []
    Dict = []

    # first read all unique tags from 'test_dict.txt' file
    fid = open(settings.SRC_DATA_DIR + test_dicfile)
    allinfo = fid.readlines()
    num_tag = len(allinfo)
    for line in allinfo:
        Dict.append(line.strip('\n'))

    print 'there all total %d tags in dev set' % num_tag
    fid.close()

    # loop to read each line in dev_conceptlistsfile to generate the tag_mask matrix
    fid2 = open(settings.SRC_DATA_DIR + test_conceptlistsfile)
    allinfo2 = fid2.readlines()


    num_img = len(allinfo2)
    print 'total image number for dev set is %d' % num_img
    for idx in range(num_img):
        # now process each line
        newImg = img()
        info2 = allinfo2[idx].strip('\n').split()

        newImg.imgname = info2[0]
        newImg.imgtagmasks = info2[1:]

        Imgs.append(newImg)

    fid2.close()

    # now save in dst files
    # here we save (2) tag matrix and (3) imglist and (4) tag mask matrix at same time
    # we loop for
    dev_imglistfile = 'test_imglist.txt'
    dev_tagmaskfile = 'test_tagmask.txt'

    fid_imglistfile = open(settings.DST_DATA_DIR + dev_imglistfile, 'w')
    fid_tagmask = open(settings.DST_DATA_DIR + dev_tagmaskfile, 'w')

    # new a tag and tag mask matrix with size num_img x num_tag
    tagmaskmatrix = np.zeros((num_img, num_tag))

    for image_index in range(len(Imgs)):
        # first write image name to imagelistfile
        image = Imgs[image_index]
        fid_imglistfile.write(image.imgname+'\n')

        # then find tag index for each tag in current image
        for tag in image.imgtags:
            tag_idx = Dict.index(tag)

        # then find vaid tag index for each masked tag in current image
            for masked_tag in image.imgtagmasks:
                tag_idx = Dict.index(masked_tag)
                tagmaskmatrix[image_index][tag_idx] = 1

    # now finished write imagelist file
    fid_imglistfile.close()
    print 'finished write imagelist file'

    # now finished write tagmask file and save tagmatrix file
    np.savetxt(fid_tagmask, tagmaskmatrix, fmt='%d')
    fid_tagmask.close()
    print 'finished write tagmask file'

    """


    """
    # now generate the unique test_imglist_unique.txt

    imglist_replicate = 'test_imglist.txt'
    imglist_unique = 'test_imglist_unique.txt'

    fileparser.generate_unique_imglist(settings.SRC_DATA_DIR + imglist_replicate, \
                            settings.SRC_DATA_DIR+imglist_unique)

    print 'finished generating unqiue test imagelist!'

    """

    # now only preserve the image ids that not occurs in the dev set, and generate the final unique test imglist
    dev_imglist_unique = 'devel_imglist_unique-jpg.txt'
    test_imglist_unique = 'test_imglist_unique-jpg.txt'

    fid_dev = open(settings.SRC_DATA_DIR + dev_imglist_unique, 'r')
    fid_test = open(settings.SRC_DATA_DIR + test_imglist_unique, 'r')

    list_dev_unique = []
    list_test_unique = []

    for line in fid_dev.readlines():
        list_dev_unique.append(line.strip('\n'))

    for line in fid_test.readlines():
        list_test_unique.append(line.strip('\n'))

    fid_dev.close()
    fid_test.close()
    # now loop to preserve
    for item in list_dev_unique:
        try:
            idx = list_test_unique.index(item)
            list_test_unique.pop(idx)
        except Exception, ex:
            print 'item %s in dev list not found in test list!' % item

    print 'finally we get %d unique samples in test set except dev set!' % len(list_test_unique)
    # now write to new file
    test_imglist_unique_final =  'test_imglist_unique_final-jpg.txt'

    fid_final = open(settings.DST_DATA_DIR+test_imglist_unique_final, 'w')

    for item in list_test_unique:
        fid_final.write(item + '\n')

    fid_final.close()

    test_imglist_unique_final =  'test_imglist_unique_final+jpg.txt'

    fid_final = open(settings.DST_DATA_DIR+test_imglist_unique_final, 'w')

    for item in list_test_unique:
        fid_final.write(item + '.jpg' + '\n')

    fid_final.close()

