clear all;

I1 = imread('../examples/simple1.png');
I2 = imread('../examples/simple2.png');

[U1, V1, Q1, VI1] = extractmotion(I1, I2, 'Proesmans');
[U2, V2, Q2, VI2] = extractmotion(I1, I2, 'LucasKanade');
[U3, V3, Q3, VI3] = extractmotion(I1, I2, 'OpenCV');

figure();
imshow(VI1);
title('Example Motion Field, Proesmans Algorithm');

figure();
imshow(VI2);
title('Example Motion Field, Lucas&Kanade Algorithm');

figure();
imshow(VI3);
title('Example Motion Field, OpenCV Algorithm');

