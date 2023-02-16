# get_disk_info.py
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
            "name": "/dev/sda",
            "size": "42949672960B",
            "relatedPvs": [
                "/dev/sda2"
            ]
        }
    ],
    "physicalVolumes": [
        {
            "name": "/dev/sda2",
            "size": "41871736832B",
            "free": "0B",
            "relatedDisk": "/dev/sda",
            "relatedVg": "cs"
        }
    ],
    "volumeGroups": [
        {
            "name": "cs",
            "size": "41871736832B",
            "free": "0B",
            "relatedPvs": [
                "/dev/sda2"
            ],
            "relatedLvs": [
                "root",
                "swap"
            ]
        }
    ],
    "logicalVolumes": [
        {
            "name": "root",
            "size": "37576769536B",
            "relatedVg": "cs",
            "relatedFs": "/dev/mapper/cs-root"
        },
        {
            "name": "swap",
            "size": "4294967296B",
            "relatedVg": "cs",
            "relatedFs": ""
        }
    ],
    "filesystems": [
        {
            "name": "/dev/mapper/cs-root",
            "mountpoint": "/",
            "size": "37558423552B",
            "used": "25470230528B",
            "available": "12088193024B",
            "relatedLv": "root",
            "type": "xfs"
        }
    ]
}

```
