function [ corr_coef] = morph_corr2( pic1, pic2)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
pic1(pic1 <= -50) = nan;
pic2(pic2 <= -50) = nan;
C = pic1+pic2;
pic1 = C-pic2;
pic2 = C-pic1;
corr_coef = corr2(pic1(isfinite(pic1(:))),pic2(isfinite(pic2)));

end

