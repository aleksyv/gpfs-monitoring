#!/usr/bin/python

################################################################################
# Name:    Check IBM Spectrum Scale / GPFS inode stats
# Dependencies:   - IBM Spectrum Scale
################################################################################

import os
import subprocess
import sys
import re
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



def checkStatusAll(args):

    output = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmlsfs all -Y")
    list = []
    criticalFlag=0
    outputS=""
    outputA=""
    if output:
        for liner in output.splitlines()[1:]:
            if liner.split(':')[7] == 'inodeSize':
                if args.exclude:
                    if liner.split(':')[6] not in args.exclude:
                        list.append(liner.split(':')[6])
                else:
                    list.append(liner.split(':')[6])
        for fsDevice in list:
            fdout = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmdf " + fsDevice + " -Y")
            for line in fdout.splitlines()[4:]:
                if line.split(':')[1] == 'inode' and line.split(':')[8] != "allocatedInodes":
                    if 100 * float(line.split(':')[6])/ float(line.split(':')[8]) > float(args.critical):
                        criticalFlag=2
                        print( "CRITICAL - " + fsDevice + "-" '{:.2f}'.format(100* float(line.split(':')[6])/ float(line.split(':')[8])) + "%;" +"; Used=" + line.split(':')[6] + "; Allocated=" + line.split(':')[8] )
                    elif 100 * float(line.split(':')[6])/ float(line.split(':')[8]) > float(args.warning):
                        if criticalFlag != 2:
                            criticalFlag=1
                        print( "WARNING - " + fsDevice + "-" '{:.2f}'.format(100* float(line.split(':')[6])/ float(line.split(':')[8])) + "%;" +"; Used=" + line.split(':')[6] + "; Allocated=" + line.split(':')[8] )
                    else:
                        print( "OK - " + fsDevice + "-" '{:.2f}'.format(100* float(line.split(':')[6])/ float(line.split(':')[8])) + "%;" +"; Used=" + line.split(':')[6] + "; Allocated=" + line.split(':')[8] )
                    outputS = outputS + " " + fsDevice + "=" '{:.2f}'.format(100* float(line.split(':')[6])/ float(line.split(':')[8])) + "%;" + str(args.warning) + ";" + str(args.critical) + ";0;100; "+fsDevice+"_Used=" + line.split(':')[6] + ";;;;; "+fsDevice+"_Allocated=" + line.split(':')[8] + ";;;;;"
        print(outputA)
        print("|" + outputS)
        sys.exit(criticalFlag)

    else:
        print ("3;Get Filesystem information failed")
        sys.exit(3)

def checkStatusDevice(args):
    outputS=""
    criticalFlag=0
    fdout = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmdf " + args.device + " -Y")
    for line in fdout.splitlines()[4:]:
        if line.split(':')[1] == 'inode' and line.split(':')[8] != "allocatedInodes":
            if 100 * float(line.split(':')[6])/ float(line.split(':')[8]) > float(args.critical):
                criticalFlag=2
                print ("CRITICAL - " + args.device + " - " '{:.2f}'.format(100* float(line.split(':')[6])/ float(line.split(':')[8])) + "%;" +"; Used=" + line.split(':')[6] + "; Allocated=" + line.split(':')[8] )
            elif 100 * float(line.split(':')[6])/ float(line.split(':')[8]) > float(args.warning):
                if criticalFlag != 2:
                    criticalFlag=1
                print ("WARNING - " + args.device + " - " '{:.2f}'.format(100* float(line.split(':')[6])/ float(line.split(':')[8])) + "%;" +"; Used=" + line.split(':')[6] + "; Allocated=" + line.split(':')[8] )
            else:
                print ("OK - " + args.device + " - " '{:.2f}'.format(100* float(line.split(':')[6])/ float(line.split(':')[8])) + "%;" +"; Used=" + line.split(':')[6] + "; Allocated=" + line.split(':')[8] )
            outputS = outputS + " " + args.device + "=" '{:.2f}'.format(100* float(line.split(':')[6])/ float(line.split(':')[8])) + "%;" + str(args.warning) + ";" + str(args.critical) + ";0;100; "+ args.device +"_Used=" + line.split(':')[6] + ";;;;; " + args.device + "_Allocated=" + line.split(':')[8] + ";;;;;"
    print("|" + outputS)
    sys.exit(criticalFlag)


def executeBashCommand(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0]

def argumentParser():
    parser = argparse.ArgumentParser(description='Check NSD gpfs status')
    group = parser.add_argument_group();

    subParser = parser.add_subparsers()

    nodeParser = subParser.add_parser('device', help='Check inode status')
    nodeParser.set_defaults(func=checkStatusDevice)
    nodeParser.add_argument('-d', '--device', dest='device', action='store', help='Device to get inode stats', required=True)
    nodeParser.add_argument('-w', '--warning', dest='warning', action='store', help='Warning level of inodes utilization, in percent', default=90)
    nodeParser.add_argument('-c', '--critical', dest='critical', action='store', help='Critical level of inodes utilization, in percent', default=96)

    allnodeParser = subParser.add_parser('all', help='Check All devices inode status')
    allnodeParser.set_defaults(func=checkStatusAll)
    allnodeParser.add_argument('-w', '--warning', dest='warning', action='store', help='Warning level of inodes utilization, in percent', default=90)
    allnodeParser.add_argument('-c', '--critical', dest='critical', action='store', help='Critical level of inodes utilization, in percent', default=96)
    allnodeParser.add_argument('-e', '--exclude', dest='exclude', action='store', help='Critical level of inodes utilization')
    return parser

if __name__ == '__main__':
    checkRequirments()
    parser = argumentParser()
    args = parser.parse_args()
    args.func(args)