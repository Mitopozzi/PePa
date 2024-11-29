# Function to check and install missing packages quietly
check_and_install_packages <- function(packages) {
  for (pkg in packages) {
    if (!require(pkg, character.only = TRUE)) {
      install.packages(pkg, dependencies = TRUE, quiet = TRUE)
      library(pkg, character.only = TRUE, quietly = TRUE)
    }
  }
}

# List of required packages
required_packages <- c("dplyr", "tidyr", "ggplot2")

# Check and install packages quietly
check_and_install_packages(required_packages)

# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)

# Check if arguments are provided
if (length(args) < 2) {
  stop("Please provide both input file and base name for output files.")
}

# Read command line arguments
input_file <- args[1]
base_name <- args[2]

# Read the input data
data <- read.csv(input_file, sep = '\t', stringsAsFactors = FALSE)

# Process the data
summary_data <- data %>%
  group_by(Sequence.Name, FileName, Ancestry) %>%
  summarise(Count = n(), .groups = 'drop') %>%
  group_by(Sequence.Name, FileName) %>%
  mutate(Percentage = (Count / sum(Count)) * 100) %>%
  arrange(Sequence.Name, FileName, Ancestry)

# Rename columns
colnames(summary_data) <- c("Chromosome", "Individual", "Ancestry", "Count", "Percentage")

# Plot the data
p = ggplot(summary_data, aes(x = Chromosome, y = Percentage, color = Ancestry, fill = Ancestry)) +
  geom_bar(stat = "identity", position = "stack") +
  facet_wrap(~Individual) +  theme_bw()  + 
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
pdf_filename <- paste(base_name, "GeneBarPlot.pdf", sep = "_")
ggsave(pdf_filename, plot = p, width = 20, height = 20, device = "pdf")

# Save the summary to a new CSV file
csv_file <- paste0(base_name, "_GeneAncPerc.csv") # Output file for the summary data
write.csv(summary_data, csv_file, row.names = FALSE)

