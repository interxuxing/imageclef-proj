function imageclef_merge_images()
%% function imageclef_merge_images() is a script to merge the images in subdir into one
% single directory


src_dir = 'D:\workspace-limu\image-annotation\datasets\imageclef2014\imageclef2014data\dev\devimages';
merge_dirname = 'devall';

if ~exist(fullfile(src_dir, merge_dirname), 'dir')
    mkdir(fullfile(src_dir, merge_dirname));
end
    
imgNum = 0;
dirInfor = dir(src_dir);

for d = 3 : length(dirInfor)
    if ~dirInfor(d).isdir
        continue;
    else
        if strcmp('.', dirInfor(d).name) || strcmp('..', dirInfor(d).name) || strcmp('devall', dirInfor(d).name)
            continue;
        end
        % is sub directory, go to this directory
        subdir = dirInfor(d).name;
        fileInfor = dir(fullfile(src_dir, subdir));
        
        for f = 1 : length(fileInfor)
            if ~fileInfor(f).isdir
                % is a jpg file
                jpgfilename = fileInfor(f).name;
                % move jpg file to merge dir
                try
                    movefile(fullfile(src_dir, subdir, jpgfilename), fullfile(src_dir, merge_dirname));
                catch
                    error('meet error');
                end
                imgNum = imgNum + 1;
            else
                continue;
            end
        end
        
        % remove the current sub dir
        rmdir(fullfile(src_dir, subdir));
    end
end

fprintf('finished merge dev set, total images %d \n', imgNum);