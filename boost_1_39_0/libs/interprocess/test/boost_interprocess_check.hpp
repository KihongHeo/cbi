//////////////////////////////////////////////////////////////////////////////
//
// (C) Copyright Ion Gaztanaga 2004-2007. Distributed under the Boost
// Software License, Version 1.0. (See accompanying file
// LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//
// See http://www.boost.org/libs/interprocess for documentation.
//
//////////////////////////////////////////////////////////////////////////////

#ifndef BOOST_INTERPROCESS_TEST_HEADER
#define BOOST_INTERPROCESS_TEST_HEADER

#include <boost/interprocess/detail/config_begin.hpp>
#include <boost/interprocess/exceptions.hpp>
#include <iostream>

namespace boost { namespace interprocess { namespace test {

#define BOOST_INTERPROCES_CHECK( P )  \
   if(!(P)) do{  std::cout << "Failed: " << #P << " file: " << __FILE__ << " line : " << __LINE__ << std::endl; throw boost::interprocess::interprocess_exception();}while(0)

}}}   //namespace boost { namespace interprocess { namespace test {

#include <boost/interprocess/detail/config_end.hpp>

#endif   //BOOST_INTERPROCESS_TEST_HEADER
