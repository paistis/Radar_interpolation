
#include "InverseDenseImageExtrapolator.h"

#include "CImg_config.h"
#include <CImg.h>

using namespace cimg_library;

void InverseDenseImageExtrapolator::extrapolate(const CImg< unsigned char > &I0,
                                                const CImg< double > &V,
                                                double multiplier,
                                                CImg< unsigned char > &Ie) const
{
  const int W = I0.dimx();
  const int H = I0.dimy();
  
  double u, v;
  
  Ie = CImg< unsigned char >(I0.dimx(), I0.dimy(), 1, 1);
  Ie.fill(0);
  
  for(int i = 0; i < H; i++)
  {
    for(int j = 0; j < W; j++)
    {
      u = V(j, i, 0, 0);
      v = V(j, i, 0, 1);
      Ie(j, i) = I0.cubic_at(j + multiplier * u, i + multiplier * v);
    }
  }
}
