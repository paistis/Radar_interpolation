
#include "DualDenseMotionExtractor.h"
#include "PyramidalDenseMotionExtractor.h"

#include <stdexcept>

PyramidalDenseMotionExtractor::~PyramidalDenseMotionExtractor() { }

void PyramidalDenseMotionExtractor::compute(const CImg< unsigned char > &I1,
                                            const CImg< unsigned char > &I2,
                                            CImg< double > &V)
{
  CImg< double > VB; // not used
  compute(I1, I2, V, VB);
}

void PyramidalDenseMotionExtractor::compute(const CImg< unsigned char > &I1,
                                            const CImg< unsigned char > &I2,
                                            CImg< double > &VF,
                                            CImg< double > &VB)
{
  const int W = I1.dimx();
  const int H = I1.dimy();
	
  CImg< double > nextLevelVF;
  CImg< double > nextLevelVB;
  
  // Check that the input images have the same dimensions;
  if(I1.dimx() != I2.dimx() || 
     I1.dimy() != I2.dimy())
    throw invalid_argument("The dimensions of the input images must match.");
	
  // Check that the dimensions are powers of 2. 
  if(W == 0 || ( (W-1) & W ))
    throw invalid_argument("The image width is not a power of two.");
  if(H == 0 || ( (H-1) & H ))
    throw invalid_argument("The image height is not a power of two.");
	
  imagePyramids[0] = ImagePyramid(I1, NUMLEVELS);
  imagePyramids[1] = ImagePyramid(I2, NUMLEVELS);
	
  if(VF.dimx() != W || VF.dimy() != H || 
     VF.dimz() != getNumResultChannels())
    VF = CImg< double >(W, H, 1, 2 + getNumResultQualityChannels());
  if(isDual())
  {
    if(VB.dimx() != W || VB.dimy() != H || 
	VB.dimz() != getNumResultChannels())
      VB = CImg< double >(W, H, 1, 2 + getNumResultQualityChannels());
  }
  
  baseWidth = W;
  baseHeight = H;
	
  printInfoText();
	
  curLevelW = imagePyramids[0].getImageLevel(NUMLEVELS - 1).dimx();
  curLevelH = imagePyramids[0].getImageLevel(NUMLEVELS - 1).dimy();
	
  curLevelVF = CImg< double >(curLevelW, curLevelH, 1, getNumResultChannels());
  curLevelVF.fill(0);
  if(isDual())
  {
    curLevelVB = CImg< double >(curLevelW, curLevelH, 1, getNumResultChannels());
    curLevelVB.fill(0);
  }
	
  for(int i = NUMLEVELS - 1; i >= 0; i--)
  {
    computeLevel_(i, curLevelVF, curLevelVB);
    
    if(i > 0)
    {
      curLevelW *= 2;
      curLevelH *= 2;
      
      nextLevelVF = CImg< double >(curLevelW, curLevelH, 1, getNumResultChannels());
      if(isDual())
        nextLevelVB = CImg< double >(curLevelW, curLevelH, 1, getNumResultChannels());
      
      initializeNextLevel_(nextLevelVF, nextLevelVB);
      
      curLevelVF = nextLevelVF;
      if(isDual())
        curLevelVB = nextLevelVB;
    }
  }
  
  VF = curLevelVF;
  if(isDual())
    VB = curLevelVB;
}

bool PyramidalDenseMotionExtractor::isDual() const
{
  return motionExtractor->isDual();
}

PyramidalDenseMotionExtractor::PyramidalDenseMotionExtractor(int numLevels) : 
  NUMLEVELS(numLevels)
{ }

void PyramidalDenseMotionExtractor::computeLevel_(int level,
                                                  CImg< double > &VF,
                                                  CImg< double > &VB)
{
  curLevelI[0].assign(imagePyramids[0].getImageLevel(level), true);
  curLevelI[1].assign(imagePyramids[1].getImageLevel(level), true);
	
  if(isDual())
    dynamic_cast< DualDenseMotionExtractor * >(motionExtractor)->
      compute(curLevelI[0], curLevelI[1], VF, VB);
  else
    motionExtractor->compute(curLevelI[0], curLevelI[1], VF);
}

void PyramidalDenseMotionExtractor::initializeNextLevel_(CImg< double > &nextLevelVF,
                                                         CImg< double > &nextLevelVB)
{
  const int WOLD = curLevelVF.dimx();
  const int HOLD = curLevelVF.dimy();
  const int WNEW = nextLevelVF.dimx();
  const int HNEW = nextLevelVF.dimy();
  
  double vxf, vyf;
  double vxb, vyb;
	
  double xc, yc;
  int xn, yn;
  
  for(yn = 0; yn < HNEW; yn++)
  {
    yc = yn / 2.0;
    for(xn = 0; xn < WNEW; xn++)
    {
      xc = xn / 2.0;
      if(xn % 2 != 0 || yn % 2 != 0)
      {
        vxf = curLevelVF.linear_at4(xc, yc, 0, 0);
        vyf = curLevelVF.linear_at4(xc, yc, 0, 1);
        if(isDual())
        {
          vxb = curLevelVB.linear_at4(xc, yc, 0, 0);
          vyb = curLevelVB.linear_at4(xc, yc, 0, 1);
        }
      }
      else
      {
        vxf = curLevelVF(xc, yc, 0, 0);
        vyf = curLevelVF(xc, yc, 0, 1);
        if(isDual())
        {
          vxb = curLevelVB(xc, yc, 0, 0);
          vyb = curLevelVB(xc, yc, 0, 1);
        }
      }
      
      nextLevelVF(xn, yn, 0, 0) = 2.0 * vxf;
      nextLevelVF(xn, yn, 0, 1) = 2.0 * vyf;
      if(isDual())
      {
        nextLevelVB(xn, yn, 0, 0) = 2.0 * vxb;
        nextLevelVB(xn, yn, 0, 1) = 2.0 * vyb;
      }
    }
  }
}
