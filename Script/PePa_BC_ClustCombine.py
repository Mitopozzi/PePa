#!/usr/bin/env python3

import os
import argparse
import time

def combine_csv_files(suffix, output_file):
    # Find all CSV files that contain the provided suffix anywhere in the filename before '.csv'
    csv_files = [file for file in os.listdir() if suffix in file and file.endswith('.csv')]

    # Check if any files are found
    if not csv_files:
        print(f"No CSV files with '{suffix}' suffix found.")
        return

    # Open the output file in write mode
    with open(output_file, 'w') as outfile:
        first_file = True

        for file in csv_files:
            print(f"Combining file: {file}")
            with open(file, 'r') as infile:
                header = infile.readline().strip()  # Read the header
                if first_file:
                    # Write header with additional column for file name
                    outfile.write(f"{header}\tfilename\n")
                    first_file = False
                else:
                    # Skip the header for subsequent files
                    infile.readline()
                
                # Write the rest of the file content with additional column for file name
                for line in infile:
                    outfile.write(f"{line.strip()}\t{file}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine CSV files with a specified suffix into one file.")
    parser.add_argument('-S', '--suffix', required=True, help="The suffix for the CSV files to combine.")
    parser.add_argument('-o', '--output', required=True, help="The name of the output CSV file.")
    args = parser.parse_args()
    # Record the start time for measuring execution duration
    start_time = time.time()
    combine_csv_files(args.suffix, args.output)
    # Record the end time and calculate elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time  # Time taken in seconds
    print(f"Total execution time: {elapsed_time:.2f} seconds")