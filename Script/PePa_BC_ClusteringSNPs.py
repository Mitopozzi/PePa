#!/usr/bin/env python3

import csv
import sys
import tempfile
import os
import argparse
import time

def main(input_file, output_file_base, cluster_size):
    # Check if the input and output file names are provided
    if not input_file or not output_file_base:
        print("Usage: script.py input_file output_file_base -CLUSTER cluster_size")
        sys.exit(1)

    # Create a temporary file for sorted data
    with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_file:
        temp_file_name = temp_file.name

    # Read the input file and determine the number of columns
    with open(input_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader, None)
        num_columns = len(headers)
        
        # Sort the data by columns 1 and 2
        data = sorted(reader, key=lambda row: (row[0], int(row[1])))

    # Write sorted data to the temporary file
    with open(temp_file_name, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(data)

    name = 1

    # Process each column (skipping columns 1 and 2)
    for col in range(2, num_columns):
        output_file = f"{output_file_base}_CLUST_Individual{name}.csv"
        name += 1

        # Read the sorted data from the temporary file
        with open(temp_file_name, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader, None)  # Skip header
            
            # Initialize variables
            prev_chrom = None
            prev_ancestry = None
            start = None
            end = None
            result = []

            # Process the data
            for row in reader:
                chrom, pos, ancestry = row[0], int(row[1]), row[col]

                if prev_chrom == chrom and prev_ancestry == ancestry:
                    end = pos  # Update end position for the current cluster
                else:
                    if prev_chrom is not None and end - start + 1 >= cluster_size:
                        result.append([prev_chrom, start, end, prev_ancestry])
                    start = pos  # Start a new cluster
                    end = pos
                    prev_chrom = chrom
                    prev_ancestry = ancestry

            # Add the last cluster if valid
            if prev_chrom is not None and end - start + 1 >= cluster_size:
                result.append([prev_chrom, start, end, prev_ancestry])

        # Write results to output file
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(["Chromosome", "Start", "End", "Ancestry"])
            writer.writerows(result)

    # Clean up the temporary file
    os.remove(temp_file_name)

    print(f"Clustering performed for Individuals in {name - 1} columns")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and cluster data from an input file.')
    parser.add_argument('input_file', help='Path to the input file')
    parser.add_argument('output_file_base', help='Base name for the output files')
    parser.add_argument('-CLUSTER', type=int, required=True, help='Size of the clusters')
    # Record the start time for measuring execution duration
    start_time = time.time()
    
    args = parser.parse_args()

    main(args.input_file, args.output_file_base, args.CLUSTER)
    # Record the end time and calculate elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time  # Time taken in seconds
    print(f"Total execution time: {elapsed_time:.2f} seconds")