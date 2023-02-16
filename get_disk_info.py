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
for vgs in vgs_cmd_output.splitlines():
    vg = OrderedDict()
    vg['name'] = vgs.split()[0]
    vg['size'] = vgs.split()[1]
    vg['free'] = vgs.split()[2]
    vg['relatedPvs'] = []  # Value will be updated during the create PV list step
    vg['relatedLvs'] = []  # Value will be updated during the create LV list step
    vg_list.append(vg)

# Create a list of logical volumes
lv_list = []
lvs_cmd_output = run_os_command(
    "lvs --units b --noheadings --options \"name,size,vg_name\"")
for lvs in lvs_cmd_output.splitlines():
    lv = OrderedDict()
    lv['name'] = lvs.split()[0]
    lv['size'] = lvs.split()[1]
    lv['relatedVg'] = lvs.split()[2]
    lv['relatedFs'] = ""  # Value will be updated during the create FS list step
    lv_list.append(lv)

    # Update the relatedLvs field of the vg_list
    for count, vg in enumerate(vg_list):
        if lvs.split()[2] == vg['name']:
            vg_list[count]['relatedLvs'].append(lvs.split()[0])

# Create a list of filesystems
fs_list = []
df_cmd_out = run_os_command("df -TB1")
for lvs in lvs_cmd_output.splitlines():
    vg_name = lvs.split()[2]
    lv_name = lvs.split()[0]
    for df in df_cmd_out.splitlines():
        s = re.search('{}-{}'.format(vg_name, lv_name), df)
        if s:
            fs = OrderedDict()
            fs['name'] = df.split()[0]
            fs['mountpoint'] = df.split()[6]
            fs['size'] = df.split()[2] + "B"
            fs['used'] = df.split()[3] + "B"
            fs['available'] = df.split()[4] + "B"
            fs['relatedLv'] = lv_name
            fs['type'] = df.split()[1]
            fs_list.append(fs)

            # Update the relatedFs field of the lv_list
            for count, lv in enumerate(lv_list):
                if lv_name == lv['name']:
                    lv_list[count]['relatedFs'] = df.split()[0]

# Create a list of physical volumes
pv_list = []
pvs_cmd_out = run_os_command(
    "pvs --units b --noheadings --options \"name,size,free,vg_name\"")
for pvs in pvs_cmd_out.splitlines():
    pv = OrderedDict()
    pv['name'] = pvs.split()[0]
    pv['size'] = pvs.split()[1]
    pv['free'] = pvs.split()[2]
    pv['relatedDisk'] = ""  # Value will be updated during the create disk list step
    pv['relatedVg'] = pvs.split()[3]
    pv_list.append(pv)

    # Update the relatedPvs field of the vg_list
    for count, vg in enumerate(vg_list):
        if pvs.split()[3] == vg['name']:
            vg_list[count]['relatedPvs'].append(pvs.split()[0])

# Create a list of disks
disk_list = []
lsblk_cmd_out = run_os_command("lsblk -lnbo \"name,size,type,pkname\"")
for lsblk in lsblk_cmd_out.splitlines():
    s = re.search("disk", lsblk)
    if s:
        disk = OrderedDict()
        disk['name'] = "/dev/" + lsblk.split()[0]
        disk['size'] = lsblk.split()[1] + 'B'
        disk['relatedPvs'] = []
        # Update the relatedDisk and the relatedPvs fields of the pv_list and disk_list respectively
        for lsblk_2 in lsblk_cmd_out.splitlines():
            if len(lsblk_2.split()) == 4 and lsblk_2.split()[3] == lsblk.split(
            )[0]:
                for count, pv in enumerate(pv_list):
                    pv_name = "/dev/" + lsblk_2.split()[0]
                    if pv_name == pv['name']:
                        pv_list[count]['relatedDisk'] = disk['name']
                        disk['relatedPvs'].append(pv_name)
        disk_list.append(disk)

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
