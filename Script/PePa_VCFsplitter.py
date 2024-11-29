#!/usr/bin/env python3

import sys
import argparse
import math
import multiprocessing as mp
import gzip

def process_batch(input_vcf, header_lines, batch_sample_names, sample_indices):
    # Open output files for the current batch
    sample_files = {}
    try:
        # Process header lines to identify the #CHROM line and lines before it
        pre_header_lines = []
        chrom_line = ''
        for line in header_lines:
            if line.startswith('#CHROM'):
                chrom_line = line.strip()
                break
            else:
                pre_header_lines.append(line)
        
        fixed_columns = ['#CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO','FORMAT']
        # Now create the adjusted header and open the file
        for sample in batch_sample_names:
            # Open the output file (change to 'wt' if you want uncompressed output)
            f = open(f'{sample}_output.vcf', 'w')
            # Write the pre-header lines
            f.writelines(pre_header_lines)
            # Write the adjusted #CHROM line
            sample_chrom_line = '\t'.join(fixed_columns + [sample]) + '\n'
            f.write(sample_chrom_line)
            sample_files[sample] = f

        # Read the input VCF file line by line
        with gzip.open(input_vcf, 'rt') as file:
            for line in file:
                if line.startswith('#'):
                    continue  # Skip header lines
                fields = line.strip().split('\t')
                fixed_fields = fields[:9]  # Fixed columns
                sample_data = fields[9:]   # Sample-specific columns

                # Write data lines to sample files in the batch
                for sample in batch_sample_names:
                    idx = sample_indices[sample]
                    sample_line = '\t'.join(fixed_fields + [sample_data[idx]]) + '\n'
                    sample_files[sample].write(sample_line)
    finally:
        # Close all output files
        for f in sample_files.values():
            f.close()

def split_vcf(input_vcf, batch_size=100):
    # Initialize variables
    header_lines = []
    sample_names = []

    # First pass: Read the header and get sample names
    with gzip.open(input_vcf, 'rt') as file:
        for line in file:
            if line.startswith('#'):
                header_lines.append(line)
                if line.startswith('#CHROM'):
                    # Extract sample names from the header line
                    try:
                        sample_names = line.strip().split('\t')[9:]
                        if not sample_names:
                            raise ValueError("No sample names found in the #CHROM header line.")
                    except Exception as e:
                        print(f"Error parsing #CHROM line: {e}")
                        return
                    break
            else:
                # Reached data lines
                break

    num_samples = len(sample_names)
    if num_samples == 0:
        print("Error: No samples found in the input VCF.")
        return

    num_batches = math.ceil(num_samples / batch_size)

    # Prepare sample indices
    sample_indices = {sample: idx for idx, sample in enumerate(sample_names)}

    # Create batches of samples
    batches = []
    for batch_num in range(num_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, num_samples)
        batch_sample_names = sample_names[start_idx:end_idx]
        if batch_sample_names:
            batches.append((input_vcf, header_lines, batch_sample_names, sample_indices))

    if not batches:
        print("Error: No batches created. Check your batch size and input file.")
        return

    # Determine the number of processes to use
    num_processes = min(len(batches), max(1, mp.cpu_count()))
    print(f"Using {num_processes} processes for multiprocessing.")

    # Create a pool of worker processes
    with mp.Pool(processes=num_processes) as pool:
        # Start processing batches in parallel
        pool.starmap(process_batch, batches)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split a multi-sample zipped VCF file into separate VCF files for each sample.')
    parser.add_argument('-I', '--input', required=True, help='Path to the input bgzipped VCF file')
    parser.add_argument('-b', '--batch-size', type=int, default=100, help='Number of samples to process in each batch')
    
    args = parser.parse_args()
    input_vcf = args.input
    batch_size = args.batch_size
    split_vcf(input_vcf, batch_size)
