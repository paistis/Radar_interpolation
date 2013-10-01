
#ifndef MOTIONEXTRACTORDRIVER_H

#include "DenseMotionExtractor.h"
#include "SparseMotionExtractor.h"

#include <string>

class SparseVectorField;

using namespace std;

/// Implements methods for testing motion extractors and saving the results to disk.
/**
 * The methods in this class invoke motion extraction 
 * algorithms to extract motion between two source images. 
 * These methods also slightly blur the source images in order 
 * to achieve better results (gradient computation is 
 * sensitive to noise). 
 * The blurred images and the resulting motion image and 
 * motion vector quality images are saved with the 
 * following names:
 * [basename1]-smoothed.[extension]
 * [basename2]-smoothed.[extension]
 * [prefix]-motion.png
 * [prefix]-quality[n].png
 * 
 * where "basename1" and "basename2" are the 
 * names of the source images excluding their 
 * extensions and "prefix" is given by user. 
 */
class MotionExtractorDriver
{
public:
  /// Runs a dense motion extractor.
  /**
   * @param e motion extraction algorithm
   * @param srcFileName1 the file to read the first source image from
   * @param srcFileName2 the file to read the second source image from
   * @param outFileNamePrefix the prefix of the resulting images
   */
  static void runDenseMotionExtractor(DenseMotionExtractor &e,
                                      const string &src1,
                                      const string &src2,
                                      const string &outFilePrefix);
  
#ifdef WITH_CGAL
  /// Runs a sparse motion extractor.
  /**
   * @param e motion extraction algorithm
   * @param srcFileName1 the file to read the first source image from
   * @param srcFileName2 the file to read the second source image from
   * @param outFileNamePrefix the prefix of the resulting images
   */
  static void runSparseMotionExtractor(SparseMotionExtractor &e,
                                       const string &src1,
                                       const string &src2,
                                       const string &outFilePrefix);
#endif
private:
  static string getBaseName_(const string &fileName);
  
  static void preProcess_(const CImg< unsigned char > &I1,
                          const CImg< unsigned char > &I2,
                          CImg< unsigned char > &I1_smoothed,
                          CImg< unsigned char > &I2_smoothed,
                          CImg< unsigned char > &motionImageF,
                          CImg< unsigned char > *motionImageB = NULL);
  
  static void saveResultImages_(const string &srcFileName1,
                                const string &srcFileName2,
                                const string &outFilePrefix,
                                const CImg< unsigned char > &I1_smoothed,
                                const CImg< unsigned char > &I2_smoothed,
                                const CImg< unsigned char > &motionImageF,
                                const CImg< unsigned char > *motionImageB = NULL);
  
  static void saveResultMotionField_(const CImg< double > &VF,
                                     const string &outFilePrefix,
                                     const CImg< double > *VB = NULL);
  
#ifdef WITH_CGAL
  static void saveResultMotionField_(const SparseVectorField &V,
                                     const string &outFilePrefix);
#endif
};

#define MOTIONEXTRACTORDRIVER_H

#endif
