function [] = boundary(filename)
    %filename = '201008081710_VAN.PPI3_A.raw.h5_with_rayHdrs_F_Z2.png';
    [van8bit]= imread(filename);
    s=strel('disk',20);
    D=~im2bw(van8bit);
    BW = im2bw(van8bit,graythresh(van8bit));
    F=imerode(D,s);
    %figure,imshow(van8bit);title('original file');
    %figure,imshow(D);title('bw image');
    %figure,imshow(D-F);title('boundary');
    B = D-F;
    h = fspecial('gaussian');
    B = imfilter(B,h);
    I = van8bit;
    I((B == 1)) = nan;
    [path,name,ext] = fileparts(filename);
    filename_new = [name,'.png'];

    %gaussian filtering
    h = fspecial('gaussian');
    I = imfilter(I,h);
    imwrite(I,filename_new,'png');
    
end
