function imageclef_evaluation()
%% function imageclef_evaluation is a script to call the 'evalannotat.m' file
%   which is provied by ImageClef community
%
%  Especially, for the input file, we need 4 types of files
%   1, groundtruth decision, which is a txt file, eg. 'devel_groundtruth_tagmatrix.txt'
%   2, groundtruth mask, e.g. 'devel_groundtruth_tagmask.txt'
%   3, predict decision, e.g. 'devel_predict_decision.txt'
%   4, predict score, e.g. 'devel_predict_socres.txt'
clear all;
%% parse the files
ENV = 1; % 1: devel set 2: test set
if ENV == 1
    data_dir = '../data/devel_result';
else
    data_dir = '../data/test_result';
end

fprintf('...Evaluation for devel set on ImageCLEF2014 ...\n\n');

groundtruth_decision = logical(dlmread(fullfile(data_dir, 'devel_groundtruth_tagmatrix.txt')));
groundtruth_mask = logical(dlmread(fullfile(data_dir, 'devel_groundtruth_tagmask.txt')));
% predict_decision = logical(dlmread(fullfile(data_dir, 'devel_predict_decision.txt')));
% predict_score = dlmread(fullfile(data_dir, 'devel_predict_scores.txt'));


for K = 6
    fprintf('For K = %d \n', K);
    file_predict_decision = sprintf('clarifai_devel_predict_decision_K%d.txt',K);
    file_predict_score = sprintf('clarifai_devel_predict_scores_K%d.txt', K);
    predict_decision = logical(dlmread(fullfile(data_dir, file_predict_decision)));
    predict_score = dlmread(fullfile(data_dir, file_predict_score));

    [ sampRES, cnptRES, AP ] = evalannotat(groundtruth_decision, predict_decision, ...
        predict_score, groundtruth_mask);
    mean_sampRES = mean(sampRES);
    mean_cnptRES = mean(cnptRES);
    mAP = mean(AP);
    fprintf('For sampRES, P %f, R %f, F1 %f \n', mean_sampRES(1), mean_sampRES(2), mean_sampRES(3));
    fprintf('For cnptRES, P %f, R %f, F1 %f \n', mean_cnptRES(1), mean_cnptRES(2), mean_cnptRES(3));
    fprintf('For AP, mAP %f \n', mAP);
    fprintf('finished! \n\n');
    
    [new_predict_decision, new_predict_score] = select_dominant_topK(predict_decision, predict_score, 0.92);
    [ new_sampRES, new_cnptRES, new_AP ] = evalannotat(groundtruth_decision, new_predict_decision, ...
        new_predict_score, groundtruth_mask);
    mean_sampRES = mean(new_sampRES);
    mean_cnptRES = mean(new_cnptRES);
    mAP = mean(new_AP);
    fprintf('After the select dominant tags in each sample: \n')
    fprintf('For sampRES, P %f, R %f, F1 %f \n', mean_sampRES(1), mean_sampRES(2), mean_sampRES(3));
    fprintf('For cnptRES, P %f, R %f, F1 %f \n', mean_cnptRES(1), mean_cnptRES(2), mean_cnptRES(3));
    fprintf('For AP, mAP %f \n', mAP);
    fprintf('finished! \n\n');
end


%% evaluate baseline method (co-occurrence sift)
% baseline_decision = logical(dlmread(fullfile(data_dir, 'baseline_random_predict_decision.txt')));
% baseline_score = dlmread(fullfile(data_dir, 'baseline_random_predict_scores.txt'));
% [ sampRES, cnptRES, AP ] = evalannotat(groundtruth_decision, baseline_decision, ...
%     baseline_score, groundtruth_mask);
% mean_sampRES = mean(sampRES);
% mean_cnptRES = mean(cnptRES);
% mAP = mean(AP);
% fprintf('For sampRES, P %f, R %f, F1 %f \n', mean_sampRES(1), mean_sampRES(2), mean_sampRES(3));
% fprintf('For cnptRES, P %f, R %f, F1 %f \n', mean_cnptRES(1), mean_cnptRES(2), mean_cnptRES(3));
% fprintf('For AP, mAP %f \n', mAP);


function [new_predict_decision, new_predict_score] = select_dominant_topK(predict_decision, predict_score, sigma)
%% function select_dominant_topK is to select dominant values in matrix prediction_decision and predict_score
%   based on the cummulative sum of each row
%   
%   prediction_decision and predict_score are matrix with nSamples x nTags

[nSamples, nTags] = size(predict_score);

new_predict_decision = zeros(nSamples, nTags);
new_predict_score = zeros(nSamples, nTags);

% sort the value in row 
[predict_score_value, predict_score_indice] = sort(predict_score, 2, 'descend');

% make sum
predict_socre_cum = cumsum(predict_score_value, 2);
predict_score_sum = sum(predict_score_value, 2);

% norm the predict_score_value with sum
predict_score_norm = predict_socre_cum ./ repmat(predict_score_sum,1,nTags);
predict_score_norm(predict_score_norm == 1) = predict_score_norm(predict_score_norm == 1) +  eps;
predict_score_bool = predict_score_norm <= sigma;
% get the number of tag to be presverd in each sample
predict_score_dominant = sum(double(predict_score_bool), 2);

% now loop for each sample to assign the value in new_predict_decision and new_predict_score
for i = 1 : nSamples
    count = predict_score_dominant(i);
    values = predict_score_value(i, 1:count);
    indices = predict_score_indice(i, 1:count);
    
    new_predict_score(i, indices) = values;
    new_predict_decision(i, indices) = 1;
    
end

new_predict_decision = logical(new_predict_decision);
