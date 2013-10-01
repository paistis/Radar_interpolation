dir_ = '/home/nordlikg/fmi/tiffs/20100808/VAN/';
dir2 = '/home/nordlikg/fmi/pngs/20100808/VAN/';
files = strsplit(ls(dir_));
close all;
for i = 1:numel(files)
    name = strcat(dir_, files(i))
    [test,R]= geotiffread(char(name));
    imagesc(test)
    pause(5)
    clim = get(gca,'clim')
    levels = 255
    target = grayslice(test,linspace(clim(1),clim(2),levels));
    map=jet(levels);
    name = strcat(dir2, files(i), '.png');
    imwrite(target,map,char(name));
    close all;
end
