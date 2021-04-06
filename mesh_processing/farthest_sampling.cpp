//
// Created by Zhenyu Tang on 4/6/20.
//

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
#include <vcg/complex/complex.h>
#include <vcg/complex/allocate.h>
#include <vcg/complex/algorithms/geodesic.h>
#include <wrap/io_trimesh/import.h>
#include <wrap/io_trimesh/export.h>



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
                "Usage: farthest_sampling filein.ply fileout.ply [opt] \n"
                "options: \n"
                "-k pointnum     number of points to be sampled; default 1024\n"
        );
        exit(0);
    }

    int K=1024;

    int i=3;
    while(i<argc)
    {
        if(argv[i][0]!='-')
        { printf("Error unable to parse option '%s'\n",argv[i]); exit(0); }
        switch(argv[i][1])
        {
            case 'k' :	K=atoi(argv[i+1]); ++i; printf("Using %i sampling points\n",K); break;

            default : {printf("Error unable to parse option '%s'\n",argv[i]); exit(0);}
        }
        ++i;
    }

    int mask = 0;
    mask |= vcg::tri::io::Mask::IOM_VERTTEXCOORD;
    mask |= vcg::tri::io::Mask::IOM_EDGEINDEX;

    MyMesh m, resampled;
    if(vcg::tri::io::Importer<MyMesh>::Open(m,argv[1],mask)!=0)
    {
        printf("Error reading file  %s\n",argv[1]);
        exit(0);
    }

//    vcg::tri::UpdateBounding<MyMesh>::Box(m);
//    vcg::tri::UpdateNormal<MyMesh>::PerFace(m);
    printf("Input mesh  vn:%i fn:%i\n",m.VN(),m.FN());

    int N = m.VN();

    // If the sampled cloud has more points than the original coud
    while (K >= N)
    {
//        resampled->points.insert(resampled->points.end(), cur_cloud->points.begin(), cur_cloud->points.end());
//        K -= N;
        printf("attempting to sample more points than original mesh\n");
        return -1;
    }
    if (0 == K) return -1;

    int s0 = rand() % N;
    vcg::tri::EuclideanDistance<MyMesh> df;
    std::vector<float> dist_table(N, std::numeric_limits<float>::max());
    resampled.vert.reserve(K);
    for (int i = 0; i < K; ++i)
    {
        vcg::tri::Allocator<MyMesh>::AddVertex(resampled, m.vert[s0].cP());
        float farthest_dist = 0;
        int farthest_point = -1;
        for (int j = 0; j < N; ++j)
        {
            float new_dist = df(&m.vert[s0], &m.vert[j]);
            dist_table[j] = std::min<float>(dist_table[j], new_dist);
            if (dist_table[j] >= farthest_dist)
            {
                farthest_dist = dist_table[j];
                farthest_point = j;
            }
        }
        s0 = farthest_point;
    }
    printf("Output mesh vn:%i fn:%i\n",resampled.VN(),resampled.FN());

    mask = 0;
    mask |= vcg::tri::io::Mask::IOM_FACEINDEX;
    vcg::tri::io::Exporter<MyMesh>::Save(resampled,argv[2],mask);
    return 0;
}
