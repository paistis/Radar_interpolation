%picture 1 information and reading
kum_dir = dir('/home/nordlikg/fmi/test_interpolation/images/kum');
van_dir = dir('/home/nordlikg/fmi/test_interpolation/images/van');
corr_coef = [];
for file = 3:numel(kum_dir)
    van_file = ['van/' van_dir(file).name];
    kum_file = ['kum/' kum_dir(file).name];
    [pic1 R1] = geotiffread(van_file); 
    info1 = geotiffinfo(van_file);
    %picture 2 information and reading
    [pic2 R2] = geotiffread(kum_file); 
    info2 = geotiffinfo(kum_file);
    %get latitude and longiture of the picture
    lat1 = info1.CornerCoords.Lat;
    lat2 = info2.CornerCoords.Lat;
    lon1 = info1.CornerCoords.Lon;
    lon2 = info2.CornerCoords.Lon;
    %make latitude and longitude vectors
    lat1 = linspace(min(lat1(:)),max(lat1(:)),size(pic1,1));
    lat2 = linspace(min(lat2(:)),max(lat2(:)),size(pic2,1));
    lon1 = linspace(min(lon1(:)),max(lon1(:)),size(pic1,2));
    lon2 = linspace(min(lon2(:)),max(lon2(:)),size(pic2,2));
    %find same index's
    %firs some rounding
    lat1_round = floor(lat1*1000)/1000;
    lat2_round = floor(lat2*1000)/1000;
    lon1_round = floor(lon1*1000)/1000;
    lon2_round = floor(lon2*1000)/1000;
    %find intersect
    [C, lat1_ind, lat2_ind] = intersect(lat1_round,lat2_round);
    [C, lon1_ind, lon2_ind] = intersect(lon1_round,lon2_round);
    %make temp matrix from new pictures
    pic1_new = ones(numel(lat1_ind),numel(lon1_ind));
    pic2_new = ones(numel(lat2_ind),numel(lon2_ind));
    for lat_ = 1:numel(lat1_ind)
        for lon_ = 1:numel(lon1_ind)
            %map pixel from old picture to new one
            pic1_new(lat_,lon_) = pic1(lat1_ind(lat_),lon1_ind(lon_));
            pic2_new(lat_,lon_) = pic2(lat2_ind(lat_),lon2_ind(lon_));
        end
    end
    pic1_new(isnan(pic1_new(:))) = 0;
    pic2_new(isnan(pic2_new(:))) = 0;
    corr_coef = [corr_coef, corr2(pic1_new,pic2_new)];
end