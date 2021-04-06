/****************************************************************************
* VCGLib                                                            o o     *
* Visual and Computer Graphics Library                            o     o   *
*                                                                _   O  _   *
* Copyright(C) 2004-2016                                           \/)\/    *
* Visual Computing Lab                                            /\/|      *
* ISTI - Italian National Research Council                           |      *
*                                                                    \      *
* All rights reserved.                                                      *
*                                                                           *
* This program is free software; you can redistribute it and/or modify      *
* it under the terms of the GNU General Public License as published by      *
* the Free Software Foundation; either version 2 of the License, or         *
* (at your option) any later version.                                       *
*                                                                           *
* This program is distributed in the hope that it will be useful,           *
* but WITHOUT ANY WARRANTY; without even the implied warranty of            *
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             *
* GNU General Public License (http://www.gnu.org/licenses/gpl.txt)          *
* for more details.                                                         *
*                                                                           *
****************************************************************************/
/*! \file trimesh_clustering.cpp
\ingroup code_sample

\brief a minimal example of a clustering based simplification

*/
#include <time.h>
#include <vcg/complex/complex.h>
#include <vcg/complex/algorithms/clustering.h>

#include <wrap/io_trimesh/import.h>
#include <wrap/io_trimesh/export.h>

float RandomFloat(float a, float b) {
    float random = ((float) rand()) / (float) RAND_MAX;
    float diff = b - a;
    float r = random * diff;
    return a + r;
}

const float pi = 3.14159265358979323846;
 
class MyFace;
class MyVertex;

struct MyUsedTypes : public vcg::UsedTypes<	vcg::Use<MyVertex>::AsVertexType,    vcg::Use<MyFace>::AsFaceType>{};

class MyVertex  : public vcg::Vertex< MyUsedTypes, vcg::vertex::Coord3f, vcg::vertex::Normal3f, vcg::vertex::BitFlags, vcg::vertex::Color4b >{};
class MyFace    : public vcg::Face < MyUsedTypes, vcg::face::VertexRef, vcg::face::Normal3f, vcg::face::BitFlags > {};
class MyMesh    : public vcg::tri::TriMesh< std::vector<MyVertex>, std::vector<MyFace> > {};

int  main(int argc, char **argv)
{
  if(argc<3)
  {
    printf(
          "Usage: trimesh_clustering filein.ply fileout.ply [opt] \n"
          "options: \n"
          "-r randseed     random seed for rotation\n"
          );
    exit(0);
  }

  int rand_seed = 0;
  srand(time(0));   // randomize with time if a seed is not given

  int i=3;
  while(i<argc)
  {
    if(argv[i][0]!='-')
    { printf("Error unable to parse option '%s'\n",argv[i]); exit(0); }
    switch(argv[i][1])
    {
    case 'r' :	rand_seed=atoi(argv[i+1]); ++i; printf("Using random seed %i\n",rand_seed); srand(rand_seed); break;

    default : {printf("Error unable to parse option '%s'\n",argv[i]); exit(0);}
    }
    ++i;
  }

  int mask = 0;

  MyMesh m;
  if(vcg::tri::io::Importer<MyMesh>::Open(m,argv[1],mask)!=0)
  {
    printf("Error reading file  %s\n",argv[1]);
    exit(0);
  }

  mask = 0;
  mask |= vcg::tri::io::Mask::IOM_FACEINDEX;

  vcg::tri::UpdateBounding<MyMesh>::Box(m);
  vcg::tri::UpdateNormal<MyMesh>::PerFace(m);
  printf("Input mesh  vn:%i fn:%i\n",m.VN(),m.FN());

  vcg::Matrix44f rotTran;
  vcg::Point3f rot_axis;
  float rot_rad;

  for (int ind = 0; ind < 3; ++ind)
  {
      rot_axis[ind] = RandomFloat(0, 1);
  }
  rot_rad = RandomFloat(0, 2*pi);
  rotTran.SetRotateRad(rot_rad, rot_axis);
  vcg::tri::UpdatePosition<MyMesh>::Matrix(m, rotTran);
  vcg::tri::UpdateBounding<MyMesh>::Box(m);

  printf("rotate %.2f degrees around axis ( %.2f, %.2f, %.2f )\n", rot_rad*180/pi, rot_axis.X(), rot_axis.Y(), rot_axis.Z());

  printf("Output mesh vn:%i fn:%i\n",m.VN(),m.FN());

  vcg::tri::io::Exporter<MyMesh>::Save(m,argv[2],mask);
  return 0;
}
