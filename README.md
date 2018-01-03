# GPFS monitoring scripts 

The repo contains a few useful scripts to monitor GPFS file system. Scripts can be integrated with Zabbix/Nagios/etc

[Usage](#usage)
* [Inode status](#inode-status)
* [Inode Fileset status](#inode-fileset-status)
* [Mounts status](#mounts-status)
* [Replications status](#replication-status)
* [Searching in GPFS logs](#search-in-gpfs-status)
* [Node status](#node-status)
* [Cluster status](#cluster-status)

### Usage
#### Inode status
Provide inode status information per device (disk) or for all.

Warning and critical levels can be specified.

In **all** option its possibly to exclude some devices from check with parameter **-e**(in case device in maintenance)

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

#### Mounts status
Help to monitor mounts per device and node. Example bellow:

    [root@node1 ]# ./gpfs_mounts.py all
    FS1;node1;node3;node4;node2
    FS2;node1;node2;node3;node4
    FS3;node1;node3;node2;node4
    [root@node1 ]# ./gpfs_mounts.py mounts -m FS2 -d node1
    OK - FS2
    [root@node1 ]# ./gpfs_mounts.py mounts -m fs_gpfs01 -d node3
    WARNING - fs_gpfs01 not mounted on node3

#### Replication status
Verify and test GPFS replication by creating file and verify replication flag.

Path for test file, with permission to write, should be specified.

    [root@node1 ]# ./gpfs_replication.py replication -p /FS1/
    1000+0 records in
    1000+0 records out
    65536000 bytes (66 MB) copied, 0.15785 s, 415 MB/s
    CRITICAL - replication failed on test file
    [root@node1 ]# mmlsattr /FS1/replication_testfile2 
      replication factors
    metadata(max) data(max) file    [flags]
    ------------- --------- ---------------
          2 (  2)   2 (  2) /FS1/replication_testfile2  [dataupdatemiss]


#### Searching in GPFS logs
The script allow to search for a specified line in GPFS logs on all or particular node.

The time period can be - **hour day week month**

Gives critical status if found string in logs.

Useful if you are looking for any event in logs.

    [root@node1 ]# ./gpfs_search_logs.py node -n node4 -t month -s gpfs_pagepool_small
    CRITICAL;node4;gpfs_pagepool_small

#### Node status
Get status from **mmgetstate** for all or particular node.

In **all** option its possibly to exclude nodes with **-e** parameter(in case node in maintenance).

    [root@node1 ]# ./gpfs_node.py all
    node1;active;node2;active;node3;active;node4;active;
    [root@node1 ]# ./gpfs_node.py device -d node2
    OK - node2 - active; nodesUp=1; quorumNeeded=1; totalNodes=4


#### Cluster status
Get status from **mmgetstate** for all or particular nodes and output the lowest as cluster status.

    [root@node1 ]# ./gpfs_cluster2.py all -e node3,node4
    WARNING;TIPS
    [root@node1 ]# ./gpfs_cluster2.py node -n  node3
    CRITICAL;DEGRADED
    [root@node1 ]# ./gpfs_cluster2.py node -n  node1
    WARNING;TIPS
    [root@node1 ]# mmhealth node show -N node3
    Node name:      node3
    Node status:    TIPS
    Status Change:  26 days ago
    Component      Status        Status Change     Reasons
    --------------------------------------------------------------------------------------------------
    GPFS           TIPS          26 days ago       gpfs_maxstatcache_high, gpfs_pagepool_small
    NETWORK        HEALTHY       26 days ago       -
    FILESYSTEM     DEGRADED      26 days ago       unmounted_fs_check(fs_gpfs01, fs_gpfs03, fs_gpfs02)
    DISK           DEGRADED      26 days ago       disk_down(nsd3)

