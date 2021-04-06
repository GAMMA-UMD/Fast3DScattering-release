cmake_minimum_required(VERSION 3.10)
project( mesh_processing )

# Set a default build type if none was specified
if( NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES )
    message( STATUS "Setting build type to 'debug' as none was specified." )
    set( CMAKE_BUILD_TYPE debug CACHE STRING "Choose the type of build." FORCE )
    # Set the possible values of build type for cmake-gui
    set_property( CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "debug" "release" )
endif()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wno-narrowing -Wno-deprecated")

message(STATUS "VCGLIB ROOT: ${VCGLIB_ROOT}")

# Add include directories
include_directories(${VCGLIB_ROOT}/eigenlib
        ${VCGLIB_ROOT}
        )

add_executable( trimesh_clustering trimesh_clustering.cpp ${VCGLIB_ROOT}/wrap/ply/plylib.cpp )
add_executable( random_rotation random_rotation.cpp ${VCGLIB_ROOT}/wrap/ply/plylib.cpp )
add_executable( scale_rot_clustering scale_rot_clustering.cpp ${VCGLIB_ROOT}/wrap/ply/plylib.cpp )
add_executable( farthest_sampling farthest_sampling.cpp ${VCGLIB_ROOT}/wrap/ply/plylib.cpp )

