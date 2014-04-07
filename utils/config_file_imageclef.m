%%% Global configuration file %%%%

%% Path for laptop
ROOT_DIR = 'C:\workspace\my tools\git code\imageclef-proj';
SRC_DATA_DIR = 'C:\workspace\my tools\git code\imageclef-proj\data';
UTILS_DIR = 'C:\workspace\my tools\git code\imageclef-proj\utils';

DST_FEA_DIR = 'C:\workspace\program\image-annotation\benchmark-dataset\Imageclef2014\imageclef2014data';
%% Path for desktop


%% visual feature files for Dev
FeatureFilesDev = {'webupv14_devel_visual_getlf';
    'webupv14_devel_visual_gist2';
    'webupv14_devel_visual_sift_1000';
    'webupv14_devel_visual_rgbsift_1000';
    'webupv14_devel_visual_opponentsift_1000';
    'webupv14_devel_visual_csift_1000';
    'webupv14_devel_visual_colorhist'
    };

%% tag files for Dev
DevFiles.tagmatrix = 'devel_tagmatrix.txt';
DevFiles.imglist = 'devel_imglist.txt';
DevFiles.dict = 'devel_dict.txt';
DevFiles.tagmask = 'devel_tagmask.txt';

%% visual feature files for Test
FeatureFilesTest = {'webupv14_test_visual_getlf';
    'webupv14_test_visual_gist2';
    'webupv14_test_visual_sift_1000';
    'webupv14_test_visual_rgbsift_1000';
    'webupv14_test_visual_opponentsift_1000';
    'webupv14_test_visual_csift_1000';
    'webupv14_test_visual_colorhist'
    };



%% settings for svm training
SVM.cList = [-2:1:5];
SVM.bCrossValSVM = true;
SVM.kernel = 'linear';