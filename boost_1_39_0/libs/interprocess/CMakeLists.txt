#----------------------------------------------------------------------------
# This file was automatically generated from the original CMakeLists.txt file
# Add a variable to hold the headers for the library
set (lib_headers
    interprocess
)

# Add a library target to the build system
boost_library_project(
  interprocess
  #  SRCDIRS 
  TESTDIRS  test
  HEADERS ${lib_headers}
  #  DOCDIRS 
  DESCRIPTION  "Shared memory, memory mapped files, process-shared mutexes, condition variables, containers and allocators."
  MODULARIZED
  AUTHORS  "Ion Gaztanaga <igaztanaga -at- gmail.com>"
  #  MAINTAINERS 
)


