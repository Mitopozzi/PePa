#!/usr/bin/env python3

import sys
import argparse

def parse_arguments():
    """
    Parses command-line arguments provided by the user.

    Returns:
        args: An object containing the input file, output file, and length threshold N.
    """
    parser = argparse.ArgumentParser(
        description='Combines consecutive clusters with the same ancestry.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-I', '--input', required=True,
                        help='Path to the input file.')
    parser.add_argument('-O', '--output', default='combined_clusters.txt',
                        help='Path to the output file (default: combined_clusters.txt).')
    parser.add_argument('-N', '--threshold', required=True, type=int,
                        help='Length threshold N to ignore clusters.')

    args = parser.parse_args()
    return args

def read_input_file(input_file):
    """
    Reads the input file and stores the cluster data.

    Parameters:
        input_file (str): Path to the input file.

    Returns:
        clusters (list): A list of dictionaries containing cluster data.
    """
    clusters = []

    try:
        with open(input_file, 'r') as file:
            # Read the header line and split into column names
            header_line = file.readline().strip()
            header = header_line.split('\t')

            # Verify that required columns are present
            required_columns = {'Chromosome', 'Start', 'End', 'Ancestry', 'filename'}
            if not required_columns.issubset(set(header)):
                print("Error: Input file must contain 'Chromosome', 'Start', 'End', 'Ancestry', and 'filename' columns.")
                sys.exit(1)

            # Get the indices of the required columns
            col_indices = {col: idx for idx, col in enumerate(header)}

            # Process each line in the file
            for line_num, line in enumerate(file, start=2):
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                # Split the line into columns based on tab delimiter
                columns = line.split('\t')

                # Ensure the line has enough columns
                if len(columns) < len(header):
                    continue  # Skip lines with insufficient columns

                # Extract required data
                cluster = {
                    'Chromosome': columns[col_indices['Chromosome']],
                    'Start': int(columns[col_indices['Start']]),
                    'End': int(columns[col_indices['End']]),
                    'Ancestry': columns[col_indices['Ancestry']],
                    'filename': columns[col_indices['filename']],
                    'Length': int(columns[col_indices['End']]) - int(columns[col_indices['Start']])
                }

                clusters.append(cluster)

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        sys.exit(1)

    return clusters

def combine_clusters(clusters, N):
    """
    Combines consecutive clusters with the same ancestry, ignoring clusters of different ancestry
    if their length is less than N.

    Parameters:
        clusters (list): List of cluster dictionaries.
        N (int): Length threshold to ignore clusters.

    Returns:
        combined_clusters (list): List of combined cluster dictionaries.
    """
    combined_clusters = []

    if not clusters:
        return combined_clusters

    # Sort clusters first by filename, then by Chromosome, then by Start position
    clusters.sort(key=lambda x: (x['filename'], x['Chromosome'], x['Start']))

    i = 0
    total_clusters = len(clusters)

    while i < total_clusters:
        current_cluster = clusters[i]
        current_ancestry = current_cluster['Ancestry']
        current_chromosome = current_cluster['Chromosome']
        current_filename = current_cluster['filename']
        combined_start = current_cluster['Start']
        combined_end = current_cluster['End']

        j = i + 1
        while j < total_clusters:
            next_cluster = clusters[j]
            length = next_cluster['Length']

            # Check if the next cluster is on the same filename and chromosome
            if (next_cluster['filename'] != current_filename or
                next_cluster['Chromosome'] != current_chromosome):
                break

            if next_cluster['Ancestry'] == current_ancestry:
                # Same ancestry, combine clusters
                combined_end = next_cluster['End']
                j += 1
            else:
                if length < N:
                    # Ignore the cluster and continue
                    j += 1
                else:
                    # Different ancestry and length >= N, stop combining
                    break

        # Add the combined cluster to the list
        combined_cluster = {
            'Chromosome': current_chromosome,
            'Start': combined_start,
            'End': combined_end,
            'Ancestry': current_ancestry,
            'filename': current_filename
        }
        combined_clusters.append(combined_cluster)

        # Move to the next cluster to start a new combination
        i = j

    return combined_clusters

def write_output(combined_clusters, output_file):
    """
    Writes the combined clusters to the output file.

    Parameters:
        combined_clusters (list): List of combined cluster dictionaries.
        output_file (str): Path to the output file.
    """
    try:
        with open(output_file, 'w') as file:
            # Write the header
            file.write('Chromosome\tStart\tEnd\tAncestry\tfilename\n')

            # Write each combined cluster
            for cluster in combined_clusters:
                file.write(f"{cluster['Chromosome']}\t{cluster['Start']}\t{cluster['End']}\t{cluster['Ancestry']}\t{cluster['filename']}\n")
            print(f"Refined clusters written in: '{output_file}'")
    except IOError:
        print(f"Error: Unable to write to the file '{output_file}'.")
        sys.exit(1)

def main():
    """
    The main function that orchestrates the combining of clusters.
    """
    # Parse command-line arguments
    args = parse_arguments()
    input_file = args.input
    output_file = args.output
    N = args.threshold

    # Read clusters from the input file
    clusters = read_input_file(input_file)

    # Combine clusters based on the given criteria
    combined_clusters = combine_clusters(clusters, N)

    # Write the results to the output file
    write_output(combined_clusters, output_file)

if __name__ == '__main__':
    main()
