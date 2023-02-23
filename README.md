# get_disk_info.py

### Overview

This script collects basic disk and volume data from a Linux system. It includes details about the relationships, size, and free space. The script needs to be run with `sudo` or as the **root** user.

The script uses `lsblk`, `pvs`, `vgs`, `lvs`, and `df` commands.

Currently, the sizes are displayed in bytes format.

### Usage
`[root@localhost ~]# python3 /tmp/get_disk_info.py` 

or

`[brobana@localhost ~]$ sudo python3 /tmp/get_disk_info.py`

### Sample output
```
{
    "disks": [
        {
            "name": "/dev/xvda",
            "size": "8589934592B",
            "relatedPvs": []
        },
        {
            "name": "/dev/xvdb",
            "size": "8589934592B",
            "relatedPvs": [
                "/dev/sdb"
            ]
        },
        {
            "name": "/dev/xvdc",
            "size": "8589934592B",
            "relatedPvs": [
                "/dev/sdc"
            ]
        }
    ],
    "physicalVolumes": [
        {
            "name": "/dev/sdb",
            "size": "8585740288B",
            "free": "6069157888B",
            "relatedDisk": "/dev/xvdb",
            "relatedVg": "tstappvg"
        },
        {
            "name": "/dev/sdc",
            "size": "8585740288B",
            "free": "8585740288B",
            "relatedDisk": "/dev/xvdc",
            "relatedVg": "devappvg"
        }
    ],
    "volumeGroups": [
        {
            "name": "devappvg",
            "size": "8585740288B",
            "free": "8585740288B",
            "relatedPvs": [
                "/dev/sdc"
            ],
            "relatedLvs": []
        },
        {
            "name": "tstappvg",
            "size": "8585740288B",
            "free": "6069157888B",
            "relatedPvs": [
                "/dev/sdb"
            ],
            "relatedLvs": [
                "tstapp1_lv",
                "tstapp2_lv"
            ]
        }
    ],
    "logicalVolumes": [
        {
            "name": "tstapp1_lv",
            "size": "1048576000B",
            "relatedVg": "tstappvg",
            "relatedFs": "/dev/mapper/tstappvg-tstapp1_lv"
        },
        {
            "name": "tstapp2_lv",
            "size": "1468006400B",
            "relatedVg": "tstappvg",
            "relatedFs": "/dev/mapper/tstappvg-tstapp2_lv"
        }
    ],
    "filesystems": [
        {
            "name": "/dev/mapper/tstappvg-tstapp1_lv",
            "mountpoint": "/tstapp1",
            "size": "1042161664B",
            "used": "41095168B",
            "available": "1001066496B",
            "relatedLv": "tstapp1_lv",
            "type": "xfs"
        },
        {
            "name": "/dev/mapper/tstappvg-tstapp2_lv",
            "mountpoint": "/tstapp2",
            "size": "1457520640B",
            "used": "44003328B",
            "available": "1413517312B",
            "relatedLv": "tstapp2_lv",
            "type": "xfs"
        }
    ]
}
```
