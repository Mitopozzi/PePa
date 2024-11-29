import csv
import argparse
import re

def extract_genes_from_gtf(input_file, output_file):
    """
    Extracts unique genes from a GTF file and writes the relevant fields to an output file.
    
    Parameters:
    input_file (str): Path to the input GTF file.
    output_file (str): Path to the output file where extracted data will be saved.
    """
    genes = set()
    
    # Regular expression for parsing attributes
    attr_pattern = re.compile(r'(\S+)\s+"([^"]+)"')

    with open(input_file, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        for row in reader:
            if len(row) < 9:
                continue  # Skip malformed lines
            
            seq_name, source, feature_type, start, end, score, strand, frame, attributes = row
            
            if feature_type == 'gene':
                # Extract gene attributes
                attributes_dict = dict(attr_pattern.findall(attributes))
                gene_id = attributes_dict.get('gene_id', 'Unknown')
                
                # Collect unique gene entries
                genes.add((seq_name, start, end, strand, feature_type, gene_id))
    
    # Write the extracted genes to the output file
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(['Sequence Name', 'Start', 'End', 'Strand', 'Feature Type', 'Gene ID'])
        for gene in sorted(genes, key=lambda x: (x[0], int(x[1]))):  # Sort by sequence name and start position
            writer.writerow(gene)

def main():
    parser = argparse.ArgumentParser(description='Extract genes from a GTF file.')
    parser.add_argument('-I', '--input', required=True, help='Path to the input GTF file.')
    parser.add_argument('-O', '--output', required=True, help='Path to the output file.')
    
    args = parser.parse_args()
    
    extract_genes_from_gtf(args.input, args.output)

if __name__ == '__main__':
    main()
