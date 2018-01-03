#!/usr/bin/python

################################################################################
# Name:    Check IBM Spectrum Scale / GPFS Cluster status
# Dependencies: - IBM Spectrum Scale
################################################################################

import os
import subprocess
import sys
import re
import argparse

################################################################################
# # Variable definition for Nagios
################################################################################
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

    """
spectrum scale node status from documentation

UNKNOWN - Status of the node or the service hosted on the node is not known.
HEALTHY - The node or the service hosted on the node is working as expected. There are no active error events.
CHECKING - The monitoring of a service or a component hosted on the node is starting at the moment. This state is a transient state and is updated when the startup is completed.
TIPS - There might be an issue with the configuration and tuning of the components. This status is only assigned to a Tip event
DEGRADED - The node or the service hosted on the node is not working as expected. That is, a problem occurred with the component but it did not result in a complete failure.
FAILED - The node or the service hosted on the node failed due to errors or cannot be reached anymore.
DEPEND - The node or the services hosted on the node have failed due to the failure of some components. For example, an NFS or SMB service shows this status if authentication has failed.
    """

def checkRequirments():
    """
    Check if IBM Spectrum Scale
    """
    if not (os.path.isdir("/usr/lpp/mmfs/bin/") and os.path.isfile("/usr/lpp/mmfs/bin/mmgetstate") ):
        print(str(STATE_CRITICAL) + "CRITICAL - No IBM Spectrum Scale Installation detected." )



def checkStatusAll(args):
    output = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmhealth node show -Y -N all")
    criticalFlag=0
    lines = output.split("\n")
    list = []
    for line in lines:
        if ('Event' not in line) and ('mmhealth' in line):
            if args.exclude and (line.split(":")[6] not in args.exclude):
                list.append(line.split(":"))
            elif not args.exclude:
                list.append(line.split(":"))
    list.remove(list[-1])
    list.remove(list[0])
#    print(list)
    if "DEPEND" in [list[i][10] for i in range(len(list))]:
        print("CRITICAL"  + ";DEPEND")
        criticalFlag=2
    elif "FAILED" in [list[i][10] for i in range(len(list))]:
        print("CRITICAL"  + ";FAILED")
        criticalFlag=2
    elif "DEGRADED" in [list[i][10] for i in range(len(list))]:
        print("CRITICAL"  + ";DEGRADED")
        criticalFlag=2
    elif "TIPS" in [list[i][10] for i in range(len(list))]:
        print("WARNING"  + ";TIPS")
        if criticalFlag != 2:
            criticalFlag=1
    elif "CHECKING" in [list[i][10] for i in range(len(list))]:
        print("WARNING"  + ";CHECKING")
        if criticalFlag != 2:
            criticalFlag=1
    elif "UNKNOWN" in [list[i][10] for i in range(len(list))]:
        print("UNKNOWN" + ";UNKNOWN")
        if criticalFlag != 2:
            criticalFlag=3
    else:
        print("OK" )
    sys.exit(criticalFlag)


def checkStatusNode(args):
    output = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmhealth node show -Y -N " + args.node)
    criticalFlag=0
    lines = output.split("\n")
    list = []
    for line in lines:
        if ('Event' not in line) and ('mmhealth' in line) :
            list.append(line.split(":"))
    list.remove(list[-1])
    list.remove(list[0])
    if "DEPEND" in [list[i][10] for i in range(len(list))]:
        print("CRITICAL" + ";DEPEND")
        criticalFlag=2
    elif "FAILED" in [list[i][10] for i in range(len(list))]:
        print("CRITICAL" + ";FAILED")
        criticalFlag=2
    elif "DEGRADED" in [list[i][10] for i in range(len(list))]:
        print("CRITICAL" + ";DEGRADED")
        criticalFlag=2
    elif "TIPS" in [list[i][10] for i in range(len(list))]:
        print("WARNING"  + ";TIPS")
        if criticalFlag != 2:
            criticalFlag=1
    elif "CHECKING" in [list[i][10] for i in range(len(list))]:
        print("WARNING" + ";CHECKING")
        if criticalFlag != 2:
            criticalFlag=1
    elif "UNKNOWN" in [list[i][10] for i in range(len(list))]:
        print("UNKNOWN" + ";UNKNOWN")
        if criticalFlag != 2:
            criticalFlag=3
    else:
        print("OK" )
    sys.exit(criticalFlag)

def executeBashCommand(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0]



def argumentParser():
    parser = argparse.ArgumentParser(description='Check GPFS node status')
    group = parser.add_argument_group();
    subParser = parser.add_subparsers()

    nodeParser = subParser.add_parser('node', help='Check Node status')
    nodeParser.set_defaults(func=checkStatusNode)
    nodeParser.add_argument('-n', '--node', dest='node', action='store', help='Node to get status', required=True)

    allnodeParser = subParser.add_parser('all', help='Check All nodes/Cluster status')
    allnodeParser.add_argument('-e', '--exclude', dest='exclude', action='store', help='Exclude nodes from check, comma separated')
    allnodeParser.set_defaults(func=checkStatusAll)
    return parser


if __name__ == '__main__':
    checkRequirments()
    parser = argumentParser()
    args = parser.parse_args()
    args.func(args)