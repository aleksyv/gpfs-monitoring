#!/usr/bin/python

################################################################################
# Name:    Check IBM Spectrum Scale / GPFS monitoring events for any string
# Dependencies:   - IBM Spectrum Scale
################################################################################

import os
import subprocess
import sys
import string
import argparse


################################################################################
# # Variable definition for Nagios
################################################################################
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3


def checkRequirments():
    """
    Check if IBM Spectrum Scale
    """
    if not (os.path.isdir("/usr/lpp/mmfs/bin/") and os.path.isfile("/usr/lpp/mmfs/bin/mmgetstate") ):
        print(str(STATE_CRITICAL) + "CRITICAL - No IBM Spectrum Scale Installation detected." )

def checkStatusNode(args):
    fdout = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmhealth node eventlog --" +args.time+ " -N " + args.node + " -Y")
    if str(args.string) in fdout:
        print( "CRITICAL;"+ str(args.node)+str(args.string))
        sys.exit(STATE_CRITICAL)
    else:
        print("OK;"+ str(args.node))
        sys.exit(STATE_OK)

def checkStatusAll(args):
    healthStatus=0
    output = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmhealth cluster show node -Y")
    list = []
    if output:
        for liner in output.splitlines()[1:]:
            if "mmhealth" in liner:
                if liner.split(':')[7] == 'NODE':
                    list.append(liner.split(':')[6])
        for fsNode in list:
            fdout = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmhealth node eventlog --" +args.time+ " -N " + fsNode + " -Y")
            if str(args.string) in fdout:
                print("CRITICAL;"+ str(fsNode)+ ";"+ str(args.string))
                healthStatus=2
            else:
                print("OK;"+ str(fsNode))
        sys.exit(healthStatus)
    else:
        print (str(STATE_UNKNOWN)+";Get logs information failed")
        sys.exit(STATE_UNKNOWN)

def executeBashCommand(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0]


def argumentParser():
    """
    Parse the arguments from the command line
    """
    parser = argparse.ArgumentParser(description='Check logs for string ')
    group = parser.add_argument_group();
    subParser = parser.add_subparsers()
    nodeParser = subParser.add_parser('node', help='Check Node logs for string')
    nodeParser.set_defaults(func=checkStatusNode)
    nodeParser.add_argument('-n', '--node', dest='node', action='store', help='Node to test NSD', required=True)
    nodeParser.add_argument('-t', '--time', dest='time', action='store', help='Review period, can be [hour day week month]', required=True)
    nodeParser.add_argument('-s', '--string', dest='string', action='store', help='String for search', required=True)

    allnodeParser = subParser.add_parser('all', help='Check All node logs for string')
    allnodeParser.set_defaults(func=checkStatusAll)
    allnodeParser.add_argument('-t', '--time', dest='time', action='store', help='Review period, can be [hour day week month]', required=True)
    allnodeParser.add_argument('-s', '--string', dest='string', action='store', help='String for search', required=True)
    return parser


if __name__ == '__main__':
    checkRequirments()
    parser = argumentParser()
    args = parser.parse_args()
    args.func(args)