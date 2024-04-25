# !/usr/bin/env python3

import argparse
import hashlib
import os
import stat
import time
from collections import defaultdict

from alive_progress import alive_bar
from tabulate import tabulate

# source https://gist.githubusercontent.com/rene-d/9e584a7dd2935d0f461904b9f2950007/raw/e2e58ccf955475d8066338a4e538c52debc06a06/colors.py
""" ANSI color codes """
BOLD            = "\033[1m"
END             = "\033[0m"


def file_has_read_permissions(file_mode):
    return stat.S_IRUSR & file_mode


def find_dupes(path):
    try:
        start_time = time.time()
        total_files_in_path = 0
        total_path_size = 0
        total_skipped_files = 0

        unique_files = []
        duplicate_files = []

        size_dict = defaultdict(list)
        hash_dict = defaultdict(list)

        """
        This walks every directory inside of `path` and looks at every file within every directory
        We first get the full path of every file
        Then we get the size in bytes of every file and add the file path to size_dict[file_size]

        We do it this way because it is possible for two completely different files to have the exact same size
        """
        with alive_bar(title=f"{BOLD}Scanning files\t\t\t\t{END}") as bar:
            for current_path, _, files_in_current_path in os.walk(path):
                total_files_in_path += len(files_in_current_path)

                for file in files_in_current_path:
                    bar()
                    # TODO add functionality to skip regex patterns from a .ignore file or a regex pattern

                    full_path_to_file = os.path.join(current_path, file)
                    if not os.path.exists(full_path_to_file):
                        continue

                    # If we don't have the rights to read a file, we should skip it
                    file_permissions = os.stat(full_path_to_file).st_mode

                    if not file_has_read_permissions(file_permissions):
                        total_skipped_files += 1
                        continue

                    # Skip socksets too I guess LOL
                    if stat.S_ISSOCK(file_permissions):
                        total_skipped_files += 1
                        continue


                    file_size = os.stat(full_path_to_file).st_size
                    total_path_size += file_size
                    size_dict[file_size].append(full_path_to_file)
        

        """
        Now we iterate over the values of size_dict (which are lists whose size is either 1 or greater than 1)
        If the list size is equal to one, we can be certain that this is the only file of its kind in this directory (in other words, this file is unique), so we add it
        to unique_files list
        If the list size is greater than one, we compute the file has for every file within the list and add it to hash_dict[file_hash]
        """
        with alive_bar(title=f"{BOLD}Hashing files\t\t\t\t{END}") as bar:
            for file_list in size_dict.values():
                if len(file_list) == 1:
                    # We do file_list[0] because we know that there is only one item in this list
                    unique_files.append(file_list[0])
                    bar()
                else:
                    for file in file_list:
                        if not os.path.exists(file):
                            continue
                        try:
                            with open(file, "rb") as file_object:
                                file_hash = hashlib.sha256(file_object.read()).hexdigest()
                                hash_dict[file_hash].append(file)
                            bar()
                        
                        except (PermissionError) as e:
                            print(f"{e}, skipping...")
                            total_skipped_files += 1
                            continue


        """
        Now we do the exact same thing we did in the previous step
        We iterate over hash_dict.values()
        If the size of the list == 1, we add it to unique_files
        Otherwise, we can be certain that the files in the list are duplicates, so we can flatten the list and add every file to duplicate_files
        """
        with alive_bar(title=f"{BOLD}Finding duplicates{END}\t\t\t") as bar:
            for file_list in hash_dict.values():
                if len(file_list) == 1:
                    unique_files.append(file_list[0])
                else:
                    for file in file_list:
                        duplicate_files.append(file)
                bar()

        unique_files_size = 0
        with alive_bar(title=f"{BOLD}Counting number of unique files{END}\t\t") as bar:
            for file in unique_files:
                if not os.path.exists(file):
                    continue
                unique_files_size += os.path.getsize(file)

        duplicate_files_size = 0
        with alive_bar(title=f"{BOLD}Counting number of duplicate files{END}\t") as bar:
            for file in duplicate_files:
                if not os.path.exists(file):
                    continue
                duplicate_files_size += os.path.getsize(file)

        """
        Write duplicate_files to a file called `duplicate_files.txt` found in the current directory
        """
        # Create and clear the file before appending to it
        with open("duplicate_files.txt", "w") as output_file:
            output_file.write("")

        with alive_bar(title=f"{BOLD}Writing to output file{END}\t\t\t") as bar:
            for file in duplicate_files:
                with open("duplicate_files.txt", "a") as output_file:
                    output_file.write(file + "\n")
                bar()

        elapsed_time = time.time() - start_time

        print(f"\n{BOLD}{os.path.abspath("./duplicate_files.txt")}{END} was successfully written")

        """
        Print out info about what we just did
        """
        def format_num(size):
            return f"{BOLD}{size:_}{END}"

        table = [
            [f"Total number of files",           format_num(total_files_in_path)],
            [f"Total number of unique files",    format_num(len(unique_files))],
            [f"Total number of duplicate files", format_num(len(duplicate_files))],
            [f"Total number of skipped files",   format_num(total_skipped_files)],

            [f"Total size of files",             f"{format_num(total_path_size)} bytes"],
            [f"Total size of unique files",      f"{format_num(unique_files_size)} bytes"],
            [f"Total size of duplicate files",   f"{format_num(duplicate_files_size)} bytes"],
            [f"Total time elapsed", f"{BOLD}{elapsed_time:.2f}{END} seconds"],
        ]

        print(tabulate(table, tablefmt="fancy_grid"))

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(
                        prog="doopie",
                        description="A script that finds duplicate files in a given directory")

    parser.add_argument("directory")
    parser.add_argument("-r", "--regex")
    parser.add_argument("-i", "--ignore")

    args = parser.parse_args()

    full_directory = os.path.abspath(args.directory)

    find_dupes(full_directory)


if __name__ == "__main__":
    main()
