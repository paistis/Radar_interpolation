
#ifdef WITH_CGAL

#include "SparseVectorField.h"

#include <CGAL/Delaunay_triangulation_2.h>
#include <CGAL/Simple_cartesian.h>
#include <iomanip>
#include <stdexcept>

typedef CGAL::Simple_cartesian< double > K;
typedef CGAL::Delaunay_triangulation_2< K > Delaunay;

SparseVectorField::SparseVectorField() : triangulationValid_(false) { }

void SparseVectorField::addVector(const Point &ip)
{
  initialPoints_.push_back(Point(ip.x(), ip.y()));
  terminalPoints_.push_back(Point(ip.x(), ip.y()));
  triangulationValid_ = false;
}

void SparseVectorField::addVector(const Point &ip, const Point &tp)
{
  initialPoints_.push_back(Point(ip.x(), ip.y()));
  terminalPoints_.push_back(Point(tp.x(), tp.y()));
  triangulationValid_ = false;
}

void SparseVectorField::clear()
{
  initialPoints_.clear();
  terminalPoints_.clear();
  triIndices_.clear();
  triangulationValid_ = false;
}

const Point &SparseVectorField::getInitialPoint(int i) const
{
  return initialPoints_[i];
}

const vector< Point > &SparseVectorField::getInitialPoints() const
{
  return initialPoints_;
}

const vector< Point > &SparseVectorField::getTerminalPoints() const
{
  return terminalPoints_;
}

const Point &SparseVectorField::getTerminalPoint(int i) const
{
  return terminalPoints_[i];
}

int SparseVectorField::getNumVectors() const
{
  return initialPoints_.size();
}

const list< int > &SparseVectorField::getTriIndices() const
{
  if(triangulationValid_)
    return triIndices_;
  else
    throw logic_error("No valid triangulation");
}

void SparseVectorField::setInitialPoint(int i, int x, int y)
{
  initialPoints_[i] = Point(x, y);
}

void SparseVectorField::setTerminalPoint(int i, double x, double y)
{
  terminalPoints_[i] = Point(x, y);
}

void SparseVectorField::triangulate()
{
  Delaunay dt;
  Delaunay::Finite_edges_iterator eIter;
  Delaunay::Finite_faces_iterator fIter;
  vector< Point >::const_iterator fpIter;
  int i;
  map< Delaunay::Vertex_handle, int > V;
  map< Point, int > Vi;
  Delaunay::Finite_vertices_iterator vIter;
  
  dt.insert(initialPoints_.begin(), initialPoints_.end());
  
  // Map each vertex to its index.
  for(int i = 0; i < initialPoints_.size(); i++)
    Vi[initialPoints_[i]] = i;
  
  // Map vertices in the Delaunay triangulation to the original vertices.
  for(vIter = dt.finite_vertices_begin(); vIter != dt.finite_vertices_end(); vIter++)
    V[vIter] = Vi[Point(vIter->point().x(), vIter->point().y())];
  
  // Retrieve vertex indices from the vertex map.
  for(fIter = dt.finite_faces_begin(); fIter != dt.finite_faces_end(); fIter++)
  {
    Delaunay::Face f = *fIter;
    
    triIndices_.push_back(V[f.vertex(0)]);
    triIndices_.push_back(V[f.vertex(1)]);
    triIndices_.push_back(V[f.vertex(2)]);
  }
  
  triangulationValid_ = true;
}

ostream &operator<<(ostream &os, const SparseVectorField &V)
{
  Point p1;
  Point p2;
  double u, v;
  
  for(int i = 0; i < V.getNumVectors(); i++)
  {
    p1 = V.getInitialPoint(i);
    p2 = V.getTerminalPoint(i);
    u = p2.x() - p1.x();
    v = p2.y() - p1.y();
    os<<"Vector "<<i+1<<": ";
    os<<"x: "<<setw(8)<<setprecision(3)<<left<<p1.x();
    os<<" y: "<<setw(8)<<setprecision(3)<<left<<p1.y();
    os<<" u: "<<setw(8)<<setprecision(3)<<left<<u;
    os<<" v: "<<setw(8)<<setprecision(3)<<left<<v<<endl;
  }
  
  return os;
}

#endif
