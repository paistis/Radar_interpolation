
#ifndef IMAGEPYRAMID_H

#include <vector>

namespace cimg_library { template < class T > class CImg; }

using namespace cimg_library;
using namespace std;

/// Implements an image pyramid.
/**
 * This class contains the implementation of image pyramid. 
 * Image pyramid is an ordered set of scaled instances of 
 * a given source image.
 */
class ImagePyramid
{
public:
  /// Constructs an empty image pyramid
  ImagePyramid();
  
  /// Constructs an n-level pyramid from a given source image.
  /**
   * This method constructs an n-level pyramid from a given source image.
   * @param I0 source image
   * @param n number of levels
   */
  ImagePyramid(const CImg< unsigned int > &I0, int n);
  
  /// Returns a reference to the ith level of this image pyramid.
  const CImg< unsigned int > &getImageLevel(int i) const;
  
  /// Returns the number of levels in this image pyramid.
  int getNumLevels() const;
private:
  vector< CImg< unsigned int > > levels_;
  
  void computeNextLevel_(const CImg< unsigned int > &src,
                         CImg< unsigned int > &dest);
};

#define IMAGEPYRAMID_H

#endif
