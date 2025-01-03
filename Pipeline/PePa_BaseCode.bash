#!/bin/bash

# Check the Python version
python_version=$(python --version 2>&1)

# Extract the version number
version_number=$(echo $python_version | awk '{print $2}')

# Check if the version starts with "3."
if [[ $version_number == 3.* ]]; then
    :
else
    echo "Python 3 is required. Installed version: $version_number"
fi

#Make path relative to the starting position (bin for pipeline and src for python scripts)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
script_path="$(cd "$SCRIPT_DIR/../src/" && pwd)"

# Function to display usage information
usage() {
    echo "Usage: $0 -i ListVCF.txt -o Results -1 Parent1.vcf -2 Parent2.vcf -c 100"
    echo ""
    echo "Required Flags:"
    echo ""
    echo "  -i    Specify a file with a list of VCF files (one for each sample)"
    echo "  -o    Specify the base name to generate output files"
    echo "  -1    Specify the first target VCF file for comparison."
    echo "  -2    Specify the second target VCF file for comparison."
    echo "  -c    Clustering size to generate regions from SNPs (eg. 100)"
    echo ""
    echo "Optional Flags:"
    echo ""
    echo "  -I    Specify a file with a Comparison table (generated by pepa-table)"
    echo ""
    echo "  -h    Display this help message."
    exit 1
}

# Default value for the A, G and C flags
GRAPH=""
GTF=""
ANNO=""

# Parse command-line arguments using getopts
while getopts ":i:I:o:1:2:G:A:c:C:h" opt; do
    case $opt in
        i )
            if [[ $OUTPUT0 == true ]]; then
                echo "Error: -i and -I flags cannot be used together."
				echo ""
                usage
            fi
            input_file="$OPTARG"
            ;;
        I )
            if [[ $input_file == true ]]; then
                echo "Error: -i and -I flags cannot be used together."
				echo ""
                usage
            fi
            OUTPUT0="$OPTARG"
        ;;
        o) output_file_base="${OPTARG}"
        ;;
        1) TARGET1="$OPTARG"
        ;;
        2) TARGET2="$OPTARG"
        ;;
        G )
            if [[ $ANNO == true ]]; then
                echo "Error: -G and -A flags cannot be used together."
				echo ""
                usage
            fi
            GTF="$OPTARG"
            ;;
        A )
            if [[ $GTF == true ]]; then
                echo "Error: -G and -A flags cannot be used together."
				echo ""
                usage
            fi
            ANNO="$OPTARG"
        ;;
		c) CSIZE="$OPTARG"
        ;;
        h) usage
           exit 0
           ;;
        \?) echo "Invalid option: -$OPTARG" >&2
            usage
            exit 1
            ;;
        :) echo "Option -$OPTARG requires an argument." >&2
           usage
           exit 1
           ;;
    esac
done

# Check if the input files exist
if [ -z "$input_file" ]; then
    echo "Error: List file $input_file does not exist."
	echo "You can generate this file by doing 'find *.vcf.gz > List.txt'"
	echo ""
	usage
    exit 1
fi

if [[ -n "$input_file" && -n "$OUTPUT0" ]]; then
    echo "Error: List file -i or comparison table -I do not exist."
	echo "You can generate -i by doing 'find *.vcf.gz > List.txt'"
	echo ""
	usage
    exit 
fi


if [ -z  "$TARGET1" ]; then
    echo "Error: Parental vcf file $TARGET1 does not exist."
	echo ""
	usage
    exit 1
fi
if [ -z "$TARGET2" ]; then
    echo "Error: Parental vcf file $TARGET2 does not exist."
	echo ""
	usage
    exit 1
fi
if [ -z  "$CSIZE" ]; then
    echo "Error: The size of the regions was not specified"
	echo ""
	usage
    exit 1
fi

# Determinate the number of files
file_length=$(wc -l < "$input_file")

# Debugging
echo "Input info:"
echo "List of VCF files to analyze: $input_file"
echo "Number of individuals analyzed: $file_length"
echo "Base name for the file output: $output_file_base"
echo "Parent/Ancestry N.1: $TARGET1"
echo "Parent/Ancestry N.2: $TARGET2"
echo "Clustering size: $CSIZE"
echo ""

if [ -n "$input_file" ]; then
	# Create a temporary output file
	OUTPUT000=$(mktemp)

	# Part 0: Prepare the data from genome painting
	echo "Running Part 0: Generating a tabulate version of VCF files provided..."
	# Call a Python script for processing using TARGET1 and TARGET2
	python "${script_path}/PePa_BC_VCFtoTable.py" -L "$input_file" -P1 "$TARGET1" -P2 "$TARGET2" -O "$OUTPUT000"
	echo "Part 0: Complete"
	echo ""

	OUTPUT0=$(mktemp)
	TABULATED="${output_file_base}_Tabulated.csv"

	sed 's/.vcf.gz//g' $OUTPUT000 | sed 's/-/0/g' | tr ',' '\t' > $OUTPUT0
	sed 's/.vcf.gz//g' $OUTPUT000 | sed 's/-/0/g' | tr ',' '\t' > $TABULATED

fi

# Get unique chromosome names (first column) and store them in $chromosomes
chromosomes0=$(awk 'NR>1 {print $1}' "$OUTPUT0" | sort -u)
chromosomes=$(awk 'NR>1 {print $1}' "$OUTPUT0" | sort | uniq -c | awk '$1 > 200 {print $2}')

# Get the number of columns in the first row using cut and wc
num_columns=$(head -n 1 "$OUTPUT0" | tr '\t' '\n' | wc -l)

# Generate the list of column numbers from 6 to the total number of columns
# The columns 1 is Chromosomes, 2 is Position, 3 is Reference, 4 is Parent1 (TARGET1), 5 is Parent2 (TARGET2)
# From 6 onward are individuals (each VCF file in -L) under analysis
columns=$(seq 6 "$num_columns")

# Prepare grep pattern by converting the chromosome list to a space-separated string
grep_pattern=$(echo "$chromosomes" | tr '\n' ' ')
# Prepare target columns by converting the column numbers to a space-separated string
target_columns=$(echo "$columns" | tr '\n' ' ')

# Fixed parameters
print_columns="1 2"
compare_columns="4 5"

# Part 1: Run the first script
OUTPUT1=$(mktemp)
FILT1="${output_file_base}_Transformed.csv"

echo "Running Part 1: Transforming Tabulated VCF file into Comparison File"
python "${script_path}/PePa_BC_ComparisonTable.py" -i "$OUTPUT0" -o "$OUTPUT1" -p "$print_columns" -t "$target_columns" -c "$compare_columns" 
echo "Part 1: Complete"
grep -v -e BOTH $OUTPUT1 > $FILT1
echo ""

# Part 2: Run the Second script
echo "Running Part 2: Clustering SNPs into ancestry regions"
python "${script_path}/PePa_BC_ClusteringSNPs.py" "$FILT1" "$output_file_base"  -CLUSTER "$CSIZE"
echo "Part 2: Complete"
echo ""

# Part 3: Run the Third script
OUTPUT3=$(mktemp)
SUFFIX="_CLUST_"
FILT3="${output_file_base}_ClusteredRaw.csv"
echo "Running Part 3: Combining clustering files from Individuals to a single file"
python "${script_path}/PePa_BC_ClustCombine.py" -S "$SUFFIX" -o "$OUTPUT3"

sed 's/_CLUST_Individual//g' $OUTPUT3 | sed 's/.csv//g' > $FILT3

REFINE="${output_file_base}_Clustered.csv"
SEL=$((CSIZE * 10))

echo "Refining clusters.."
echo "To generate ancestry blocks, clusters of the following size will be ignored:" "$SEL"
python "${script_path}/PePa_BC_ClusterClusters.py" -I "$FILT3" -O "$REFINE"  -N "$SEL"

echo "Part 3: Complete"
echo ""


# zipping files to clean not clutter the folder
ZIPPED="${output_file_base}_Clusters.zip"
zip -m -q $ZIPPED *_CLUST_*.csv
