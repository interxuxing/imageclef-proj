__author__ = 'LIMU'

"""
    generate_tag_matrix.py is a script to produce the tag matrix file which can be used in matlab platform from given file.

    Especially, for imageclef2014 dataset, we transform original '[dev/test]_allconcepts.txt' file into 3 files.
    (1) '[dev/test]_dict.txt' file, which includes all concepts with each in each row.
    (2) '[dev/test]_tagmatrix.txt', which is a tag matrix file with all tags' presence/absence (1/0) in each row.
    (3) '[dev/test]_imglist.txt', which includes all images with each in each row.
"""


import numpy as np

# define a structure of each image entry
class img:
    def __init__(self):
        self.imgname = ''
        self.imgtags = []


if __name__ == '__main__':
    # give some initial configuration
    SRC_DATA_DIR = 'D:\\workspace-limu\\image-annotation\\datasets\\imageclef2014\\imageclef-proj\\data\\'
    DST_DATA_DIR = SRC_DATA_DIR

    dev_gtfile = 'devel_groundtruth.txt'
    dev_dicfile = 'devel_dict.txt'



    Imgs = []
    Dict = []

    # first read all unique tags from 'dev_dict.txt' file
    fid = open(SRC_DATA_DIR + dev_dicfile)
    allinfo = fid.readlines()
    num_tag = len(allinfo)
    for line in allinfo:
        Dict.append(line.strip('\n'))

    print 'there all total %d tags in dev set' % num_tag
    fid.close()

    # loop to read each line in dev_gtfile
    fid = open(SRC_DATA_DIR + dev_gtfile)
    allinfo = fid.readlines()
    num_img = len(allinfo)
    print 'total image number for dev set is %d' % num_img
    for line in allinfo:
        # now process each line
        newImg = img()
        info = line.strip('\n').split()

        newImg.imgname = info[0]
        newImg.imgtags = info[1:]

        Imgs.append(newImg)

    fid.close()

    # now save in dst files
    # here we save (2) tag matrix and (3) imglist at same time
    # we loop for
    dev_tagmatrixfile = 'devl_tagmatrix.txt'
    dev_imglistfile = 'devl_imglist.txt'
    fid_tagmatrix = open(DST_DATA_DIR+dev_tagmatrixfile, 'w')
    fid_imglistfile = open(DST_DATA_DIR+dev_imglistfile, 'w')

    # new a tag matrix with size num_img x num_tag
    tagmatrix = np.zeros((num_img, num_tag))

    for image_index in range(len(Imgs)):
        # first write image name to imagelistfile
        image = Imgs[image_index]
        fid_imglistfile.write(image.imgname+'\n')

        # then find tag index for each tag in current image
        for tag in image.imgtags:
            tag_idx = Dict.index(tag)
            tagmatrix[image_index][tag_idx] = 1

    # now finished write imagelist file
    fid_imglistfile.close()
    print 'finished write imagelist file'

    # now loop again to save tagmatrix file
    for data_slice in tagmatrix:
        np.savetxt(fid_tagmatrix, data_slice, fmt='%d')

    # now finished wirte tagmatrix file
    fid_tagmatrix.close()
    print 'finished write tagmatrix file'



