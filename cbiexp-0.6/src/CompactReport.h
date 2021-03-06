#ifndef INCLUDE_CompactReport_h
#define INCLUDE_CompactReport_h

#include <string>
#include "arguments.h"
#include <stdlib.h>
#include <string.h>


namespace CompactReport
{
  extern const argp argp;

  extern std::string suffix;
  extern std::string format(unsigned runId);
}


#endif // !INCLUDE_CompactReport_h
