# GPFS monitoring scripts 

The repo contains a few useful scripts to monitor GPFS file system. Scripts can be integrated with Zabbix/Nagios/etc

[Usage](#usage)
* [Inode status](#inode-status)
* [Inode Fileset status](#inode-fileset-status)

### Usage
#### Inode status
Provide inode status information per device (disk) or for all.
Warning and critical levels can be specified.
In **all** option its possibly to exclude some devices from check with parameter **-e**

    [root@node1 ]# ./gpfs_inode_status.py all
    OK - FS1-3.08%;; Used=4345; Allocated=141120
    OK - FS2-6.19%;; Used=4070; Allocated=65792
    OK - FS3-6.23%;; Used=4101; Allocated=65792
    | FS1=3.08%;90;96;0;100; FS1_Used=4345;;;;; FS1_Allocated=141120;;;;; FS2=6.19%;90;96;0;100; FS2_Used=4070;;;;; FS2_Allocated=65792;;;;; FS3=6.23%;90;96;0;100; FS3_Used=4101;;;;; FS3_Allocated=65792;;;;;

    [root@node1 ]# ./gpfs_inode_status.py device -d FS1 -w 3 -c 30
    WARNING - FS1 - 3.08%;; Used=4345; Allocated=141120
    | FS1=3.08%;3;30;0;100; FS1_Used=4345;;;;; FS1_Allocated=141120;;;;;


#### Inode Fileset status
Provide inode status information per Fileset on particular device.
Warning and critical levels can be specified.

    [root@node1 ]# ./gpfs_inode_fileset_status.py device -d FS1
    FS1| fset1=0.01%;90;96;0;100; fset1_Used=7;62899;67092;0;69888;  fset2=0.00%;90;96;0;100; fset2_Used=1;62899;67092;0;69888;  fset=0.04%;90;96;0;100; fset_Used=31;63130;67338;0;70144;  fset3=0.09%;90;96;0;100; fset3_Used=1;979;1044;0;1088; 

    [root@node1 ]# ./gpfs_inode_fileset_status.py device -d FS1 -f fset1 -w 70 -c 80 -p
    FS1| fset1=0.01%;70;80;0;100; 


