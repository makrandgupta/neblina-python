#!/usr/bin/env python
# Neblina unit testing framework
# (C) 2015 Motsai Research Inc.

import unittest

from integration import apiIntegrationTest

def getSuite():
    suite = unittest.TestSuite()
    suite.addTest(apiIntegrationTest.getSuite())
    return suite


