function demo_svm()
%% function demo_svm() is a demo script to use linear SVM classifiers
% 
clc;
%% add path
addpath('../utils/');

eval('config_file_imageclef');


%% load groundtruth tags for dev set
tagmatrixTr = dlmread(fullfile(DST_FEA_DIR, 'dev', DevFiles.tagmatrix));
[imgNum, tagNum] = size(tagmatrixTr);

%% load tagmask for dev set
tagmaskTr = dlmread(fullfile(DST_FEA_DIR, 'dev', DevFiles.tagmask));
%% load visual feature files for dev set (mat type)
featTr = [];
tagTr = [];

for i = 1 : length(FeatureFilesDev)
    % get mat file name
    matFile = strrep(FeatureFilesDev{i}, '.feat', '.mat');
    load(fullfile(DST_FEA_DIR, 'dev', matFile));
    featTr = [featTr, featMat];
    fprintf('load mat data for %s finished! \n', matFile);
end

if size(tagmatrixTr,1) ~= size(featTr, 1)
    error('tag matrix should have same dimension as featMat!');
end


%% use svm classifiers for training
if SVM.bCrossValSVM
    % loop for each tag
    for t = 1 : tagNum
        maxci{t} = 1;
        maxmap{t} = 0;
        gtTag = tagmatrixTr(:, t);
        
        pNum = length(find(gtTag == 1));
        nNum = length(gtTag) - pNum;
        fprintf('For tag %d, positive Num: %d, negative Num %d \n', t, pNum, nNum);
        
        for ci = 1 : length(SVM.cList)
            c = pow2(SVM.cList(ci));
            model = svmtrain(gtTag, featTr, sprintf(' -q -t 0 -c %f', pow2(c)));
            
            % use model to predict
            [pred_label, acc, dec_value] = svmpredict(gtTag, featTr, model);
            
            % evaluate ap
            GTMAT = logical(gtTag');
            DEC = logical(pred_label');
            SCO = exp(dec_value');
            MASK = logical(tagmaskTr(:,t)');
            [sampRES, cnptRES, AP] = evalannotat(GTMAT, DEC, SCO, MASK);
            map = mean(AP);
            fprintf('...for tag %d, c %f, map %f \n', t, c, map);
            fprintf('... ... concept P %f, R %f, F1 %f \n', cnptRES(1), cnptRES(2), cnptRES(3));
            if map > maxmap{t}
                maxci{t} = ci;
                maxmap{t} = map;
            end
        end
    end
end

fprintf('learned finished!\n');
