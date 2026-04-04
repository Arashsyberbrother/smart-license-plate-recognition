cmake_minimum_required(VERSION 3.14)
project(plate_reader_app LANGUAGES CXX)

set(BINARY_NAME "plate_reader_app")

cmake_policy(SET CMP0063 NEW)

set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}/run" CACHE PATH "Installation directory")
set(CMAKE_VERBOSE_MAKEFILE ON)

find_package(Flutter REQUIRED)

add_subdirectory(${FLUTTER_MANAGED_DIR} managed_flutter)
add_subdirectory(flutter flutter_managed)
add_subdirectory(runner)

# Generated plugin build rules, which manage building the plugins and adding them
# to the application.
include(flutter/generated_plugins.cmake)

# === Installation ===
# Support files are copied into place next to the executable, so that it can
# run in place. This is done instead of making a separate bundle (as on Linux)
# so that building and running from within Visual Studio will work.
set(BUILD_BUNDLE_DIR "$<TARGET_FILE_DIR:${BINARY_NAME}>")
# Make the "install" step default, as it's required to run.
set(CMAKE_VS_INCLUDE_INSTALL_TO_DEFAULT_BUILD 1)
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set(CMAKE_INSTALL_PREFIX "${BUILD_BUNDLE_DIR}" CACHE PATH "..." FORCE)
endif()

set(INSTALL_BUNDLE_DATA_DIR "${CMAKE_INSTALL_PREFIX}/data")
set(INSTALL_BUNDLE_LIB_DIR "${CMAKE_INSTALL_PREFIX}")

install(TARGETS ${BINARY_NAME} RUNTIME DESTINATION "${CMAKE_INSTALL_PREFIX}"
    COMPONENT Runtime)
install(FILES "${FLUTTER_ICU_DATA_FILE}" DESTINATION "${INSTALL_BUNDLE_DATA_DIR}"
    COMPONENT Runtime)
install(FILES "${FLUTTER_LIBRARY}" DESTINATION "${INSTALL_BUNDLE_LIB_DIR}"
    COMPONENT Runtime)
if(PLUGIN_BUNDLED_LIBRARIES)
  install(FILES "${PLUGIN_BUNDLED_LIBRARIES}"
    DESTINATION "${INSTALL_BUNDLE_LIB_DIR}"
    COMPONENT Runtime)
endif()
install(CODE
  "file(REMOVE_RECURSE \"${INSTALL_BUNDLE_DATA_DIR}/flutter_assets\")"
  COMPONENT Runtime)
install(CODE
  "execute_process(
    COMMAND \"${CMAKE_COMMAND}\" -E copy_directory
      \"${PROJECT_BUILD_DIR}/flutter_assets\"
      \"${INSTALL_BUNDLE_DATA_DIR}/flutter_assets\"
    COMMAND_ERROR_IS_FATAL ANY
  )"
  COMPONENT Runtime)
install(CODE
  "execute_process(
    COMMAND \"${CMAKE_COMMAND}\" -E copy_directory
      \"${FLUTTER_ASSET_DIR}\"
      \"${INSTALL_BUNDLE_DATA_DIR}/flutter_assets\"
    COMMAND_ERROR_IS_FATAL ANY
  )"
  COMPONENT Runtime)
