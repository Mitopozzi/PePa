# Ensure ggplot2 is installed
if (!requireNamespace("ggplot2", quietly = TRUE)) {
  install.packages("ggplot2")
}
library(ggplot2)


# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)

# Check if arguments are provided
if (length(args) < 2) {
  stop("Please provide both input file and base name for output files.")
}

# Read command line arguments
input_file <- args[1]
base_name <- args[2]
SIZE <- args[3]
# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)

# Step 1: Read the data from a CSV file
# Read the data from the input file
data <- read.csv(input_file, stringsAsFactors = FALSE, sep = "\t")  # Adjust sep if necessary

# Step 2: Calculate the number of base pairs for each segment
data$Count <- data$End - data$Start + 1

# Step 3: Aggregate the counts by filename, Chromosome, and Ancestry
aggregated_data <- aggregate(
  Count ~ filename + Chromosome + Ancestry,
  data = data,
  sum
)

# Step 4: Calculate the total base pairs per filename and Chromosome
total_counts <- aggregate(
  Count ~ filename + Chromosome,
  data = aggregated_data,
  sum
)

# Step 5: Merge the total counts back to the aggregated data
merged_data <- merge(aggregated_data, total_counts, by = c("filename", "Chromosome"), suffixes = c("_Ancestry", "_Total"))

# Step 6: Calculate the percentage
merged_data$Percentage <- round((merged_data$Count_Ancestry / merged_data$Count_Total) * 100, 2)

# Step 7: Organize
final_results <- merged_data[, c("filename", "Chromosome", "Ancestry", "Count_Ancestry", "Percentage")]

# Rename columns 
names(final_results) <- c("Individuals", "Chromosome", "Ancestry", "Count_BP", "Percentage")

# Step 8: Remove short chromosomes
filter_results = subset(final_results,Count_BP > SIZE)

# Optional: Order the results for better readability
filter_results <- filter_results[order(filter_results$Individuals, filter_results$Chromosome, filter_results$Ancestry), ]

# Step 9: Display the results
p = ggplot(filter_results, aes(x = Chromosome, y = Percentage, color = Ancestry, fill = Ancestry)) +
  geom_bar(stat = "identity", position = "stack") +
  facet_wrap(~Individuals) +  theme_bw()  + 
  scale_fill_manual(values = c("blue", "red", 'darkgrey')) + # Define the fill for the bars 
  scale_color_manual(values = c("blue", "red", 'darkgrey')) + # Define the colors for the bars edges
  theme(strip.text.x = element_text(size = 24, face = "bold")) + 
  ylab("Percentage (%)") + xlab("Chromosomes") +
  theme(
    axis.text.x = element_text(size = 20, face = "bold"),
    axis.text.y = element_text(size = 20, face = "bold"),
    axis.title.y = element_text(size = 20, face = "bold"),
    axis.title.x = element_text(size = 20, face = "bold"),
    legend.title = element_text(size = 20, face = "bold"),
    legend.text = element_text(size = 20, face = "bold"))
# Save the plot
pdf_filename <- paste(base_name, "GenomeBarPlot.pdf", sep = "_")
ggsave(pdf_filename, plot = p, width = 20, height = 20, device = "pdf")

# Save the summary to a new CSV file
csv_file <- paste0(base_name, "_GenomePercentage.csv") # Output file for the summary data
write.csv(filter_results, csv_file, row.names = FALSE)
