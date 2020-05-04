# Darryl Leo, Quinn Coleman
# <Darryl's email here>, qcoleman@calpoly.edu
# Lab 4 - CSC 369 Spring 2020
# covidTracker - Analytical tool for tracking COVID spread in the US

import argparse
from configConverter import *
from htmlGenerator import *


# Function that handles MongoDB auth, given auth file
def handle_auth():
    pass

# Function that takes data from covid tracking API & NY Times Dataset, 
# and puts it in MongoDB collections: covid & states
def fill_mongo_db():
    pass


def main():
    parser = argparse.ArgumentParser(description=
                                     'Analytical tool for tracking COVID spread in the US')
    parser.add_argument('-auth',
                        default='credentials.json', 
                        help='file for MongoDB access (credentials.json is default)')
    parser.add_argument('-config',
                        default='trackerConfig.json',
                        help='file to convey your request (trackerConfig.json is default)')
    args = parser.parse_args()
    auth_file = args.auth
    config_file = args.config



if __name__ == '__main__':
    main()

