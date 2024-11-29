# WIP Change to take only the largest 20 chromosomes
# WIP make this change so that the plot doesn't always become insane
# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
output_file <- args[2]

# List of required packages
packages <- c("dplyr", "ggplot2", "patchwork")
options(repos = c(CRAN = "https://cran.r-project.org"))

# Loop through each package to install if missing and load quietly
for (pkg in packages) {
  suppressWarnings(suppressMessages({
    if (!requireNamespace(pkg, quietly = TRUE)) {
      install.packages(pkg, quietly = TRUE)
    }
    library(pkg, character.only = TRUE, quietly = TRUE)
  }))
}


# Load required libraries
library(dplyr, quietly = T)
library(ggplot2, quietly = T)

# Read the data from the input file
df <- read.csv(input_file, sep = "\t")  # Adjust sep if necessary

# List to store plots
plot_list <- list()

# Calculate the total range for each chromosome and filter for the top X longest
top_chromosomes <- df %>%
  group_by(Chromosome) %>%
  summarise(total_length = max(End) - min(Start)) %>%
  arrange(desc(total_length)) %>%
  slice_head(n = 7) %>%
  pull(Chromosome)

# Filter the dataset to include only the top X chromosomes
df <- df %>% filter(Chromosome %in% top_chromosomes)


# Loop through each unique filename
for (file in unique(df$filename)) {
  # Filter data for the current filename
  subset_data <- subset(df, filename == file)
  
  # Conditional to check if this is the first file
  if (file == unique(df$filename)[1]) {
    # Create the plot with strip.text size 16 and bold for the first file
    p <- ggplot(subset_data, aes(xmin = Start, xmax = End, ymin = 0, ymax = 1, fill = Ancestry)) +
      geom_rect(color = "white") +  # Draw rectangles with white borders
      scale_fill_manual(values = c("blue", "red", "white")) +  # Define fill colors for bars
      scale_color_manual(values = c("blue", "red", "white")) +  # Define edge colors for bars
      theme_minimal() +  
      facet_wrap(~Chromosome, nrow=1, scales = "free_x") +
      theme(
        plot.background = element_rect(fill = "white", color = NA),      # Background color for the entire plot
        panel.background = element_rect(fill = "white", color = NA),     # Background color for the plot panel
        axis.text.y = element_blank(),            # Remove y-axis text
        axis.ticks.y = element_blank(),           # Remove y-axis ticks
        axis.text.x = element_blank(),            # Remove x-axis text
        axis.ticks.x = element_blank(),           # Remove x-axis ticks
        panel.grid = element_blank(),             # Remove grid lines
        axis.title.y = element_blank(),           # Remove y label 
        axis.title.x = element_blank(),           # Remove x label
        panel.spacing = unit(0.1, "lines"),       # Reduce space between facets
        strip.placement = "outside", 
        strip.text = element_text(size = 18, face = "bold",angle = 1),  # Bold and larger strip text for the first plot
        legend.title = element_blank(),           # Remove legend title
        legend.position = "none"                  # Hide the legend
      ) +
      # Add rotated title on the left side
      geom_text(data = subset(subset_data, Chromosome == unique(subset_data$Chromosome)[1]),
                aes(x = -Inf, y = 0.5), label = file,
                angle = 1, vjust = 0.6, hjust = 0.9, size = 6) + 
      coord_cartesian(clip = "off") +theme(plot.margin = unit(c(0, 0, 0, 3), "cm"))
    
  } else {
    # Create the plot with strip.text element_blank for other files
    p <- ggplot(subset_data, aes(xmin = Start, xmax = End, ymin = 0, ymax = 1, fill = Ancestry)) +
      geom_rect(color = "white") +  # Draw rectangles with white borders
      scale_fill_manual(values = c("blue", "red", "grey")) +  # Define fill colors for bars
      scale_color_manual(values = c("blue", "red", "grey")) +  # Define edge colors for bars
      theme_minimal() +  
      facet_wrap(~Chromosome, nrow=1, scales = "free_x") +
      theme(
        plot.background = element_rect(fill = "white", color = NA),      # Background color for the entire plot
        panel.background = element_rect(fill = "white", color = NA),     # Background color for the plot panel
        axis.text.y = element_blank(),            # Remove y-axis text
        axis.ticks.y = element_blank(),           # Remove y-axis ticks
        axis.text.x = element_blank(),            # Remove x-axis text
        axis.ticks.x = element_blank(),           # Remove x-axis ticks
        panel.grid = element_blank(),             # Remove grid lines
        axis.title.y = element_blank(),           # Remove y label 
        axis.title.x = element_blank(),           # Remove x label
        panel.spacing = unit(0.1, "lines"),       # Reduce space between facets
        strip.text = element_blank(),             # Remove strip text for other plots
        legend.title = element_blank(),           # Remove legend title
        legend.position = "none"                  # Hide the legend
      ) +
      # Add rotated title on the left side
      geom_text(data = subset(subset_data, Chromosome == unique(subset_data$Chromosome)[1]),
                aes(x = -Inf, y = 0.5),label = file,
                angle = 0.8, vjust = 0.6, hjust = 0.9, size = 6) + 
      coord_cartesian(clip = "off") +theme(plot.margin = unit(c(0, 0, 0, 2), "cm"))
    
  }
  
  # Add the plot to the list
  plot_list[[file]] <- p
}

if (length(unique(df$filename)) > 10) {
  Plots <- 0.3
} else {
  Plots <- 0.5
}

if (length(unique(df$Chromosome)) > 10) {
  Large <- 40
} else {
  Large <- 30
}

# Combine ancestry plots into a single vertical plot
ancestry_plots <- wrap_plots(plot_list, ncol = 1)

# Save each plot as a PDF in landscape orientation
png_filename <- paste(output_file, "PePa_Paint.png", sep = "_")
ggsave(png_filename, plot = ancestry_plots, width = Large, height = Plots * length(plot_list), units = "in", dpi = 300,device = "png")

print(paste('Ancestry Plot:', png_filename))
