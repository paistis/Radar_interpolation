
#include "DualDenseMotionExtractor.h"
#include <iostream>
#include "CImg_config.h"
#include <CImg.h>

void DualDenseMotionExtractor::compute(const CImg< unsigned int > &I1,
                                       const CImg< unsigned int > &I2,
                                       CImg< double > &V)
{
  CImg< double > VB;
  std::cout << "dual dence motion extractor compute\n";
  return compute(I1, I2, V, VB);
}
