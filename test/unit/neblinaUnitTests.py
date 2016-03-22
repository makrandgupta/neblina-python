#!/usr/bin/env python
# Neblina unit testing framework
# (C) 2015 Motsai Research Inc.

import unittest

from unit import packetsUnitTest

def getSuite():  
    suite = unittest.TestSuite()
    suite.addTest( packetsUnitTest.getSuite() )    
    return suite
  
        
