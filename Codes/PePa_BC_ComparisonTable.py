import csv
import argparse
import tempfile
import shutil
import os
import time

def parse_args():
    """
    Parse command-line arguments and display help if needed.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Process a tab-delimited file based on specified columns.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('-i', '--input', required=True, help='Input file name (tab-delimited).')
    parser.add_argument('-o', '--output', required=True, help='Base output file name (without extension). The script appends "_Transformed.csv".')
    parser.add_argument('-p', '--print_columns', required=True, 
                        help='Columns to print (1-based index). Provide as space-separated values, e.g., "1 2".')
    parser.add_argument('-t', '--target_columns', required=True, 
                        help='Target columns for comparison (1-based index). Provide as space-separated values, e.g., "3 4".')
    parser.add_argument('-c', '--compare_columns', required=True, 
                        help='Comparison columns (1-based index) for determining categories. Provide exactly two space-separated values, e.g., "7 8".')
    
    return parser.parse_args()

def main():
    args = parse_args()

    # Validate that exactly two comparison columns are provided
    compare_columns = list(map(int, args.compare_columns.split()))
    if len(compare_columns) != 2:
        print("Error: -c should specify exactly two columns.")
        sys.exit(1)

    target_columns = list(map(int, args.target_columns.split()))
    print_columns = list(map(int, args.print_columns.split()))

    output_file = f"{args.output}"

    # Extract the input file name without extension for dynamic column naming
    input_file_name = os.path.splitext(os.path.basename(args.input))[0]

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_file:
        temp_file_name = temp_file.name

    # Read and process the input file
    with open(args.input, 'r') as infile, open(temp_file_name, 'w', newline='') as outfile:
        reader = csv.reader(infile, delimiter='\t')
        writer = csv.writer(outfile, delimiter='\t')

        headers = next(reader, None)
        if headers:
            # Write headers for the selected columns and new columns for each target comparison
            selected_headers = [headers[i - 1] for i in print_columns]
            target_headers = [f"{input_file_name}_{i}" for i in target_columns]
            writer.writerow(selected_headers + target_headers)

            for row in reader:
                # Extract selected columns
                selected_values = [row[i - 1] for i in print_columns]
                
                # Initialize output for categories of each target column
                output = []

                for target_column in target_columns:
                    target_value = row[target_column - 1]
                    compare1_value = row[compare_columns[0] - 1]
                    compare2_value = row[compare_columns[1] - 1]
                    
                    # Determine the category for this target column comparison
                    if target_value == compare1_value and target_value == compare2_value:
                        output.append("BOTH")
                    elif target_value == compare1_value:
                        output.append("Ancestry1")
                    elif target_value == compare2_value:
                        output.append("Ancestry2")
                    else:
                        output.append("Unknown")
                
                writer.writerow(selected_values + output)

    # Copy the temporary file to the final output file and then remove the temporary file
    shutil.copy(temp_file_name, output_file)
    os.remove(temp_file_name)

if __name__ == "__main__":
    # Record the start time for measuring execution duration
    start_time = time.time()
    main()
    
    # Record the end time and calculate elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time  # Time taken in seconds
    print(f"Total execution time: {elapsed_time:.2f} seconds")
