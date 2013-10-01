function [ corr_coef] = morph_corr2( pic1, pic2)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
%filter out some noise
%pic1(pic1 <= -50) = nan;
%pic2(pic2 <= -50) = nan;


C = pic1+pic2;
pic1 = C-pic2;
pic2 = C-pic1;
corr_coef = corr2(pic1(isfinite(pic1(:))),pic2(isfinite(pic2)))
mean_bias = mean(pic1(isfinite(pic1(:)))-pic2(isfinite(pic2)))
figure;plot(pic1(:),pic2(:),'.');title('without filtering')
disp('Filtering...')

pic1(pic1 < 10) = nan;
pic2(pic2 < 10) = nan;

pic1(pic1 >= 50) = 50;
pic2(pic2 >= 50) = 50;

C = pic1+pic2;
pic1 = C-pic2;
pic2 = C-pic1;
figure;imagesc(pic1);title('real')
figure;imagesc(pic2);title('morp')
corr_coef = corr2(pic1(isfinite(pic1(:))),pic2(isfinite(pic2)))
mean_bias = mean(pic1(isfinite(pic1(:)))-pic2(isfinite(pic2)))

figure;
hold on
plot(pic1(:),pic2(:),'.')
plot([10,50],[10,50],'LineWidth',5,'Color','red');
title('with filtering, 10-50 db values')

end

