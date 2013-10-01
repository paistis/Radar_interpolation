require("raster")
require("fields")

ker = raster("ker.tif")
kum = raster("kum.tif")

kerc=resample(ker,kum,method='ngb')
print(paste("Correlation = ",cor(as.vector(kerc),as.vector(kum),use='complete.obs')))
png("diff.png")
plot(kum-kerc,col=tim.colors(),zlim=c(-60,60),main="Kumupa - Kerava")
dev.off()
quit()
