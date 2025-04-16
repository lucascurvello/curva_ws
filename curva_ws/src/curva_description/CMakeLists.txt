cmake_minimum_required(VERSION 3.8)
project(curva_description)


find_package(ament_cmake REQUIRED)
find_package(xacro REQUIRED)

# Install all necessary directories
install(
  DIRECTORY urdf rviz launch sdf config world
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
