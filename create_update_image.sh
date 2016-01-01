#!/bin/sh
#
# Copyright (C) 2015, Jaguar Land Rover
#
# Mozilla Public License, version 2.0.  The full text of the 
# Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
#
# Create a software update squashfs image with the given manifest file
#

usage() {
    echo "Usage: $0 -d update_dir -o squasfs_fname"
    echo
    echo "  -d update_dir       The directory to create a squashfs image from."
    echo "                      The directory must contain a 'update_manifest.json' file."
	echo
    echo "  -o update_fname     The file name of the squashfs image to be generated."
	echo
    exit 1
}

MANIFEST_FILE="update_manifest.json"

unset UPDATE_DIR
unset OUT_FILE
while getopts "d:o:" o; do
    case "${o}" in
        d)
            UPDATE_DIR=${OPTARG}
            ;;
        o)
            OUT_FILE=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

# Check that we have a update dir
if [ -z "${UPDATE_DIR}" ]
then
	echo
	echo "Missing -d option."
	echo
	usage
fi

# Check that we have a update dir
if [ -z "$OUT_FILE}" ]
then
	echo
	echo "Missing -o option."
	echo
	usage
fi

if [ ! -r "${UPDATE_DIR}/${MANIFEST_FILE}" ]
then
	echo
	echo "${UPDATE_DIR}/${MANIFEST_FILE} cannot be opened" 
	echo
	usage
fi

#
# Check that we have a manifest file
#

#
# Check that we do have squashfs tools installed
#
if [ -z "$(which mksquashfs)" ]
then
	echo "Squashfs package not installed. Try:"
	echo "   sudo apt-get install squashfs-tools"
	exit 1
fi

# Create baseline squashfs image
rm -f ${OUT_FILE}
mksquashfs  ${UPDATE_DIR} ${OUT_FILE}

exit 0
