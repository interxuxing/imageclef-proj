function featMat = imageclef_parse_featfile(vfilename)
%% function imageclef_read_visual_feature(vfilename)
%   is a basic function to read original visual feature file into matlab
%   data format


%% start
%vfilename = 'webupv14_test_visual_colorhist.feat';

fid = fopen(vfilename);

% first read 'totalnumber' and 'vdim'
a = fscanf(fid, '%d %d', 2);

imgNum = a(1);
feaDim = a(2);

fprintf('Feature file: %s, Num of images: %d, Dim of feature: %d \n', ...
    vfilename, imgNum, feaDim);

featMat = zeros(imgNum, feaDim);
% then read each image
for i = 1 : imgNum
    % first total descriptors in one image
    desnum = fscanf(fid, '%d', 1);
    b = fscanf(fid, '%d %f', [2,desnum]);
    
    % copy to featMat, b(1)+1 use index starts from 1, not 0
    featMat(i, b(1,:)+1) = b(2,:);
%     if mod(i, 300) == 0
%         fprintf('%d imgs finished! \n', i);
%     end
end

featMat = sparse(featMat);
fclose(fid);
fprintf('finshed parse mat file for %s!\n', vfilename);
