cmake_minimum_required(VERSION 3.16)
project(trident_test_harness C)

add_executable(test_harness test_harness.c)

if(WIN32)
    # No extra link libraries needed; LoadLibrary is in kernel32
elseif(APPLE)
    # dlopen/dlsym are in libdl (implicit on macOS)
else()
    target_link_libraries(test_harness PRIVATE dl)
endif()

set_target_properties(test_harness PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/Release"
)
