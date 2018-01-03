#!/usr/bin/python

################################################################################
# Name:    Check IBM Spectrum Scale / GPFS replications status
# Dependencies:  - IBM Spectrum Scale GPFS replication test
################################################################################

import os
import subprocess
import sys
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
    Check if IBM Spectrum Scale installed
    """
    if not (os.path.isdir("/usr/lpp/mmfs/bin/") and os.path.isfile("/usr/lpp/mmfs/bin/mmgetstate") ):
        print(str(STATE_CRITICAL) + "CRITICAL - No IBM Spectrum Scale Installation detected." )


def checkReplicationStatus(args):
    output = executeBashCommand("/usr/lpp/mmfs/bin/mmlsattr " + args.path + "/replication_testfile")
    if output:
        if "miss" in output:
            print("CRITICAL - replication failed on test file")
            command = executeBashCommand("rm -rf " + args.path + "/replication_testfile")
            sys.exit(STATE_CRITICAL)
        elif "No such file or directory" in output:
            print("WARNING - Permission denied or wrong path")
            sys.exit(STATE_WARNING)
        else:
            print("OK")
            command = executeBashCommand("rm -rf " + args.path + "/replication_testfile")
            sys.exit(STATE_OK)
    else:
        print ("STATE_UNKNOWN"+"|Get Filesystem information failed")
        command = executeBashCommand("rm -rf " + args.path + "/replication_testfile")
        sys.exit(STATE_UNKNOWN)

def executeBashCommand(command):

    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0]

def checkReplication(args):
    command2='dd if=/dev/zero of=' + args.path + '/replication_testfile bs=64k count=1000'
    code2 = subprocess.call(command2.split())
    if code2 == 0:
        checkReplicationStatus(args)
    else:
        print ("WARNING - Permission denied or wrong path")
        sys.exit(STATE_WARNING)

def argumentParser():
    """
    Parse the arguments from the command line
    """
    parser = argparse.ArgumentParser(description='Check status of the gpfs replications')
    group = parser.add_argument_group();
    subParser = parser.add_subparsers()
    replicationParser = subParser.add_parser('replication', help='Check the filesets')
    replicationParser.set_defaults(func=checkReplication)
    replicationParser.add_argument('-p', '--path', dest='path', action='store', help='Path to store test file', required=True)

    return parser


if __name__ == '__main__':
    checkRequirments()
    parser = argumentParser()
    args = parser.parse_args()
    args.func(args)