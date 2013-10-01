van600 = geotiffread('VAN-16bit_600_20008081650_-morph-16.tiff');
van800 = geotiffread('VAN-16bit_800_20008081650_-morph-16.tiff');
van1000 = geotiffread('VAN-16bit_1000_20008081650_-morph-16.tiff');
van1200 = geotiffread('VAN-16bit_1200_20008081650_-morph-16.tiff');
van1400 = geotiffread('VAN-16bit_1400_20008081650_-morph-16.tiff');

comp_data = geotiffread('van_1705.tiff');

comp_data = imresize(comp_data,size(van600));
comp_data600 = comp_data;
comp_data800 = comp_data;
comp_data1000 = comp_data;
comp_data1200 = comp_data;
comp_data1400 = comp_data;

C = van600 + comp_data600;
van600 = C - comp_data600;
comp_data600 = C - van600;

C = van800 + comp_data800;
van800 = C - comp_data800;
comp_data800 = C - van800;

C = van1000 + comp_data1000;
van1000 = C - comp_data1000;
comp_data1000 = C - van1000;

C = van1200 + comp_data1200;
van1200 = C - comp_data1200;
comp_data1200 = C - van1200;

C = van1400 + comp_data1400;
van1400 = C - comp_data1400;
comp_data1400 = C - van1400;

corr600 = corr2(van600(isfinite(van600(:))),comp_data600(isfinite(comp_data600)));
corr800 = corr2(van800(isfinite(van800(:))),comp_data800(isfinite(comp_data800)));
corr1000 = corr2(van1000(isfinite(van1000(:))),comp_data1000(isfinite(comp_data1000)));
corr1200 = corr2(van1200(isfinite(van1200(:))),comp_data1200(isfinite(comp_data1200)));
corr1400 = corr2(van1400(isfinite(van1400(:))),comp_data1400(isfinite(comp_data1400)));