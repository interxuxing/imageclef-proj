__author__ = 'LIMU'

"""
    generate_tag_matrix.py is a script to produce the tag matrix file which can be used in matlab platform from given file.

    Especially, for imageclef2014 dataset, we transform original '[dev/test]_allconcepts.txt' file into 3 files.
    (1) '[dev/test]_dict.txt' file, which includes all concepts with each in each row.
    (2) '[dev/test]_tagmatrix.txt', which is a tag matrix file with all tags' presence/absence (1/0) in each row.
    (3) '[dev/test]_imglist.txt', which includes all images with each in each row.
    (4) '[dev/test]_tagmask.txt', which is a tag mask matrix for each image, generated from '[dev/test]_conceptlists.txt' file
"""


import numpy as np


# first give some initial configuration about path, etc
# give some initial configuration
ENV = 1 # 1:laptop  2:desktop

if ENV == 1:
    SRC_DATA_DIR = 'C:\\workspace\\my tools\\git code\\imageclef-proj\\data\\'
    DST_DATA_DIR = SRC_DATA_DIR
else:
    SRC_DATA_DIR = 'C:\\workspace\\my tools\\git code\\imageclef-proj\\data\\'
    DST_DATA_DIR = SRC_DATA_DIR



# define a structure of each image entry
class img:
    def __init__(self):
        self.imgname = ''
        self.imgtags = []
        self.imgtagmasks = []


if __name__ == '__main__':


    dev_gtfile = 'devel_groundtruth.txt'
    dev_conceptlistsfile = 'devel_conceptlists.txt'
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

    # loop to read each line in dev_gtfile and dev_conceptlistsfile
    fid = open(SRC_DATA_DIR + dev_gtfile)
    fid2 = open(SRC_DATA_DIR + dev_conceptlistsfile)
    allinfo = fid.readlines()
    allinfo2 = fid2.readlines()

    if len(allinfo) != len(allinfo2):
        print 'erro with image number in %s and %s files!' % (dev_gtfile, dev_conceptlistsfile)


    num_img = len(allinfo)
    print 'total image number for dev set is %d' % num_img
    for idx in range(num_img):
        # now process each line
        newImg = img()
        info1 = allinfo[idx].strip('\n').split()
        info2 = allinfo2[idx].strip('\n').split()

        newImg.imgname = info1[0]
        newImg.imgtags = info1[1:]
        newImg.imgtagmasks = info2[1:]

        Imgs.append(newImg)

    fid.close()
    fid2.close()

    # now save in dst files
    # here we save (2) tag matrix and (3) imglist and (4) tag mask matrix at same time
    # we loop for
    dev_tagmatrixfile = 'devel_tagmatrix.txt'
    dev_imglistfile = 'devel_imglist.txt'
    dev_tagmaskfile = 'devel_tagmask.txt'

    fid_tagmatrix = open(DST_DATA_DIR+dev_tagmatrixfile, 'w')
    fid_imglistfile = open(DST_DATA_DIR+dev_imglistfile, 'w')
    fid_tagmask = open(DST_DATA_DIR+dev_tagmaskfile, 'w')

    # new a tag and tag mask matrix with size num_img x num_tag
    tagmatrix = np.zeros((num_img, num_tag))
    tagmaskmatrix = np.zeros((num_img, num_tag))

    for image_index in range(len(Imgs)):
        # first write image name to imagelistfile
        image = Imgs[image_index]
        fid_imglistfile.write(image.imgname+'\n')

        # then find tag index for each tag in current image
        for tag in image.imgtags:
            tag_idx = Dict.index(tag)
            tagmatrix[image_index][tag_idx] = 1

        # then find vaid tag index for each masked tag in current image
            for masked_tag in image.imgtagmasks:
                tag_idx = Dict.index(masked_tag)
                tagmaskmatrix[image_index][tag_idx] = 1

    # now finished write imagelist file
    fid_imglistfile.close()
    print 'finished write imagelist file'

    # now now finished wirte tagmatrix file and save tagmatrix file
    np.savetxt(fid_tagmatrix, tagmatrix, fmt='%d')
    fid_tagmatrix.close()
    print 'finished write tagmatrix file'

    # now finished write tagmask file and save tagmatrix file
    np.savetxt(fid_tagmask, tagmaskmatrix, fmt='%d')
    fid_tagmask.close()
    print 'finished write tagmask file'



