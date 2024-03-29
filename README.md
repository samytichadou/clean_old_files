# clean_old_files

This simple python script is a CLI utility to clean old files on every type of project which uses file versioning.

### Main functions :
- Remove old versioned files, according to version pattern and number of versions to keep
- Remove folder and its content and files according to an "old pattern" (for example, files/folders which has an "_old" suffix)

Removed files/folders can be delete or moved to another location, and optionnaly compressed at the end of the process.

### Usage :
The command has this form :
`python_path clean_old_files.py folder_to_clean_path -arguments`

Here are available arguments :
- `-h` : Help
- `-v` : Number of versions to keep (ex : -v 5)
- `-p` : Regex version pattern to look for. "_v[0-9][0-9][0-9]" by default (ex : -p regex_pattern)
- `-e` : File extensions to search, comma separated (-e ext1,ext2)
- `-a` : Archive folder (-a archive_folderpath)
- `-n` : No archive compression, archive is compressed by default
- `-o` : Remove old files and folders according to old pattern list
- `-l` : Old pattern list, comma separated. "_old", "old_" by default (-l _pat1,pat2)
- `-y` : Do not ask for user confirmation
- `-d` : Debug mode
