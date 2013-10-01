function [] = makeimage(ifile,ofile)
%MAKEIMAGE Summary of this function goes here
%   Detailed explanation goes here
   % name = strcat(files(i))
    [test,R]= geotiffread(char(ifile));
    %test = medfilt2(test);
    %test(test>250) =0;
    K = mat2gray(test);
    %name = strsplit(char(name),'/');
    %name = strcat(dir2, name(numel(name)), '.png');
    imwrite(K,ofile,'PNG');
    close all;
end

