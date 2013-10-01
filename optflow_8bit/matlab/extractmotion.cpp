#include "DenseMotionExtractor.h"
#include "PyramidalLucasKanade.h"
#include "PyramidalProesmans.h"
#if defined (WITH_OPENCV) && defined(WITH_CGAL)
#include "LucasKanadeOpenCV.h"
#include "SparseMotionExtractor.h"
#endif
#include "VectorFieldIllustrator.h"

#include <iostream>
#include "mex.h"

using namespace std;

static const char *ALGORITHM_NAMES[] = 
{
  "Proesmans",
  "LucasKanade",
  "OpenCV"
};

static const int NUM_ALGORITHMS = 3;

static void parseMandatoryArgs(
  int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[], 
  CImg< unsigned char > &I1, CImg< unsigned char > &I2, int &w, int &h, 
  string &algoName)
{
  if(nrhs != 3)
    mexErrMsgTxt("Must have at least three input arguments");
  if(!mxIsUint8(prhs[0]) || !mxIsUint8(prhs[1]))
    mexErrMsgTxt("Source images must be 8-bit unsigned integer arrays");
  if(!mxIsChar(prhs[2]))
    mexErrMsgTxt("The third argument must be a string");

  const mxArray *I1_arg = prhs[0];
  int m = mxGetM(I1_arg);
  int n = mxGetN(I1_arg);
  const mxArray *I2_arg = prhs[1];
  int m2 = mxGetM(I2_arg);
  int n2 = mxGetN(I2_arg);

  if(m != m2 || n != n2)
    mexErrMsgTxt("Mismatching input image dimensions");

  I1 = CImg< unsigned char >(n, m);
  unsigned char *data = (unsigned char *)mxGetData(I1_arg);
  for(int j = 0; j < n; j++)
    for(int i = 0; i < m; i++)
      I1(j, i) = data[i + j*m];

  I2 = CImg< unsigned char >(n, m);
  data = (unsigned char *)mxGetData(I2_arg);
  for(int j = 0; j < n; j++)
    for(int i = 0; i < m; i++)
      I2(j, i) = data[i + j*m];

  w = n;
  h = m;
  
  char *algoName_ = new char[mxGetN(prhs[2])+1];
  mxGetString(prhs[2], algoName_, mxGetN(prhs[2])+1);
  algoName = string(algoName_);
  delete algoName_;
  bool validName = false;
  for(int i = 0; i < NUM_ALGORITHMS; i++)
    if(algoName == ALGORITHM_NAMES[i])
    {
      validName = true;
      break;
    }
}

/*
 * Arguments:
 * I1            first source image
 * I2            second source image
 * 
 * Return values:
 * V             the computed motion vector field
 * VI            quiver plot of the computed motion field
 */
void mexFunction(
  int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
  CImg< unsigned char > I1, I2;
  string algoName;
  int w, h;
  int x, y, c;
  CImg< unsigned char > VI;
  
  parseMandatoryArgs(nlhs, plhs, nrhs, prhs, I1, I2, w, h, algoName);
  if(nlhs >= 4)
  {
    VI = CImg< unsigned char >(w, h, 1, 3);
    VI.get_shared_channel(0) = I1;
    VI.get_shared_channel(1) = I1;
    VI.get_shared_channel(2) = I1;
  }

  if(algoName == "Proesmans" || algoName == "LucasKanade")
  {
    CImg< double > V;
    if(algoName == "Proesmans")
    {
      PyramidalProesmans me;
      me.compute(I1, I2, V);
    }
    else if(algoName == "LucasKanade")
    {
      PyramidalLucasKanade me;
      me.compute(I1, I2, V);
    }
    
    if(nlhs >= 2)
    {
      plhs[0] = mxCreateDoubleMatrix(w, h, mxREAL);
      double *data = mxGetPr(plhs[0]);
      for(y = 0; y < h; y++)
        for(x = 0; x < w; x++)
          data[y + x*h] = V(x, y, 0, 0);

      plhs[1] = mxCreateDoubleMatrix(w, h, mxREAL);
      data = mxGetPr(plhs[1]);
      for(y = 0; y < h; y++)
        for(x = 0; x < w; x++)
          data[y + x*h] = V(x, y, 0, 1);
    }
    if(nlhs >= 3)
    {
      plhs[2] = mxCreateDoubleMatrix(w, h, mxREAL);
      double *data = mxGetPr(plhs[2]);
      for(y = 0; y < h; y++)
        for(x = 0; x < w; x++)
          data[y + x*h] = V(x, y, 0, 2);
    }
    if(nlhs >= 4)
      VectorFieldIllustrator::renderDenseVectorField(V, VI);
  }
#if defined (WITH_OPENCV) && defined(WITH_CGAL)
  else
  {
    LucasKanadeOpenCV me;
    SparseVectorField V;
    me.compute(I1, I2, V);
    
    if(nlhs >= 2)
    {
      plhs[0] = mxCreateDoubleMatrix(w, h, mxREAL);
      plhs[1] = mxCreateDoubleMatrix(w, h, mxREAL);
    }
    
    if(nlhs >= 3)
    {
      plhs[2] = mxCreateDoubleMatrix(w, h, mxREAL);
      // TODO: quality field for the OpenCV algorithm?
    }
    
    if(nlhs >= 4)
    {
      V.triangulate();
      VectorFieldIllustrator::renderSparseVectorField(V, VI);
    }
  }
#endif
  
  if(nlhs >= 4)
  {
    const mwSize dims[] = { w, h, 3 };
    plhs[3] = mxCreateNumericArray(3, dims, mxUINT8_CLASS, mxREAL);
    unsigned char *data = (unsigned char *)mxGetData(plhs[3]);
    for(y = 0; y < h; y++)
      for(x = 0; x < w; x++)
        for(c = 0; c < 3; c++)
          data[y + x*h + c*w*h] = VI(x, y, 0, c);
  }
}

