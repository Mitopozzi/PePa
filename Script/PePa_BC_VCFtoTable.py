#!/usr/bin/env python3

import gzip
import sys
import time
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import os
import tempfile
import csv
import glob

def extract_variants(vcf_file, apply_filter):
    """
    Extracts variants from a VCF file and writes them to a temporary CSV file.

    This function reads the given VCF file line by line, extracts relevant variants,
    and writes them to a temporary CSV file to minimize memory usage.

    Args:
        vcf_file (str): Path to the VCF file (either compressed or uncompressed).
        apply_filter (bool): Whether to filter out variants that did not pass the filter.

    Returns:
        str: Path to the temporary file containing the extracted variants.
    """
    # Determine whether the file is gzipped based on the file extension and open accordingly
    open_func = gzip.open if vcf_file.endswith('.gz') else open

    # Create a temporary file to store the variants
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', suffix=".tmp")
    temp_writer = csv.writer(temp_file)

    # Write a header row
    temp_writer.writerow(["Chromosome", "Position", "Ref", "Alt", "File"])

    # Open the VCF file and read line by line
    with open_func(vcf_file, 'rt') as file:
        for line in file:
            if line.startswith("#"):
                continue  # Skip header lines

            # Split the line into fields based on tab ('\t') separation
            parts = line.strip().split('\t')
            # Ensure that there are enough fields to avoid IndexError
            if len(parts) < 10:
                continue  # Skip malformed lines

            chrom, pos, ref, alt, filter_info, genotype_info = (
                parts[0], parts[1], parts[3], parts[4], parts[6], parts[9]
            )

            # Extract the genotype field from the genotype_info
            genotype = genotype_info.split(':')[0]

            # Skip heterozygous SNPs (e.g., '0/1', '1/0')
            if genotype in ['0/1', '1/0']:
                continue

            # Only include variants based on the filter flag
            if apply_filter:
                if filter_info == "PASS" and './.' not in genotype_info and ref != alt:
                    temp_writer.writerow([chrom, pos, ref, alt, vcf_file])
            else:
                if './.' not in genotype_info and ref != alt:
                    temp_writer.writerow([chrom, pos, ref, alt, vcf_file])

    temp_file.close()  # Close the temporary file
    return temp_file.name  # Return the path to the temporary file

def write_organized_output(temp_files, output_file, all_files):
    """
    Aggregates all partial results from temporary files into a single output file.

    Args:
        temp_files (list): List of paths to temporary files containing partial results.
        output_file (str): Path to the output file where differences will be written.
        all_files (list): List of all VCF files for the header.
    """
    # Create a dictionary to hold the combined variant data
    variant_data = defaultdict(dict)

    # Build a mapping from temp file to original file name
    temp_file_to_vcf = {}
    for temp_file in temp_files:
        # Extract the original VCF file name from the temp file data
        with open(temp_file, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            try:
                first_row = next(reader)
                vcf_file = first_row[4]  # The original VCF file name
                temp_file_to_vcf[temp_file] = vcf_file
            except StopIteration:
                # Empty temp file
                temp_file_to_vcf[temp_file] = None

    # Read each temp file and populate variant_data
    for temp_file in temp_files:
        vcf_file = temp_file_to_vcf[temp_file]
        if vcf_file is None:
            continue  # Skip empty temp files
        with open(temp_file, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                chrom, pos, ref, alt, _ = row
                key = (chrom, pos, ref)
                variant_data[key][vcf_file] = alt
        # Remove the temp file
        os.remove(temp_file)

    # Write the organized output
    with open(output_file, 'w', newline='') as out:
        writer = csv.writer(out)
        # Write the header
        writer.writerow(["Chromosome", "Position", "Ref"] + all_files)
        # Sort the keys for consistent output
        for key in sorted(variant_data.keys(), key=lambda x: (x[0], int(x[1]))):
            chrom, pos, ref = key
            # Get the alt values for each file, or '-' if the file doesn't have this variant
            alt_values = [variant_data[key].get(vcf_file, '-') for vcf_file in all_files]
            writer.writerow([chrom, pos, ref] + alt_values)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Compare a list of VCF files to two target VCF files and organize the output.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Define the arguments (flags) to be passed in
    parser.add_argument('-L', '--list', required=True, help="Path to a file containing a list of VCF files to compare.")
    parser.add_argument('-P1', '--target1', required=True, help="Path to the first target VCF file (P1) to compare against.")
    parser.add_argument('-P2', '--target2', required=True, help="Path to the second target VCF file (P2) to compare against.")
    parser.add_argument('-O', '--output', required=True, help="Path to the output file where differences will be written.")
    parser.add_argument('-FILTER', action='store_true', help="Only include variants that passed the filter (PASS).")

    # Parse the arguments
    args = parser.parse_args()

    # Read the list of VCF files from the file provided with the -L flag
    with open(args.list, 'r') as file_list:
        vcf_files = [line.strip() for line in file_list if line.strip()]

    # Record the start time for measuring execution duration
    start_time = time.time()

    # List to store paths of temporary files
    temp_files = []

    # Collect all file names for the header
    all_files = [args.target1, args.target2] + vcf_files

    # Determine the optimal number of workers, using half of available CPUs for safety
    max_workers = min(len(vcf_files), max(1, os.cpu_count()//2))

    # Use ThreadPoolExecutor to process the VCF files in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit the target VCF files for processing
        future_p1 = executor.submit(extract_variants, args.target1, args.FILTER)
        future_p2 = executor.submit(extract_variants, args.target2, args.FILTER)

        # Submit each file in the list for processing in parallel
        future_vcfs = {executor.submit(extract_variants, vcf_file, args.FILTER): vcf_file for vcf_file in vcf_files}

        # Collect the temporary file paths
        temp_files.append(future_p1.result())
        temp_files.append(future_p2.result())

        for future in future_vcfs:
            temp_file = future.result()
            temp_files.append(temp_file)

    # Now, aggregate the temporary files
    write_organized_output(temp_files, args.output, all_files)

    # Record the end time and calculate elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time  # Time taken in seconds

    # Output the total execution time to the console
    print(f"Total execution time: {elapsed_time:.2f} seconds")
