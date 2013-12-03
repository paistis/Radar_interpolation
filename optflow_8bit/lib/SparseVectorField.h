
#ifdef WITH_CGAL
#ifndef SPARSEVECTORFIELD_H

#include <CGAL/Simple_cartesian.h>
#include <list>
#include <ostream>
#include <vector>

typedef CGAL::Simple_cartesian< double >::Point_2 Point;

using namespace std;

/// Defines a sparse vector field, i.e. a list of vectors.
class SparseVectorField
{
public:
  /// Default constructor.
  SparseVectorField();
  
  /// Adds a zero vector at the given point.
  /**
   * This method adds a zero vector at the given point. 
   * Adding a vector breaks an existing triangulation.
   */
  void addVector(const Point &ip);
  
  /// Adds a vector with the given start and end points.
  /**
   * This method adds a vector with the given start and end points. 
   * Adding a vector breaks an existing triangulation.
   */
  void addVector(const Point &ip, const Point &tp);
  
  /// Removes all vectors in this vector field.
  void clear();
  
  /// Returns the initial point of the ith vector in this vector field.
  const Point &getInitialPoint(int i) const;
  
  /// Returns the initial points of the vectors in this vector field.
  const vector< Point > &getInitialPoints() const;
  
  /// Returns the number of vectors in this vector field.
  int getNumVectors() const;
  
  /// Returns the terminal point of the ith vector in this vector field.
  const Point &getTerminalPoint(int i) const;
  
  /// Returns the terminal points of the vectors in this vector field.
  const vector< Point > &getTerminalPoints() const;
  
  /// Returns the indices of the triangulation (if valid)
  /**
   * If this vector field has a valid triangulation, this method 
   * returns its indices. Otherwise, an exception is thrown.
   */
  const list< int > &getTriIndices() const;
  
  /// Sets the initial point of the ith vector.
  void setInitialPoint(int i, int x, int y);
  
  /// Sets the terminal point of the ith vector.
  void setTerminalPoint(int i, double x, double y);
  
  /// Triangulates the set of vector starting points.
  /**
   * This method triangulates the set of vector starting points 
   * and stores the indices of each triangle vertex.
   */
  void triangulate();
  
  friend ostream &operator<<(ostream &os, const SparseVectorField &V);
private:
  vector< Point > initialPoints_;
  bool triangulationValid_;
  vector< Point > terminalPoints_;
  list< int > triIndices_;
};

#define SPARSEVECTORFIELD_H

#endif
#endif
