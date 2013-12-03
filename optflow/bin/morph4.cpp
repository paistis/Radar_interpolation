
#include "DenseImageMorpher.h"
#if defined (WITH_OPENCV) && defined(WITH_CGAL)
#include "LucasKanadeOpenCV.h"
#endif
#include "PyramidalProesmans.h"
#include "SparseImageMorpher.h"
#include "SparseVectorField.h"
#include "VectorFieldIllustrator.h"
#include "version.h"
#include "DenseVectorFieldIO.h"

#include <boost/program_options.hpp>
#include "CImg_config.h"
#include <CImg.h>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <sstream>

using namespace boost::program_options;
using namespace cimg_library;
using namespace std;

/*enum AlgorithmType { LKOPENCV, PROESMANS };

struct ArgData
{
  CImg< unsigned char > I1;
  CImg< unsigned char > I2;
  int numSteps;
  AlgorithmType algorithmType;
  string outFilePrefix;
};

bool parseArgs(int argc, char **argv, ArgData &result)
{
  int num_errors;
  bool success = false;
  
  struct arg_file *image1filename = arg_file1(NULL, NULL, "<image1>",        "first source image");
  struct arg_file *image2filename = arg_file1(NULL, NULL, "<image2>",        "second source image");
  struct arg_int *numsteps        = arg_int1(NULL,  NULL, "<numsteps>",      "number of intermediate images");
  struct arg_str *algorithmname   = arg_str1(NULL,  NULL, "<algorithmname>", "motion extraction algorithm");
  struct arg_str *outfileprefix   = arg_str1(NULL,  NULL, "<outfileprefix>", "prefix for output file names");
  struct arg_end *end             = arg_end(20);
  
  void *argtable[] = 
  {
    image1filename,
    arg_rem(NULL, "(8-bit grayscale image, width and height "),
    arg_rem(NULL, "are powers of two)"),
    image2filename,
    arg_rem(NULL, "(8-bit grayscale image, width and height "),
    arg_rem(NULL, "are powers of two)"),
    numsteps,
    algorithmname,
#if defined (WITH_OPENCV) && defined(WITH_CGAL)
    arg_rem(NULL, "(lucaskanadeopencv, proesmans)"),
#else
    arg_rem(NULL, "(proesmans)"),
#endif
    outfileprefix,
    end
  };
  
  if(arg_nullcheck(argtable) != 0)
  {
    printf("insufficient memory\n");
    success = false;
    goto exit;
  }
  
  num_errors = arg_parse(argc, argv, argtable);
  if(num_errors == 0)
  {
    result.I1       = CImg< unsigned char >(image1filename->filename[0]);
    result.I2       = CImg< unsigned char >(image2filename->filename[0]);
    result.numSteps = numsteps->ival[0];
#if defined (WITH_OPENCV) && defined(WITH_CGAL)
    if(strcmp(algorithmname->sval[0], "lucaskanadeopencv") == 0)
      result.algorithmType = LKOPENCV;
    else
#endif
    if(strcmp(algorithmname->sval[0], "proesmans") == 0)
      result.algorithmType = PROESMANS;
    else
    {
      printf("invalid motion extraction algorithm\n");
      success = false;
      goto exit;
    }
    result.outFilePrefix = outfileprefix->sval[0];
    
    success = true;
  }
  else
  {
    printf("Usage: morph");
    arg_print_syntax(stdout, argtable, "\n");
    printf("This program demonstrates the use of the morphing functionality implemented in the OptFlow library.\n");
    arg_print_glossary(stdout, argtable, "  %-30s %s\n");
    
    success = false;
  }
  
  exit:
  arg_freetable(argtable, sizeof(argtable) / sizeof(argtable[0]));
  return success;
}

static void saveMorphImage(const CImg< unsigned char > &M, int i,
                           const string &outFilePrefix)
{
  ostringstream ostr;
  ostr<<outFilePrefix + "-morph-"<<setfill('0')<<setw(2)<<i<<".png";
  M.save_png(ostr.str().c_str());
}

static void saveMotionImages(const CImg< unsigned char > &motionImage1,
                             const CImg< unsigned char > &motionImage2,
                             const string &outFilePrefix)
{
  motionImage1.save_png((outFilePrefix + "-motion-1.png").c_str());
  motionImage2.save_png((outFilePrefix + "-motion-2.png").c_str());
}

int main(int argc, char **argv)
{
  ArgData argData;
  if(!parseArgs(argc, argv, argData))
    return EXIT_SUCCESS;
  
  const int W = argData.I1.dimx();
  const int H = argData.I1.dimy();
  
  CImg< unsigned char > I1_smoothed, I2_smoothed;
  
  argData.I1 = argData.I1.get_channel(0);
  I1_smoothed = argData.I1.get_blur(3.0, 3.0, 3.0);
  argData.I2 = argData.I2.get_channel(0);
  I2_smoothed = argData.I2.get_blur(3.0, 3.0, 3.0);
  
  CImg< unsigned char > motionImage1(W, H, 1, 3);
  motionImage1.fill(0);
  CImg< unsigned char > motionImage2(W, H, 1, 3);
  motionImage2.fill(0);

#if defined (WITH_OPENCV) && defined(WITH_CGAL)
  if(argData.algorithmType == LKOPENCV)
  {
    SparseVectorField V1, V2;
    CImg< unsigned char > M;
    LucasKanadeOpenCV motionExtractor;
    SparseImageMorpher morpher;
    ostringstream ostr;
    
    motionExtractor.compute(I1_smoothed, I2_smoothed, V1);
    V1.triangulate();
    motionExtractor.compute(I2_smoothed, I1_smoothed, V2);
    V2.triangulate();
    
    VectorFieldIllustrator::renderSparseVectorField(V1, motionImage1);
    VectorFieldIllustrator::renderSparseVectorField(V2, motionImage2);
    saveMotionImages(motionImage1, motionImage2, argData.outFilePrefix);
    
    double dt = 1.0 / (argData.numSteps - 1);
    int i = 1;
    for(double t = 0; t <= 1.0; t += dt)
    {
      morpher.morph(argData.I1, argData.I2, V1, V2, t, M);
      saveMorphImage(M, i, argData.outFilePrefix);
      
      i++;
    }
  }
  else
  {
#endif
    CImg< double > V1, V2;
    CImg< unsigned char > M;
    PyramidalProesmans motionExtractor;
    DenseImageMorpher morpher;
    ostringstream ostr;
    
    motionExtractor.compute(I1_smoothed, I2_smoothed, V1, V2);
    
    VectorFieldIllustrator::renderDenseVectorField(V1, motionImage1, 15);
    VectorFieldIllustrator::renderDenseVectorField(V2, motionImage2, 15);
    saveMotionImages(motionImage1, motionImage2, argData.outFilePrefix);
    
    double dt = 1.0 / (argData.numSteps - 1);
    int i = 1;
    for(double t = 0; t <= 1.0; t += dt)
    {
      morpher.morph(argData.I1, argData.I2, V2, V1, t, M);
      saveMorphImage(M, i, argData.outFilePrefix);
      
      i++;
    }
#if defined (WITH_OPENCV) && defined(WITH_CGAL)
  }
#endif
  
  return EXIT_SUCCESS;
}*/

static void saveMorphImage(const CImg< unsigned int > &M, int i,
                           const string &outFilePrefix)
{
  ostringstream ostr;
  ostr<<outFilePrefix + "-morph-"<<setfill('0')<<setw(2)<<i<<".png";
  M.save_png(ostr.str().c_str());
}

static void saveMotionImages(const CImg< unsigned int > &motionImage1,
                             const CImg< unsigned int > &motionImage2,
                             const string &outFilePrefix)
{
  motionImage1.save_png((outFilePrefix + "-motion-1.png").c_str());
  motionImage2.save_png((outFilePrefix + "-motion-2.png").c_str());
}

int main(int argc, char **argv)
{
  options_description generalArgs("General options");
  generalArgs.add_options()
    ("help", "print usage")
    ("version", "print version number");
  
  options_description reqArgs("Required arguments");
  reqArgs.add_options()
    ("image1", value< std::string >(), "first source image for vector field")
    ("image2", value< std::string >(), "second source image for vector field")
    ("numtimesteps", value< int >(), "number of intermediate images")
    ("algorithm", value< std::string >(), "motion extraction algorithm to use (opencv, proesmans)")
    ("outprefix", value< std::string >(), "output file prefix");
  
  options_description allArgs("Usage: morph <required arguments>");
  allArgs.add(generalArgs).add(reqArgs);
  
  try {
    variables_map vm;
    store(parse_command_line(argc, argv, allArgs), vm);
    notify(vm);
    
    if(vm.size() == 0 || vm.count("help"))
    {
      std::cout<<allArgs<<std::endl;
      return EXIT_SUCCESS;
    }
    else if(vm.count("version"))
      std::cout<<OPTFLOW_VERSION_INFO<<std::endl;
    else if(!vm.count("image1") || !vm.count("image2") || !vm.count("numtimesteps") || 
            !vm.count("algorithm") || !vm.count("outprefix"))
    {
      std::cout<<"One or more required arguments missing."<<std::endl;
      std::cout<<reqArgs<<std::endl;
    }
    
    std::string image1FileName = vm["image1"].as< std::string >();
    std::string image2FileName = vm["image2"].as< std::string >();
    int numTimeSteps           = vm["numtimesteps"].as< int >();
    std::string algorithmName  = vm["algorithm"].as< std::string >();
    std::string outFilePrefix  = vm["outprefix"].as< std::string >();
    
    CImg< unsigned int > I1(image1FileName.c_str());
    CImg< unsigned int > I2(image2FileName.c_str());
    
    CImg< unsigned int > I1_smoothed, I2_smoothed;
  
    I1 = I1.get_channel(0);
    I1_smoothed = I1.get_blur(3.0, 3.0, 3.0);
    I2 = I2.get_channel(0);
    I2_smoothed = I2.get_blur(3.0, 3.0, 3.0);

    
    const int W = I1.dimx();
    const int H = I1.dimy();
    
    CImg< unsigned int > motionImage1(W, H, 1, 3);
    motionImage1.fill(0);
    CImg< unsigned int > motionImage2(W, H, 1, 3);
    motionImage2.fill(0);
    
#if defined (WITH_OPENCV) && defined(WITH_CGAL)
    if(algorithmName == "opencv")
    {
      SparseVectorField V1, V2;
      CImg< unsigned int > M;
      LucasKanadeOpenCV motionExtractor;
      SparseImageMorpher morpher;
      ostringstream ostr;
    
      motionExtractor.compute(I1_smoothed, I2_smoothed, V1);
      V1.triangulate();
      motionExtractor.compute(I2_smoothed, I1_smoothed, V2);
      V2.triangulate();
    
      VectorFieldIllustrator::renderSparseVectorField(V1, motionImage1);
      VectorFieldIllustrator::renderSparseVectorField(V2, motionImage2);
      saveMotionImages(motionImage1, motionImage2, outFilePrefix);
    
      double dt = 1.0 / (numTimeSteps - 1);
      int i = 1;
      for(double t = 0; t <= 1.0; t += dt)
      {
        morpher.morph(I1, I2, V1, V2, t, M);
        saveMorphImage(M, i, outFilePrefix);
      
        i++;
      }
    }
    else
#endif
    if(algorithmName == "proesmans")
    {
      CImg< double > V1, V2,V3;
      CImg< unsigned int > M;
      PyramidalProesmans motionExtractor;
      DenseImageMorpher morpher;
      ostringstream ostr;
    
      motionExtractor.compute(I1_smoothed, I2_smoothed, V1, V2);
    
      VectorFieldIllustrator::renderDenseVectorField(V1, motionImage1, 15);
      VectorFieldIllustrator::renderDenseVectorField(V2, motionImage2, 15);
      saveMotionImages(motionImage1, motionImage2, outFilePrefix);
    
      //SparseVectorFieldIO test;
      //test.writeVectorField(V1, "test.pvdm");
    
      DenseVectorFieldIO::writeVectorField(V1,outFilePrefix + "-motion1.pdvm");
      DenseVectorFieldIO::writeVectorField(V2,outFilePrefix + "-motion2.pdvm");


     /* double dt = 1.0 / (numTimeSteps - 1);
      int i = 1;
      for(double t = 0; t <= 1.0; t += dt)
      {
        morpher.morph(I1, I2, V2, V1, t, M);
        saveMorphImage(M, i, outFilePrefix);
      
        i++;
      } */
    }
    else
    {
      std::cout<<"Invalid algorithm name."<<std::endl;
      return EXIT_SUCCESS;
    }
  }
  catch(CImgIOException &e1) {
    std::cout<<"Invalid source image(s)."<<std::endl;
  }
  catch(std::exception &e2) {
    std::cout<<allArgs<<std::endl;
  }
  
  return EXIT_SUCCESS;
}
