import csv
import argparse
import os
from collections import defaultdict

def read_csv(file_path, delimiter='\t'):
    """
    Reads a CSV file with a specified delimiter and returns its contents as a list of dictionaries.
    
    Parameters:
    file_path (str): Path to the CSV file.
    delimiter (str): Delimiter used in the CSV file (default is tab).
    
    Returns:
    list of dict: List of rows, where each row is represented as a dictionary.
    """
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        return list(reader)

def write_csv(file_path, data, fieldnames, delimiter='\t'):
    """
    Writes a list of dictionaries to a CSV file with a specified delimiter.
    
    Parameters:
    file_path (str): Path to the output CSV file.
    data (list of dict): Data to write to the file.
    fieldnames (list of str): List of field names for the CSV header.
    delimiter (str): Delimiter used in the CSV file (default is tab).
    """
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)

def assign_ancestry(gene_data, ancestry_data):
    """
    Assigns Ancestry to Gene IDs based on overlap with ancestry regions.
    If no matching ancestry is found, assigns 'Unknown'.

    Parameters:
    gene_data (list of dict): List of gene data dictionaries.
    ancestry_data (list of dict): List of ancestry data dictionaries.
    
    Returns:
    list of dict: Gene data with an additional 'Ancestry' field.
    """
    # Convert ancestry data to a more accessible format
    ancestry_dict = defaultdict(list)
    for entry in ancestry_data:
        chrom = entry['Chromosome']
        start = int(entry['Start'])
        end = int(entry['End'])
        ancestry = entry['Ancestry']
        ancestry_dict[chrom].append((start, end, ancestry))
    
    # Process gene data
    for gene in gene_data:
        gene_chr = gene['Sequence Name']
        gene_start = int(gene['Start'])
        gene_end = int(gene['End'])
        
        # Find overlapping ancestry regions
        assigned = False
        if gene_chr in ancestry_dict:
            for (start, end, ancestry) in ancestry_dict[gene_chr]:
                if start <= gene_end and end >= gene_start:
                    gene['Ancestry'] = ancestry
                    assigned = True
                    break  # Assuming we want the first matching ancestry
        
        if not assigned:
            gene['Ancestry'] = 'Unknown'
    
    return gene_data

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Assign ancestry to gene IDs based on overlap with ancestry regions and concatenate results.")
    parser.add_argument('-g', '--gene', required=True, help="Path to the gene data CSV file.")
    parser.add_argument('-a', '--ancestry', required=True, help="Path to the ancestry data CSV file.")
    parser.add_argument('-o', '--output', required=True, help="Path to the concatenated output CSV file.")
    
    args = parser.parse_args()
    
    # Read input files
    gene_data = read_csv(args.gene)
    ancestry_data = read_csv(args.ancestry)
    
    # Get unique names from the 'filename' column in ancestry data
    unique_names = set(row['filename'] for row in ancestry_data if 'filename' in row)
    
    # Temporary file paths to store individual CSV files
    temp_files = []
    
    # Process each unique name in ancestry data
    for name in unique_names:
        filtered_ancestry_data = [row for row in ancestry_data if row['filename'] == name]
        
        # Assign ancestry to gene data
        result_data = assign_ancestry(gene_data, filtered_ancestry_data)
        
        # Add new column 'FileName' with the name of the file
        for row in result_data:
            row['FileName'] = name
        
        # Define temporary output file path for each unique name
        temp_file_path = f"{args.output}_{name}.csv"
        temp_files.append(temp_file_path)
        
        # Define fieldnames including the new 'FileName' column
        fieldnames = list(result_data[0].keys()) if result_data else []
        
        # Save result to a temporary CSV file
        write_csv(temp_file_path, result_data, fieldnames)
    
    # Concatenate all temporary CSV files into one
    with open(args.output, 'w', newline='') as outfile:
        writer = None
        for file_name in temp_files:
            with open(file_name, 'r') as infile:
                reader = csv.reader(infile, delimiter='\t')
                headers = next(reader)  # Read header from the first file
                if writer is None:
                    # Create writer and write header
                    writer = csv.writer(outfile, delimiter='\t')
                    writer.writerow(headers)
                # Write the remaining rows
                for row in reader:
                    writer.writerow(row)
    
    # Remove temporary files
    for file_name in temp_files:
        os.remove(file_name)

if __name__ == '__main__':
    main()
