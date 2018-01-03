#!/usr/bin/python

################################################################################
# Name:    Check IBM Spectrum Scale / GPFS FS mounted on nodes
# Dependencies:   - IBM Spectrum Scale
################################################################################

import os
import subprocess
import sys
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
    if not (os.path.isdir("/usr/lpp/mmfs/bin/") and os.path.isfile("/usr/lpp/mmfs/bin/mmlsfs") ):
        print(str(STATE_CRITICAL) + "CRITICAL - No IBM Spectrum Scale Installation detected." )


def checkStatusAll(args):
    output = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmlsfs all -Y")
    list = []
    if output:
        for liner in output.splitlines()[1:]:
            if liner.split(':')[7] == 'inodeSize':
               list.append(liner.split(':')[6])
        for fsDevice in list:
            outputS=str(fsDevice)
            fdout = executeBashCommand("/usr/lpp/mmfs/bin/mmlsmount " + fsDevice + " -Y")
            for lines in fdout.splitlines()[1:]:
                outputS=outputS + ";" + lines.split(':')[11]
            print(outputS)
    else:
        print ("3;Get Filesystem information failed")
        sys.exit(STATE_CRITICAL)


def checkStatusDevice(args):
    outputS=args.device
    fdout = executeBashCommand("/usr/lpp/mmfs/bin/mmlsmount " + args.device + " -Y")
    if fdout:
        for lines in fdout.splitlines()[1:]:
            outputS=outputS + ";" + lines.split(':')[11]
        print(outputS)
    else:
        print ("3;Get Filesystem information failed")
        sys.exit(STATE_CRITICAL)


def checkStatusMount(args):
    for i in args.mounts.split(','):
        fdout = executeBashCommand("/usr/lpp/mmfs/bin/mmlsmount " + i + " -L")
        if fdout and (args.device in fdout):
            print ("OK - " + i)
        elif not fdout:
            print ("WARNING - " + i + " no such filesystem" )
        else:
            print ("WARNING - " + i + " not mounted on " +args.device )

def executeBashCommand(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0]

def argumentParser():
    parser = argparse.ArgumentParser(description='Check GPFS FS mounted on nodes')
    group = parser.add_argument_group();

    subParser = parser.add_subparsers()

    nodeParser = subParser.add_parser('device', help='Check device mounts')
    nodeParser.set_defaults(func=checkStatusDevice)
    nodeParser.add_argument('-d', '--device', dest='device', action='store', help='Device to get mounts', required=True)

    allnodeParser = subParser.add_parser('all', help='Check All Device mounts')
    allnodeParser.set_defaults(func=checkStatusAll)

    mountParser = subParser.add_parser('mounts', help='Check mounts per device')
    mountParser.set_defaults(func=checkStatusMount)
    mountParser.add_argument('-d', '--device', dest='device', action='store', help='Device to get mounts', required=True)
    mountParser.add_argument('-m', '--mounts', dest='mounts', action='store', help='Mountes to check, separated by comma', required=True)

    return parser

if __name__ == '__main__':
    parser = argumentParser()
    args = parser.parse_args()
    args.func(args)