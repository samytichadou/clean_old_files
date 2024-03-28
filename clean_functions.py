# USAGE

# Command Example
# cmd folderpath -v 5 -e blend,blend1 -a archivefolder -n


import os
import re
import shutil
import pathlib
import datetime
import sys

#TODO Add _old functionality for folders and/or files

def _get_version(
    filename,
    pattern,
    ):
    version = re.findall(pattern, filename)
    if version and len(version)==1:
        return int(version[0].replace("v","").replace("_",""))
    else:
        return None

def _find_old_files_in_folder(
        folderpath,
        extensions,
        versions_to_keep,
        version_pattern,
):
    old_files_list = []
    total_size = 0

    for extension in extensions:
        file_list = []
        for file in os.listdir(folderpath):
            name, ext = os.path.splitext(file)
            if ext==extension:
                file_list.append((file, _get_version(name, version_pattern)))

        try:
            file_list.sort(reverse=True, key=lambda a: a[1])
        except TypeError:
            print("DEBUG - Unable to find file version")
            return []

        for k in range(0, len(file_list)):
            if k>=versions_to_keep:
                filepath = os.path.join(folderpath, file_list[k][0])
                old_files_list.append(filepath)
                total_size += os.path.getsize(filepath)

    return old_files_list, total_size

def _find_folder_containing_files_recursively(folderpath, extensions):
    directories_list = []
    for root, subfolders, files in os.walk(folderpath):
        for name in files:
            if os.path.splitext(name)[1] in extensions:
                if root not in directories_list:
                    print(f"DEBUG - Files found in {root}")
                    directories_list.append(root)
    return directories_list

def _find_old_files(
        folderpath,
        extensions,
        versions_to_keep,
        version_pattern,
):
    total_size = 0

    # Get subfolders
    subfolders =  _find_folder_containing_files_recursively(
        folderpath,
        extensions,
    )
    # Get old files
    files_to_remove = []
    for subfolder in subfolders:
        files, size = _find_old_files_in_folder(
                subfolder,
                extensions,
                versions_to_keep,
                version_pattern,
        )
        files_to_remove.extend(files)
        total_size += size

    # Print informations
    total_size = total_size*0.00000125 # Convert to Mo
    print()
    print(f"DEBUG - {len(files_to_remove)} files to remove")
    print(f"DEBUG - {total_size} Mo will be freed")

    return files_to_remove

def clean_files(
        files_to_remove,
        archive_folder,
        archive_compression,
):
    # Get archive folder path if needed
    if archive_folder:
        archive_name = f"archivedfiles_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        archive_path = os.path.join(archive_folder, archive_name)

    # Process files
    for filepath in files_to_remove:

        if archive_folder:
            # Get archive filepath
            p = pathlib.Path(filepath)
            dest = os.path.join(archive_path, pathlib.Path(*p.parts[2:]))
            # Create folders if needed
            if not os.path.isdir(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))
            # Copy file
            print(f"DEBUG - Moving {filepath} to {dest}")
            shutil.move(filepath, dest)
        else:
            # Remove file
            print(f"DEBUG - Removing {filepath}")
            os.remove(filepath)

    # Zip archive if needed
    if archive_folder and archive_compression:
        # Zip folder
        shutil.make_archive(archive_path, 'zip', archive_path)
        # Remove archive folder
        shutil.rmtree(archive_path)

    # Print informations
    print(f"DEBUG - {len(files_to_remove)} files removed")

    return files_to_remove

def _print_help():
    print()
    print("Help")
    print()
    print("Command : python clean_old_files.py folderpath_to_clean arguments")
    print()
    print("-h               Help")
    print("-v               Versions to keep (-v 5)")
    print("-e               File extensions to search, comma separated (-e ext1,ext2)")
    print("-a               Archive folder (-a folderpath)")
    print("-n               No archive compression")
    print("-p               Regex version pattern to look for (-p pattern)")


### PROCESS

# Catch wrong command
if len(sys.argv)<=1:
    print()
    print("Missing argument, -h for help")
    _print_help()
    exit()
elif sys.argv[1]!="-h" and not os.path.isdir(sys.argv[1]):
    print()
    print("Missing folderpath, -h for help")
    _print_help()
    exit()
# Help argument
elif "-h" in sys.argv:
    _print_help()
    exit()

# Default arguments
dry_run = False
versions = 5
extensions = [".blend", ".blend1", ".blend2", ".blend3"]
archive_folder = None
zip = True
version_pattern = r"_v[0-9][0-9][0-9]"

# Parse arguments
folderpath = sys.argv[1]
for i in range(len(sys.argv)):
    if sys.argv[i]=="-n":
        zip = False
    elif sys.argv[i]=="-v":
        versions = int(sys.argv[i+1])
    elif sys.argv[i]=="-e":
        extensions = []
        for ext in sys.argv[i+1].split(","):
            extensions.append(f".{ext}")
    elif sys.argv[i]=="-a":
        archive_folder = sys.argv[i+1]
    elif sys.argv[i]=="-p":
        version_pattern = sys.argv[i+1]

# Get files to process
files = _find_old_files(
    folderpath,
    extensions,
    versions,
    version_pattern,
    )

# Arguments used
print(f"DEBUG - Folder to search :      {folderpath}")
print(f"DEBUG - File extensions :       {extensions}")
print(f"DEBUG - Versions to keep :      {versions}")
print(f"DEBUG - Version pattern :       {version_pattern}")
print(f"DEBUG - Archive folder :        {archive_folder}")
print(f"DEBUG - Archive compression :   {zip}")

# Abort if no files found
if not len(files):
    print("Aborting")
    exit()

# User confirmation
confirmation = input("Are you sure ? Type yes/y to start : ")
if not confirmation.lower() in {"y","yes"}:
    print("Aborting")
    exit()

# Process files
clean_files(
    files,
    archive_folder,
    zip,
    )
