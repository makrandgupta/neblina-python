#!/usr/bin/env python
###################################################################################
#
# Copyright (c)     2010-2016   Motsai
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
###################################################################################

import getopt
import sys
import unittest
import logging
import time

from test.unit import neblinaUnitTests
from test.integration import neblinaIntegrationTests

###################################################################################


def printArguments():
    print("Neblina test platform v1.0.0")
    print("Copyright Motsai 2010-2016")
    print("")
    print("Neblina commands:")
    print("    -h --help : Display available commands.")
    print("    -p --port : COM port to use.")
    print("")
    print("Neblina test commands (if none specify, run all test):")
    print("    -i : Run integration test.")
    print("    -u : Run unit test.")

###################################################################################


def testUnit():
    print( "--------------------------------------" )
    print( "Executing all unit tests." )
    print( "--------------------------------------" )
    time.sleep(0.1)         # Prevent previous print to overlap test
    suite = unittest.TestSuite()
    suite.addTest( neblinaUnitTests.getSuite() )
    unittest.TextTestRunner( verbosity = 2 ).run( suite )

###################################################################################


def testIntegration(port):
    print( "--------------------------------------" )
    if port == None:
        print("Unable to run integration test.")
        print("Please specify the PORT using -p command.")
        sys.exit()
    print( "Executing all integration tests." )
    print( "--------------------------------------" )
    time.sleep(0.1)         # Prevent previous print to overlap test
    suite = unittest.TestSuite()
    suite.addTest( neblinaIntegrationTests.getSuite(port) )
    unittest.TextTestRunner( verbosity = 2 ).run( suite )

###################################################################################


def main( argv ):
    port = None
    runAll = True
    runUnit = False
    runIntegration = False

    # Retrieve commands and arguments
    try:
        opts, args = getopt.getopt( argv, "hp:iu")
    except getopt.GetoptError:
        printArguments()
        sys.exit()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printArguments()
            sys.exit()
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-i"):
            runAll = False
            runIntegration = True
        elif opt in ("-u"):
            runAll = False
            runUnit = True

    # Run test
    if runUnit or runAll:
        testUnit()

    if runIntegration or runAll:
        testIntegration(port)

###################################################################################


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN, format='%(message)s')
    main( sys.argv[1:])
