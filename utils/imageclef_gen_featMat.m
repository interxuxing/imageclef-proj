function imageclef_save_featMat(config_file)
%% function image_gen_feaMat(config_file) save mat format for original
% feat files in dev/test set

%%
clc;
eval(config_file);


%% loop for each feat file in dev set
for i = 1 : length(FeatureFilesDev)
    % unzip the .feat.gz file
    gzFilename = [FeatureFilesDev{i}, '.feat.gz'];
    featFilename = gunzip(fullfile(DST_FEA_DIR, 'dev', gzFilename)); % full path
    
    % parse feat file
    featMat = imageclef_parse_featfile(featFilename{1});
    
    % save in mat file
    matFilename = strrep(featFilename{1}, '.feat', '.mat');
    save(matFilename, 'featMat');
end

fprintf('generate mat file for dev set finished! \n');
