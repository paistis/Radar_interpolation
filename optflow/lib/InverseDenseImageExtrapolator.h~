
#ifndef INVERSEDENSEIMAGEEXTRAPOLATOR_H

#include "DenseImageExtrapolator.h"

/// Implements inverse image extrapolation with dense motion fields.
/**
 * Inverse image extrapolation method tries to find 
 * for each pixel in the destination image its corresponding 
 * pixel in the source image. The inverse motion 
 * field between two source images is required for this.
 */
class InverseDenseImageExtrapolator : public DenseImageExtrapolator
{
public:
  void extrapolate(const CImg< unsigned char > &I0, 
                   const CImg< double > &V,
                   double multiplier,
                   CImg< unsigned char > &Ie) const;
};

#define INVERSEDENSEIMAGEEXTRAPOLATOR_H

#endif
 
