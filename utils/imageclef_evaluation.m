function imageclef_evaluation()
%% function imageclef_evaluation is a script to call the 'evalannotat.m' file
%   which is provied by ImageClef community
%
%  Especially, for the input file, we need 4 types of files
%   1, groundtruth decision, which is a txt file, eg. 'devel_groundtruth_tagmatrix.txt'
%   2, groundtruth mask, e.g. 'devel_groundtruth_tagmask.txt'
%   3, predict decision, e.g. 'devel_predict_decision.txt'
%   4, predict score, e.g. 'devel_predict_socres.txt'

%% parse the files
data_dir = '../data'

groundtruth_decision = logical(dlmread(fullfile(data_dir, 'devel_groundtruth_tagmatrix.txt')));
groundtruth_mask = logical(dlmread(fullfile(data_dir, 'devel_groundtruth_tagmask.txt')));
% predict_decision = logical(dlmread(fullfile(data_dir, 'devel_predict_decision.txt')));
% predict_score = dlmread(fullfile(data_dir, 'devel_predict_scores.txt'));

predict_decision = logical(dlmread(fullfile(data_dir, 'clarifai_devel_predict_decision.txt')));
predict_score = dlmread(fullfile(data_dir, 'clarifai_devel_predict_scores.txt'));

[ sampRES, cnptRES, AP ] = evalannotat(groundtruth_decision, predict_decision, ...
    predict_score, groundtruth_mask);

fprintf('finished!'\n);
