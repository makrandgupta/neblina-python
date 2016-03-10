# Neblina testing 
# (C) 2010-2016 Motsai Research Inc.

import os

def getDataFilepath( filename ):
    return os.path.join( os.path.dirname( __file__ ), "data/", filename )
