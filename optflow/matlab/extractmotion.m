%EXTRACTMOTION Extract motion from the given pair of source images. 
%   EXTRACTMOTION(I1,I2,ALGO,OPTS), where I1 and I2 are the mxn source images 
%   specified as 8-bit matrices and ALGO is a string specifying 
%   the name of the algorithm. 
%   The implemented algorithms are:
%     LucasKanade     local least-squares fitting algorithm by Lucas 
%                     and Kanade
%     OpenCV          the OpenCV implementation of the Lucas and Kanade 
%                     algorithm
%     Proesmans       anisotropic diffusion algorithm by Proesmans et al.
%
%   Optional parameters for algorithms are specified with array OPTS, 
%   see below.
%
%   [U,V,Q,VI] = EXTRACTMOTION(I1,I2,algo) returns the x and y 
%   components of the extracted motion vectors (stored to 
%   double mxn matrices U and V, respectively). Q is a cell 
%   array of motion vector quality measures (one mxn double matrix 
%   for each quality channel). A quiver plot of the extracted motion 
%   vector field is stored to VI as a 8-bit mxn image.
%
%   Optional arguments for algorithms (OPTS array):
%     LucasKanade:
%       
%     OpenCV:
%       
%
%     Proesmans:
%       OPTS(1)   number of pyramid levels (default = 4)  
%       OPTS(2)   number of iterations (default = 200)
%       OPTS(3)   smoothness parameter (default = 100)
%       OPTS(4)   boundary conditions (0 = Dirichlet, 1 = Neumann)
%                 (default = 1)

