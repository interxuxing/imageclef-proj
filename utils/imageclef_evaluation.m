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
ENV = 1 % 1: devel set 2: test set
if ENV == 1
    data_dir = '../data/devel_result'
else
    data_dir = '../data/test_result'
end


groundtruth_decision = logical(dlmread(fullfile(data_dir, 'devel_groundtruth_tagmatrix.txt')));
groundtruth_mask = logical(dlmread(fullfile(data_dir, 'devel_groundtruth_tagmask.txt')));
% predict_decision = logical(dlmread(fullfile(data_dir, 'devel_predict_decision.txt')));
% predict_score = dlmread(fullfile(data_dir, 'devel_predict_scores.txt'));


% for K = 4:9
%     fprintf('For K = %d \n', K);
%     file_predict_decision = sprintf('clarifai_devel_predict_decision_K%d.txt',K);
%     file_predict_score = sprintf('clarifai_devel_predict_scores_K%d.txt', K);
%     predict_decision = logical(dlmread(fullfile(data_dir, file_predict_decision)));
%     predict_score = dlmread(fullfile(data_dir, file_predict_score));
% 
%     [ sampRES, cnptRES, AP ] = evalannotat(groundtruth_decision, predict_decision, ...
%         predict_score, groundtruth_mask);
%     mean_sampRES = mean(sampRES);
%     mean_cnptRES = mean(cnptRES);
%     mAP = mean(AP);
%     fprintf('For sampRES, P %f, R %f, F1 %f \n', mean_sampRES(1), mean_sampRES(2), mean_sampRES(3));
%     fprintf('For cnptRES, P %f, R %f, F1 %f \n', mean_cnptRES(1), mean_cnptRES(2), mean_cnptRES(3));
%     fprintf('For AP, mAP %f \n', mAP);
%     fprintf('finished! \n');
% end


%% evaluate baseline method (co-occurrence sift)
baseline_decision = logical(dlmread(fullfile(data_dir, 'baseline_random_predict_decision.txt')));
baseline_score = dlmread(fullfile(data_dir, 'baseline_random_predict_scores.txt'));
[ sampRES, cnptRES, AP ] = evalannotat(groundtruth_decision, baseline_decision, ...
    baseline_score, groundtruth_mask);
mean_sampRES = mean(sampRES);
mean_cnptRES = mean(cnptRES);
mAP = mean(AP);
fprintf('For sampRES, P %f, R %f, F1 %f \n', mean_sampRES(1), mean_sampRES(2), mean_sampRES(3));
fprintf('For cnptRES, P %f, R %f, F1 %f \n', mean_cnptRES(1), mean_cnptRES(2), mean_cnptRES(3));
fprintf('For AP, mAP %f \n', mAP);
