# !/usr/bin/env python3

import argparse
import hashlib
import os
from collections import defaultdict
from tabulate import tabulate


# source https://gist.githubusercontent.com/rene-d/9e584a7dd2935d0f461904b9f2950007/raw/e2e58ccf955475d8066338a4e538c52debc06a06/colors.py
""" ANSI color codes """
BLACK           = "\033[0;30m"
RED             = "\033[0;31m"
GREEN           = "\033[0;32m"
BROWN           = "\033[0;33m"
BLUE            = "\033[0;34m"
PURPLE          = "\033[0;35m"
CYAN            = "\033[0;36m"
LIGHT_GRAY      = "\033[0;37m"
DARK_GRAY       = "\033[1;30m"
YELLOW          = "\033[1;33m"
BOLD_RED        = "\033[1;31m"
BOLD_GREEN      = "\033[1;32m"
BOLD_BLUE       = "\033[1;34m"
BOLD_PURPLE     = "\033[1;35m"
BOLD_CYAN       = "\033[1;36m"
BOLD_WHITE      = "\033[1;37m"
BOLD            = "\033[1m"
FAINT           = "\033[2m"
ITALIC          = "\033[3m"
UNDERLINE       = "\033[4m"
BLINK           = "\033[5m"
NEGATIVE        = "\033[7m"
CROSSED         = "\033[9m"
END             = "\033[0m"


def find_dupes(path):
    try:
        total_files_in_path = 0
        total_path_size = 0

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
        for current_path, _, files_in_current_path in os.walk(path):
            # if "originals" in current_path:
            #     continue

            for file in files_in_current_path:
                total_files_in_path += 1
                full_path_to_file = os.path.join(current_path, file)
                # print(f"Sizing {full_path_to_file}...")

                if not os.path.exists(full_path_to_file):
                    # print(f"{file} does not exist")
                    continue

                file_size = os.path.getsize(full_path_to_file)
                total_path_size += file_size
                size_dict[file_size].append(full_path_to_file)
        

        """
        Now we iterate over the values of size_dict (which are lists whose size is either 1 or greater than 1)
        If the list size is equal to one, we can be certain that this is the only file of its kind in this directory (in other words, this file is unique), so we add it
        to unique_files list
        If the list size is greater than one, we compute the file has for every file within the list and add it to hash_dict[file_hash]
        """
        for file_list in size_dict.values():
            if len(file_list) == 1:
                # We do file_list[0] because we know that there is only one item in this list
                unique_files.append(file_list[0])
            else:
                for file in file_list:
                    try:
                        with open(file, "rb") as file_object:
                            file_hash = hashlib.sha256(file_object.read()).hexdigest()
                            hash_dict[file_hash].append(file)
                        # print(f"Hashing {file}...")
                    
                    except (PermissionError, IsADirectoryError) as e:
                        print(f"Error processing file {file}: {e}")


        """
        Now we do the exact same thing we did in the previous step
        We iterate over hash_dict.values()
        If the size of the list == 1, we add it to unique_files
        Otherwise, we can be certain that the files in the list are duplicates, so we can flatten the list and add every file to duplicate_files
        """
        for file_list in hash_dict.values():
            if len(file_list) == 1:
                unique_files.append(file_list[0])
            else:
                for file in file_list:
                    duplicate_files.append(file)

        unique_files_size = 0
        for file in unique_files:
            if not os.path.exists(file):
                continue
            unique_files_size += os.path.getsize(file)

        duplicate_files_size = 0
        for file in duplicate_files:
            if not os.path.exists(file):
                continue
            duplicate_files_size += os.path.getsize(file)

        """
        Print out info about what we just did
        """
        def format_size(size):
            return f"{BOLD_BLUE}{size:_} {BOLD_GREEN}bytes{END}"

        table = [
            [f"Number of files",           f"{BOLD_BLUE}{total_files_in_path}{END}"],
            [f"Size of files",             format_size(total_path_size)],
            [f"Number of unique files",    f"{YELLOW}{len(unique_files)}{END}"],
            [f"Size of unique files",      format_size(unique_files_size)],
            [f"Number of duplicate files", f"{BOLD_RED}{len(duplicate_files)}{END}"],
            [f"Size of duplicate files",   format_size(duplicate_files_size)],
        ]

        print(f"\n{YELLOW}Report of scanning {BOLD_PURPLE}{path}{END}\n")
        print(tabulate(table, tablefmt="fancy_grid"))

        """
        Write duplicate_files to a file called `duplicate_files.txt` found in the `path` directory
        """
        duplicate_files_text_file_path = os.path.join(path, "duplicate_files.txt")
        # Create and clear the file before appending to it
        with open(duplicate_files_text_file_path, "w") as output_file:
            output_file.write("")

        for file in duplicate_files:
            with open(duplicate_files_text_file_path, "a") as output_file:
                output_file.write(file + "\n")

        print(f"\n{BOLD_BLUE}{duplicate_files_text_file_path}{END}{BOLD_GREEN} was successfully written{END}")


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



