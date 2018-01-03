#!/usr/bin/python

################################################################################
# Name:    Check IBM Spectrum Scale / GPFS Node status
################################################################################

import os
import subprocess
import sys
import re
import argparse

################################################################################
# # Variable definition for Nagios/Zabbix
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


def getValueFromList(list, header, row):
    col = list[0].index(header)
    return list[row][col]

def checkStatus(args):

    output = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmgetstate -N " + args.device +" -LY")

    lines = output.split("\n")
    list = []
    for line in lines:
        list.append(line.split(":"))
    state = getValueFromList(list, "state", 1)
    quorumNeeded = getValueFromList(list, "quorum", 1)
    nodeName = getValueFromList(list, "nodeName", 1)
    quorumsUp = getValueFromList(list, "nodesUp", 1)
    totalNodes = getValueFromList(list, "totalNodes", 1)

    if not(state == "active"):
       print("CRITICAL" + " - " + str(nodeName) + " - " + str(state) )
       sys.exit(STATE_CRITICAL)
    else:
        print( "OK - " + str(nodeName) + " - " + str(state) + "; nodesUp=" + str(quorumsUp) + "; quorumNeeded=" + str(quorumNeeded) + "; totalNodes=" +  str(totalNodes) )
        sys.exit(STATE_OK)


def checkStatusAll(args):
    output = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmgetstate -aLY")
    if output:
        outputS=""
        lines = output.split("\n")
        list = []
        for line in lines:
            if 'mmgetstate' in line:
                list.append(line.split(":"))
        for i in range(len(list)):
            if args.exclude:
                if (list[i][2] != 'HEADER') and (str(list[i][6]) not in args.exclude) :
                    outputS = outputS + str(list[i][6]) + ";" + str(list[i][8]) +";"
            else:
                if (list[i][2] != 'HEADER'):
                    outputS = outputS + str(list[i][6]) + ";" + str(list[i][8]) +";"
        print outputS


def executeBashCommand(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0]


def argumentParser():
    parser = argparse.ArgumentParser(description='Check node status')
    group = parser.add_argument_group();

    subParser = parser.add_subparsers()

    nodeParser = subParser.add_parser('device', help='Check node status')
    nodeParser.set_defaults(func=checkStatus)
    nodeParser.add_argument('-d', '--device', dest='device', action='store', help='Device to get inode stats', required=True)

    allnodeParser = subParser.add_parser('all', help='Check All GPFS node status')
    allnodeParser.set_defaults(func=checkStatusAll)
    allnodeParser.add_argument('-e', '--exclude', dest='exclude', action='store', help='Exclude nodes from check, comma separated')
    return parser


if __name__ == '__main__':
    checkRequirments()
    parser = argumentParser()
    args = parser.parse_args()
    args.func(args)