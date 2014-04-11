function [ sampRES, cnptRES, AP ] = evalannotat( GTMAT, DEC, SCO, MASK )
%
% EVALANNOTAT: Computes evaluation measures for image annotation
%
% Usage:
%   [ sampRES, cnptRES, AP ] = evalannotat( GTMAT, DEC [, SCO, MASK] )
%
% Input:
%   GTMAT (logical)      - Ground truth matrix (Nconcepts x Nte)
%   DEC   (logical)      - Annotation decisions (Nconcepts x Nte)
%   SCO   (double)       - Concept scores (Nconcepts x Nte)
%   MASK  (logical)      - Concept list mask per sample (Nconcepts x Nte)
%
% Output:
%   sampRES              - Precision, Recall, F-measure (for decisions, per sample)
%   cnptRES              - Precision, Recall, F-measure (for decisions, per concept)
%   AP                   - Average precision (for scores, per sample)
%
%
% $Revision: 196 $
% $Date: 2013-12-15 21:31:53 +0100 (Sun, 15 Dec 2013) $
%

% Copyright (C) 2012 Mauricio Villegas (mvillegas AT iti.upv.es)
%
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License
% along with this program. If not, see <http://www.gnu.org/licenses/>.

fn = 'evalannotat:';

%%% Error detection %%%
if nargin<2
  error(['mvo:' fn 'args'],[fn ' error: not enough input arguments']);
elseif ~islogical(GTMAT) || ~islogical(DEC) || ...
    ( exist('MASK','var') && ~islogical(MASK) )
  error(['mvo:' fn 'logi'],[fn ' error: GTMAT, DEC and MASK must be logical']);
elseif sum(size(DEC)~=size(GTMAT))>0 || ...
    ( exist('SCO','var') && sum(size(SCO)~=size(GTMAT))>0 ) || ...
    ( exist('MASK','var') && sum(size(MASK)~=size(GTMAT))>0 )
  error(['mvo:' fn 'dims'],[fn ' error: dimensions of SCO, DEC or MASK inconsistent with GTMAT']);
end

%%% Compute evaluation measures %%%

%%% Measures per concept %%%
cnptRES(:,1) = sum(GTMAT&DEC,2)./sum(DEC,2); %%% Precision %%%
cnptRES(~isfinite(cnptRES(:,1)),1) = 0;
cnptRES(:,2) = sum(GTMAT&DEC,2)./sum(GTMAT,2); %%% Recall %%%
cnptRES(~isfinite(cnptRES(:,2)),2) = 0;
cnptRES(:,3) = 2*(cnptRES(:,1).*cnptRES(:,2))./(cnptRES(:,1)+cnptRES(:,2)); %%% F-measure %%%
cnptRES(~isfinite(cnptRES(:,3)),3) = 0;

%%% Measures per sample %%%
sampRES(:,1) = (sum(GTMAT&DEC,1)./sum(DEC,1))'; %%% Precision %%%
sampRES(~isfinite(sampRES(:,1)),1) = 0;
sampRES(:,2) = (sum(GTMAT&DEC,1)./sum(GTMAT,1))'; %%% Recall %%%
sampRES(~isfinite(sampRES(:,2)),2) = 0;
sampRES(:,3) = 2*(sampRES(:,1).*sampRES(:,2))./(sampRES(:,1)+sampRES(:,2)); %%% F-measure %%%
sampRES(~isfinite(sampRES(:,3)),3) = 0;

AP = [];
if exist('SCO','var')
  Nte = size(GTMAT,2);
  AP = zeros(Nte,1);
  for nte=1:Nte
    %%% Sort sample concept scores %%%
    [ sSCOMAT, sidx ] = sort(-SCO(:,nte));
    %%% Remove concepts not in list %%%
    if exist('MASK','var')
      rmelem = ismember(sidx,find(~MASK(:,nte)));
      sidx(rmelem) = [];
      sSCOMAT(rmelem) = [];
    end
    %%% Random permutation within score ties %%%
    df = diff(sSCOMAT);
    if sum(df==0)>0
      df(df==0) = max(df);
      [ sSCOMAT2, sidx2 ] = sort(sSCOMAT-0.8*min(df)*rand(size(sSCOMAT)));
      sidx = sidx(sidx2);
    end
    %%% Compute the average precision for sample %%%
    GTPOS = find(GTMAT(sidx,nte));
    N = size(GTPOS,1);
%     if N == 0
%         AP(nte,1) = 0;
%         continue;
%     end
    nPREC = [1:N]'./GTPOS;
    AP(nte,1) = mean(nPREC);
  end
end
