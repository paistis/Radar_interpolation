%same time
[van1 R] = geotiffread('VAN_Z2_sweep1_wgs.tiff');
[van2 R] = geotiffread('VAN_Z2_sweep2_wgs.tiff');

[ker3 R] = geotiffread('KER_Z2_sweep3_wgs.tiff');
[ker2 R] = geotiffread('KER_Z2_sweep2_wgs.tiff');
[ker1 R] = geotiffread('KER_Z2_sweep1_wgs.tiff');

[kum1 R] = geotiffread('KUM_Z2_sweep1_wgs.tiff');
[kum2 R] = geotiffread('KUM_Z2_sweep2_wgs.tiff');
[kum3 R] = geotiffread('KUM_Z2_sweep3_wgs.tiff');

%time missalighment

[kum2_1715 R] = geotiffread('KUM_1715_Z2_sweep2_wgs.tiff');
[kum1_1715 R] = geotiffread('KUM_1715_Z2_sweep1_wgs.tiff');

[van1_1650 R] = geotiffread('VAN_1650_Z2_sweep1_wgs.tiff');
[van2_1650 R] = geotiffread('VAN_1650_Z2_sweep2_wgs.tiff');

%remove nans

%resize
%kumpula pictures to same size as kerava
kum1_ker = imresize(kum1,size(ker1),'nearest');
kum2_ker = imresize(kum2,size(ker2),'nearest');
kum3_ker = imresize(kum3,size(ker3),'nearest');

%kumpula pictures to same size as vantaa
kum1_van = imresize(kum1,size(van1),'nearest');
kum2_van = imresize(kum2,size(van2),'nearest');

%kerava pictures to same size as vantaa
ker1_van = imresize(ker1,size(van1),'nearest');
ker2_van = imresize(ker2,size(van2),'nearest');


kum1_ker_1715 = imresize(kum1_1715,size(ker1),'nearest');
kum2_ker_1715 = imresize(kum2_1715,size(ker2),'nearest');

ker1_1700_van = imresize(ker1,size(van1_1650),'nearest');
ker2_1700_van = imresize(ker2,size(van2_1650),'nearest');



