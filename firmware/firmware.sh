#!/bin/bash

# Author: Christian Hofstaedtler <hofstaedtler@inqnet.at>
# This file is licensed under the MIT license.

progress() {
	echo
	echo -e " \033[1;31m `date` \033[0m"
	echo -e " \033[1;31m >>\033[1;32m $@ \033[0m"
}

progress "Beginning Firmware Upgrade process"

HWMODEL=`dmidecode --string system-product-name`

progress "Upgrading ILO2 firmware... please wait and DO NOT POWER DOWN SERVER"
./ILO2_FW.scexe -- --silent
sleep 10

if [[ "$HWMODEL" == "ProLiant DL360 G6" ]]; then
	progress "DL360G6: Flashing BIOS"
	./DL360G6_BIOS.scexe -- --silent

	progress "DL360G6: Flashing Power Management Controller"
	./DL360G6_POWERMGMT.scexe -- --silent
fi

if [[ "$HWMODEL" == "ProLiant DL360 G5" ]]; then
	progress "DL360G5: Flashing BIOS"
	./DL360G5_BIOS.scexe -- --silent

	progress "DL360G5: Flashing Power Management Controller"
	./DL360G5_POWERMGMT.scexe -- --silent
fi

if [[ `lspci -n | grep -c 103c:3238` == "1" ]]; then
	progress "SA E200i: Flashing firmware"
	./SA_E200_FW.scexe -- --silent
fi

if [[ `lspci -n | grep -c 103c:3230` == "1" ]]; then
	progress "SA P400(i): Flashing firmware"
	./SA_P400_FW.scexe -- --silent
fi

if [[ `lspci -n | grep -c 103c:323a` == "1" ]]; then
	progress "SA P410i: Flashing firmware"
	./SA_P410_FW.scexe -- --silent
fi

progress "Probing Disk firmware"
for fw in disks/*.scexe; do
	if [[ `./$fw -- -d | grep -c '<action value="upgrade"'` != "0" ]]; then
		products=`./$fw -- -d | grep '<product_id' | sed -r -e 's/^.* value="([a-zA-Z0-9]+)".*$/\1/' | xargs echo`
		progress "Flashing disk firmware $fw for products $products"
		./$fw -- --silent
	fi
done

progress "Firmware Upgrade process completed"

