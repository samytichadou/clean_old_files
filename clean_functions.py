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

def _find_old_files(
        folderpath,
        extensions,
        versions_to_keep,
        version_pattern,
):
    old_files_list = []

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
                old_files_list.append(os.path.join(folderpath, file_list[k][0]))

    return old_files_list

def _find_folder_containing_files_recursively(folderpath, extensions):
    directories_list = []
    for root, subfolders, files in os.walk(folderpath):
        for name in files:
            if os.path.splitext(name)[1] in extensions:
                if root not in directories_list:
                    print(f"DEBUG - Files found in {root}")
                    directories_list.append(root)
    return directories_list

def _remove_file(filepath):
    return

def _zip_folder(filepath):
    return

def clean_folder(
        folderpath,
        extensions,
        versions_to_keep,
        dry_run,
        archive_folder,
        archive_compression,
        version_pattern,
):
    subfolders =  _find_folder_containing_files_recursively(
        folderpath,
        extensions,
    )

    # Get file list to remove
    files_to_remove = []
    for subfolder in subfolders:
        files_to_remove.extend(
            _find_old_files(
                subfolder,
                extensions,
                versions_to_keep,
                version_pattern,
            )
        )

    # Get archive folder path if needed
    if archive_folder:
        archive_name = f"archivedfiles_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        archive_path = os.path.join(archive_folder, archive_name)

    # Process files
    total_size = 0
    for filepath in files_to_remove:
        total_size += os.path.getsize(filepath)

        if not dry_run:
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
    if archive_folder and archive_compression and not dry_run:
        # Zip folder
        shutil.make_archive(archive_path, 'zip', archive_path)
        # Remove archive folder
        shutil.rmtree(archive_path)


    # Print informations
    total_size = total_size*0.00000125 # Convert to Mo
    print()
    print(f"DEBUG - {len(files_to_remove)} files removed")
    print(f"DEBUG - {total_size} Mo freed")

    return files_to_remove

# cmd folderpath -d -v 5 -e blend,blend1 -a folder -nozip -h


if not len(sys.argv)>1:
    print("Missing argument, -h for help")
    exit()
elif sys.argv[1]!="-h" and not os.path.isdir(sys.argv[1]):
    print("Missing folderpath, -h for help")
    exit()
elif sys.argv[1]=="-h":
    print("Help")
    print()
    print("Command : python clean_old_files.py folderpath_to_clean arguments")
    print()
    print("-h               Help")
    print("-d               Dry Run mode")
    print("-v               Versions to keep (-v 5)")
    print("-e               File extensions to search, comma separated (-e ext1,ext2)")
    print("-a               Archive folder (-a folderpath)")
    print("-n               No archive compression")
    print("-p               Regex version pattern to look for (-p pattern)")
    exit()

# Parse arguments
dry_run = False
versions = 5
extensions = [".blend", ".blend1", ".blend2", ".blend3"]
archive_folder = ""
zip = True
version_pattern = r"_v[0-9][0-9][0-9]"

folderpath = sys.argv[1]
for i in range(len(sys.argv)):
    if sys.argv=="-d":
        dry_run = True
    elif sys.argv=="-nozip":
        zip = False
    elif sys.argv=="-v":
        versions = sys.argv[i+1]
    elif sys.argv=="-e":
        extensions = []
        for ext in sys.argv[i+1].split(","):
            extensions.append(f".{ext}")
    elif sys.argv=="-a":
        archive_folder = sys.argv[i+1]
    elif sys.argv=="-p":
        version_pattern = sys.argv[i+1]

files = clean_folder(
        folderpath, # Folder to clean
        extensions, # Extensions to clean
        versions, # Versions to keep
        dry_run, # DryRun
        archive_folder, # Archive folder (no archive if empty)
        zip, # Compress archive
        version_pattern, # Version Pattern
    )
