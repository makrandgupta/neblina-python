import os
import binascii
import slip
import neblina as neb
import neblinaAPI as nebapi
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--type', '-t')
