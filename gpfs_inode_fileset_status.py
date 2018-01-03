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
    Check if following tools are installed on the system: IBM Spectrum Scale
    """
    if not (os.path.isdir("/usr/lpp/mmfs/bin/") and os.path.isfile("/usr/lpp/mmfs/bin/mmgetstate") ):
        print(str(STATE_CRITICAL) + "CRITICAL - No IBM Spectrum Scale Installation detected." )



def checkStatusDevice(args):
    outputS=""
    criticalFlag=0

    if args.fset:
        fdout = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmlsfileset " + args.device + " root,"+args.fset +" -iY")
    else:
        fdout = executeBashCommand("sudo /usr/lpp/mmfs/bin/mmlsfileset " + args.device + " -iY")
    '''
    position 32 - MaxInodes
    position 33 - AllocInodes
    position 14 - Used
    position 7 - FileSet name

    '''

    for line in fdout.splitlines():
        if 'mmlsfileset' in line:
            if line.split(':')[7] in {'root'}:
                MaxInodesRoot = line.split(':')[33]
    for line in fdout.splitlines():
        if 'mmlsfileset' in line:
            if line.split(':')[7] not in {'root','filesetName'}:
                FileSet= line.split(':')[7]
                UsedInodes = float (line.split(':')[14])
                UsedInodesStr = line.split(':')[14]
                MaxInodes = float (line.split(':')[33])
                MaxInodesStr = line.split(':')[33]
                if int(MaxInodesStr) == 0 :
                    MaxInodesStr = MaxInodesRoot
                    MaxInodes = float(MaxInodesRoot)
                if 100 * UsedInodes/ MaxInodes > float(args.critical):
                   print ("CRITICAL - " + line.split(':')[7] )
                   criticalFlag=2
                elif 100 * UsedInodes/ MaxInodes > float(args.warning):
                    print ("WARNING - " + line.split(':')[7] )
                    if criticalFlag != 2:
                        criticalFlag=1
                if args.percent:
                    outputS = outputS + " " + FileSet + "=" + '{:.2f}'.format(100* UsedInodes/ MaxInodes) + "%;" + str(args.warning) + ";" + str(args.critical) + ";0;100; "
                elif args.number:
                    outputS = outputS + " " + FileSet +"_Used=" + UsedInodesStr + ";" +  '{:.0f}'.format(float(args.warning) * MaxInodes / 100) +";"+ '{:.0f}'.format(float(args.critical) * MaxInodes / 100)+ ";0;" + MaxInodesStr + "; "
                else:
                    outputS = outputS + " " + FileSet + "=" + '{:.2f}'.format(100* UsedInodes/ MaxInodes) + "%;" + str(args.warning) + ";" + str(args.critical) + ";0;100; " + FileSet +"_Used=" + UsedInodesStr + ";" +  '{:.0f}'.format(float(args.warning) * MaxInodes / 100) +";"+ '{:.0f}'.format(float(args.critical) * MaxInodes / 100)+ ";0;" + MaxInodesStr + "; "
    print (args.device + "|" + outputS )
    sys.exit(criticalFlag)




def executeBashCommand(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0]

def argumentParser():
    parser = argparse.ArgumentParser(description='Check inode fileset status')
    group = parser.add_argument_group();
    subParser = parser.add_subparsers()
    nodeParser = subParser.add_parser('device', help='Check inode status for FileSets per Device')
    nodeParser.set_defaults(func=checkStatusDevice)
    nodeParser.add_argument('-d', '--device', dest='device', action='store', help='Device to get inode stats', required=True)
    nodeParser.add_argument('-f', '--fset', dest='fset', action='store', help='Fileset, comma separated, to get inode stats')
    nodeParser.add_argument('-w', '--warning', dest='warning', action='store', help='Warning level of inodes utilization, in percent', default=90)
    nodeParser.add_argument('-c', '--critical', dest='critical', action='store', help='Critical level of inodes utilization, in percent', default=96)
    nodeParser.add_argument('-p', '--percent', dest='percent', action='store_true', help='Show output in percents')
    nodeParser.add_argument('-n', '--number', dest='number', action='store_true', help='Show output in numbers')


    return parser

if __name__ == '__main__':
    checkRequirments()
    #checkStatus()
    parser = argumentParser()
    args = parser.parse_args()
    args.func(args)