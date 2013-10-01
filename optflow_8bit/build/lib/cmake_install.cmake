# Install script for directory: /home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib

# Set the install prefix
IF(NOT DEFINED CMAKE_INSTALL_PREFIX)
  SET(CMAKE_INSTALL_PREFIX "/usr/local")
ENDIF(NOT DEFINED CMAKE_INSTALL_PREFIX)
STRING(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
IF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  IF(BUILD_TYPE)
    STRING(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  ELSE(BUILD_TYPE)
    SET(CMAKE_INSTALL_CONFIG_NAME "")
  ENDIF(BUILD_TYPE)
  MESSAGE(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
ENDIF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)

# Set the component getting installed.
IF(NOT CMAKE_INSTALL_COMPONENT)
  IF(COMPONENT)
    MESSAGE(STATUS "Install component: \"${COMPONENT}\"")
    SET(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  ELSE(COMPONENT)
    SET(CMAKE_INSTALL_COMPONENT)
  ENDIF(COMPONENT)
ENDIF(NOT CMAKE_INSTALL_COMPONENT)

# Install shared libraries without execute permission?
IF(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  SET(CMAKE_INSTALL_SO_NO_EXE "1")
ENDIF(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  IF(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/liboptflow.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/liboptflow.so")
    FILE(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/liboptflow.so"
         RPATH "")
  ENDIF()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/build/lib/liboptflow.so")
  IF(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/liboptflow.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/liboptflow.so")
    IF(CMAKE_INSTALL_DO_STRIP)
      EXECUTE_PROCESS(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/liboptflow.so")
    ENDIF(CMAKE_INSTALL_DO_STRIP)
  ENDIF()
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/optflow" TYPE FILE FILES
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/DenseImageExtrapolator.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/DenseImageMorpher.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/DenseMotionExtractor.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/DenseVectorFieldIO.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/DualDenseMotionExtractor.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/ForwardDenseImageExtrapolator.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/ImageExtrapolatorDriver.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/ImagePyramid.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/InverseDenseImageExtrapolator.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/LucasKanade.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/LucasKanadeOpenCV.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/LucasKanadeROI.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/MotionExtractorDriver.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/Proesmans.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/PXMFileUtils.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/PyramidalDenseMotionExtractor.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/PyramidalLucasKanade.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/PyramidalProesmans.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/ROI.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/SparseImageExtrapolator.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/SparseImageMorpher.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/SparseMotionExtractor.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/SparseVectorField.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/SparseVectorFieldIO.h"
    "/home/nordlikg/fmi/test_interpolation16-bit/optflow_8bit/lib/VectorFieldIllustrator.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")

