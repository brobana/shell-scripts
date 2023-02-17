#!/usr/bin/python2.7

import json
import subprocess
import re
from collections import OrderedDict

# Initialize variables
exit_code = 1


# Terminate the script with exit code
def terminate_script():
    if (exit_code != 0):
        print("The script terminated with exit code " + str(exit_code) + ".\n")
    exit(exit_code)


# Execute the OS command (cmd argument), then return the standard output
def run_os_command(cmd):
    try:
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        o, e = p.communicate()
        if p.returncode == 0:
            return o.decode()
        else:
            if 'not found' in e:
                raise Exception(e.strip("\n"))
    except Exception as e:
        print(
            str(e) +
            "\n\nERROR: Something went wrong with the script. Please see the previous message.\n"
        )
        terminate_script()


# Create a list of volume groups
vg_list = []
vgs_cmd_output = run_os_command(
    "vgs --units b --noheadings --options \"name,size,free\"")
for line in vgs_cmd_output.splitlines():
    vgs = line.split()
    vg = OrderedDict()
    vg['name'] = vgs[0]
    vg['size'] = vgs[1]
    vg['free'] = vgs[2]
    vg['relatedPvs'] = []  # Value will be updated during the create PV list step
    vg['relatedLvs'] = []  # Value will be updated during the create LV list step
    vg_list.append(vg)

# Create a list of logical volumes
lv_list = []
lvs_cmd_output = run_os_command(
    "lvs --units b --noheadings --options \"name,size,vg_name\"")
for line in lvs_cmd_output.splitlines():
    lvs = line.split()
    lv = OrderedDict()
    lv['name'] = lvs[0]
    lv['size'] = lvs[1]
    lv['relatedVg'] = lvs[2]
    lv['relatedFs'] = ""  # Value will be updated during the create FS list step
    lv_list.append(lv)

    # Update the relatedLvs field of the vg_list
    for count, vg in enumerate(vg_list):
        if lvs[2] == vg['name']:
            vg_list[count]['relatedLvs'].append(lvs[0])

# Create a list of filesystems
fs_list = []
df_cmd_out = run_os_command("df -TB1")
for line in lvs_cmd_output.splitlines():
    lvs = line.split()
    vg_name = lvs[2]
    lv_name = lvs[0]
    for line2 in df_cmd_out.splitlines():
        s = re.search('{}-{}'.format(vg_name, lv_name), line2)
        if s:
            df = line2.split()
            fs = OrderedDict()
            fs['name'] = df[0]
            fs['mountpoint'] = df[6]
            fs['size'] = df[2] + "B"
            fs['used'] = df[3] + "B"
            fs['available'] = df[4] + "B"
            fs['relatedLv'] = lv_name
            fs['type'] = df[1]
            fs_list.append(fs)

            # Update the relatedFs field of the lv_list
            for count, lv in enumerate(lv_list):
                if lv_name == lv['name']:
                    lv_list[count]['relatedFs'] = df[0]

# Create a list of disks
disk_list = []
lsblk_cmd_out = run_os_command("lsblk -lnbo \"name,size,type,pkname\"")
for line in lsblk_cmd_out.splitlines():
    s = re.search("disk", line)
    if s:
        lsblk = line.split()
        disk = OrderedDict()
        disk['name'] = "/dev/" + lsblk[0]
        disk['size'] = lsblk[1] + 'B'
        disk['relatedPvs'] = []
        disk_list.append(disk)

# Create a list of physical volumes
pv_list = []
pvs_cmd_out = run_os_command(
    "pvs --units b --noheadings --options \"name,size,free,vg_name\"")
for line in pvs_cmd_out.splitlines():
    pvs = line.split()
    pv = OrderedDict()
    pv['name'] = pvs[0]
    pv['size'] = pvs[1]
    pv['free'] = pvs[2]
    lsblk_cmd_out = run_os_command(
        "lsblk -lnbo \"name,type,pkname\" {} | head -1".format(pv['name']))
    lsblk = lsblk_cmd_out.split()
    pv['relatedDisk'] = '/dev/' + \
        lsblk[2] if lsblk[1] == 'part' else '/dev/' + lsblk[0]
    pv['relatedVg'] = pvs[3]
    pv_list.append(pv)

    # Update the relatedPvs field of the vg_list
    for count, vg in enumerate(vg_list):
        if pvs[3] == vg['name']:
            vg_list[count]['relatedPvs'].append(pvs[0])

    # Update the relatedPvs field of the disk_list
    for count, disk in enumerate(disk_list):
        if pv['relatedDisk'] == disk['name']:
            disk_list[count]['relatedPvs'].append(pv['name'])

# Put together all the lists that will be converted to JSON, then display them in the output
try:
    to_json = OrderedDict()
    to_json['disks'] = disk_list
    to_json['physicalVolumes'] = pv_list
    to_json['volumeGroups'] = vg_list
    to_json['logicalVolumes'] = lv_list
    to_json['filesystems'] = fs_list
    json_object = json.dumps(to_json, indent=4)
    print(json_object)
    exit_code = 0
except Exception as e:
    print(
        str(e) +
        "\n\nERROR: Something went wrong with the script. Please see the previous message.\n")
    terminate_script()

# End the script
terminate_script()
