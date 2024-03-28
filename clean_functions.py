# USAGE

# Command Example
# cmd folderpath -v 5 -e blend,blend1 -a archivefolder -n -p _v[0-9][0-9][0-9] -o -l _old,_bin -y -d


import os
import re
import shutil
import pathlib
import datetime
import sys

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
        remove_old_patterns,
        old_patterns,
        debug,
    ):
    old_files_list = []
    total_size = 0

    for extension in extensions:
        file_list = []

        for file in os.listdir(folderpath):
            name, ext = os.path.splitext(file)

            # Get old file with old patterns
            if remove_old_patterns:
                for pattern in old_patterns:
                    if pattern in file:
                        file_list.append((file, _get_version(name, version_pattern)))
                        continue

            # Get old file with extension
            if ext==extension:
                file_list.append((file, _get_version(name, version_pattern)))

        try:
            file_list.sort(reverse=True, key=lambda a: a[1])
        except TypeError:
            if debug: print(f"DEBUG - Unable to find file versions for {extension}")
            break

        for k in range(0, len(file_list)):
            if k>=versions_to_keep:
                filepath = os.path.join(folderpath, file_list[k][0])
                old_files_list.append(filepath)
                total_size += os.path.getsize(filepath)

    return old_files_list, total_size

def _find_folder_to_process_recursively(
    folderpath,
    extensions,
    remove_old_patterns,
    old_patterns,
    debug,
    ):
    directories_list = []
    old_directories_list = []

    for root, subfolders, files in os.walk(folderpath):

        # Find dirs containing old pattern
        for sub in subfolders:
            if remove_old_patterns:
                for pattern in old_patterns:
                    if pattern in sub:
                        old_directories_list.append(os.path.join(root, sub))

        # Find dirs containing files with extension
        for name in files:
            if os.path.splitext(name)[1] in extensions:
                if root not in directories_list:
                    if debug: print(f"DEBUG - Files found in {root}")
                    directories_list.append(root)

    return directories_list, old_directories_list

def _find_old_files(
        folderpath,
        extensions,
        versions_to_keep,
        version_pattern,
        remove_old_patterns,
        old_patterns,
        debug,
):
    total_size = 0

    # Get subfolders
    subfolders, old_subfolders =  _find_folder_to_process_recursively(
        folderpath,
        extensions,
        remove_old_patterns,
        old_patterns,
        debug,
    )

    # Get old subfolders informations
    old_files_number = 0
    for sub in old_subfolders:
        for file in os.listdir(sub):
            old_files_number += 1
            total_size += os.path.getsize(os.path.join(sub, file))

    # Get old files
    files_to_remove = []
    for subfolder in subfolders:
        files, size = _find_old_files_in_folder(
                subfolder,
                extensions,
                versions_to_keep,
                version_pattern,
                remove_old_patterns,
                old_patterns,
                debug,
        )
        files_to_remove.extend(files)
        total_size += size

    # Print informations
    total_size = total_size*0.00000125 # Convert to Mo
    print()
    print(f"{len(old_subfolders)} old folders to remove")
    print(f"{len(files_to_remove) + old_files_number} files to remove")
    print(f"{total_size} Mo will be freed")
    print()

    return files_to_remove, old_subfolders

def clean_files(
        files_to_remove,
        folders_to_remove,
        archive_folder,
        archive_compression,
        debug,
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
            if debug: print(f"DEBUG - Moving {filepath} to {dest}")
            shutil.move(filepath, dest)
        else:
            # Remove file
            if debug: print(f"DEBUG - Removing {filepath}")
            os.remove(filepath)

    # Process folders
    for folderpath in folders_to_remove:

        if archive_folder:
            # Get archive filepath
            p = pathlib.Path(folderpath)
            dest = os.path.dirname(os.path.join(archive_path, pathlib.Path(*p.parts[2:])))
            # Create folders if needed
            if not os.path.isdir(dest):
                os.makedirs(dest)
            # Copy folder
            if debug: print(f"DEBUG - Moving {folderpath} to {dest}")
            shutil.move(folderpath, dest)
        else:
            # Remove folder
            if debug: print(f"DEBUG - Removing {folderpath}")
            shutil.rmtree(folderpath)

    # Zip archive if needed
    if archive_folder and archive_compression:
        # Zip folder
        shutil.make_archive(archive_path, 'zip', archive_path)
        # Remove archive folder
        shutil.rmtree(archive_path)

    # Print informations
    print()
    print(f"{len(folders_to_remove)} old folders removed")
    print(f"{len(files_to_remove)} files removed")

    return files_to_remove

def _print_help():
    print()
    print("Help")
    print()
    print("Command : python clean_old_files.py folderpath_to_clean arguments")
    print()
    print("-h               Help")
    print()
    print("-v               Versions to keep (-v 5)")
    print("-p               Regex version pattern to look for. _v[0-9][0-9][0-9] by default (-p pattern)")
    print()
    print("-e               File extensions to search, comma separated (-e ext1,ext2)")
    print()
    print("-a               Archive folder (-a folderpath)")
    print("-n               No archive compression")
    print()
    print("-o               Remove old files and folders according to old pattern list")
    print("-l               Old pattern list, comma separated. _old, old_ by default (-l _pat1,pat2)")
    print()
    print("-y               Do not ask for user confirmation")
    print("-d               Debug mode")
    print()
    print("Command example")
    print(r"python clean_old_files.py folderpath -v 5 -e blend,blend1 -a archivefolder -n -p _v[0-9][0-9][0-9] -o -l _old,_bin -d")
    print()

### PROCESS

# Catch wrong command
if len(sys.argv)<=1:
    print()
    print("Missing argument, -h for help")
    exit()
elif sys.argv[1]!="-h" and not os.path.isdir(sys.argv[1]):
    print()
    print("Missing folderpath, -h for help")
    exit()
# Help argument
elif "-h" in sys.argv:
    _print_help()
    exit()

# Default arguments
versions = 5
extensions = [".blend", ".blend1", ".blend2", ".blend3"]
archive_folder = None
zip = True
version_pattern = r"_v[0-9][0-9][0-9]"
remove_old_patterns = False
old_patterns = [r"_old", r"old_"]
no_user_confirmation = False
debug = False

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
    elif sys.argv[i]=="-o":
        remove_old_patterns = True
    elif sys.argv[i]=="-l":
        old_patterns = []
        for pat in sys.argv[i+1].split(","):
            old_patterns.append(f".{pat}")
    elif sys.argv[i]=="-y":
        no_user_confirmation = True
    elif sys.argv[i]=="-d":
        debug = True

# Arguments used
print()
print(f"Folder to search :      {folderpath}")
print(f"File extensions :       {extensions}")
print(f"Versions to keep :      {versions}")
print(f"Version pattern :       {version_pattern}")
print(f"Archive folder :        {archive_folder}")
print(f"Archive compression :   {zip}")
print(f"Remove old patterns :   {remove_old_patterns}")
print(f"Old patterns :          {old_patterns}")
print(f"No user confirmation :  {no_user_confirmation}")
print()

# Get files to process
files, folders = _find_old_files(
    folderpath,
    extensions,
    versions,
    version_pattern,
    remove_old_patterns,
    old_patterns,
    debug,
    )

# Abort if no files found
if not len(files) and not len(folders):
    print("Aborting")
    exit()

# User confirmation
if not no_user_confirmation:
    confirmation = input("Are you sure ? Type yes/y to start : ")
    if not confirmation.lower() in {"y","yes"}:
        print("Aborting")
        exit()

# Process files
clean_files(
    files,
    folders,
    archive_folder,
    zip,
    debug,
    )
