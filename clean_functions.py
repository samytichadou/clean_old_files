import os
import re

folder = r""
versions_to_keep = 5
version_pattern = "_v###_"
extensions = [
    "blend",
]
archive_folder = r""
dry_run = False # Estimate


def _get_version(filename):
    version = re.findall(r"_v[0-9][0-9][0-9]", filename)
    if version and len(version)==1:
        return int(version[0].replace("v","").replace("_",""))
    else:
        return None

def _find_old_files(
        folderpath,
        extensions,
        versions_to_keep,
):
    old_files_list = []

    for extension in extensions:
        file_list = []
        for file in os.listdir(folderpath):
            name, ext = os.path.splitext(file)
            if ext==extension:
                file_list.append((file, _get_version(name)))

        try:
            file_list.sort(reverse=True, key=lambda a: a[1])
        except TypeError:
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
                    directories_list.append(root)
    return directories_list

def _move_file(filepath):
    return

def _remove_file(filepath):
    return

def _zip_folder(filepath):
    return

def clean_folder(
        folderpath,
        extensions,
        versions_to_keep,
):
    subfolders =  _find_folder_containing_files_recursively(
        folderpath,
        extensions,
    )

    files_to_remove = []
    for subfolder in subfolders:
        files_to_remove.extend(
            _find_old_files(
                subfolder,
                extensions,
                versions_to_keep,
            )
        )
    return files_to_remove

# print(
#     _find_old_files(
#         r"C:\Users\admin\Documents\test_clean\Shots\e101\e101_sq012\e101_sq012_e101_sh044\Animation",
#         [".blend",".blend1"],
#         3,
#     )
# )

# print(
#     _find_folder_containing_files_recursively(
#         r"C:\Users\admin\Documents\test_clean",
#         [".blend", ".blend1"],
#     )
# )


files = clean_folder(
        #r"C:\Users\admin\Documents\test_clean",
        r"C:\Users\admin\workfiles",
        [".blend", ".blend1"],
        5,
    )

print("---START")
for f in files:
    print(f)