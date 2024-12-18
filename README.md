# **Pedigree Painter (PePa)**

PePa is a visualization tool for genomics data that can be used to visualize which and how much of the parental genome has been inherited by the offspring. 
The pipeline generates data optimized for ggplot2, so users can create their own plots using this data. 
The R scripts in the pipeline focus on graphics, and are optimized for tens of offspring but have been tested on up to 250 samples with 30 chromosomes each. 

---

## **Description**
The script performs the following tasks:
2. Processes VCF files for SNP clustering and ancestry identification.
3. Refines clusters and makes files suitable for ancestry-based visualizations.
4. Optionally computes gene-based ancestry statistics.

---

## **Installing `PePa` via Conda**

The pipelines are written in Bash, making it easy to modify and run locally, however, it is recommended to use the program through CONDA.
The installation through CONDA checks for all the prerequisites has been tested for both clustering and visualization. The usage is described as running within a CONDA environment.
If you don’t already have Conda installed, download and install it from (eg. [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/)).
The scripts use a mix of Bash, Python, and R. Python scripts do not generate plots and use only basic modules, so it does not require the installation of any extra code. 
The output of all analyses is made suitable for ggplot2, and all plots are done using R scripts which require only three packages.  

---

## **Installation Steps**
1. **Create a Conda Environment (Optional)**:
   To keep dependencies isolated, create a dedicated environment:
   ```bash
   conda create -n pepa_env python=3.10
   conda activate pepa_env
   ```

2. **Install `PePa`**:
   Run the following command to install `PePa`:
   ```bash
   conda install mitopozzi::pepa
   ```

3. **Verify Installation**:
   Ensure the tool is installed successfully:
   ```bash
   pepa-paint -h
   ```
---

## **Usage**

Multiple commands are available in PePa, but the main pipeline can be used with the command below.

```bash
pepa-paint -i ListVCF.txt -o Results -1 Parent1.vcf -2 Parent2.vcf -c 1000 -G NCBIannotation.gtf -C 1
```

### **Required Flags**
| Flag | Description |
|------|-------------|
| `-i` | Specify a file with a list of VCF files (one VCF per sample). |
| `-o` | Specify the base name for output files. |
| `-1` | Specify the first parental VCF file for comparison (Blue). |
| `-2` | Specify the second parental VCF file for comparison (Red). |
| `-c` | Specify the clustering size for SNP regions (e.g., 100). |

### **Optional Flags**
| Flag | Description |
|------|-------------|
| `-I` | Specify a Tabulated file (generated by `pepa-table`). |
| `-G` | Specify a GTF file for annotation conversion (will be converted in .anno). |
| `-A` | Specify annotation file (.anno). |
| `-C` | Generate and plot chromosome-wide ancestry percentages (default: inactive). |
| `-h` | Display the help message and usage instructions. |

Other possible commands are below:

Perform all analyses without plotting anything. The output file `<basename>_Clustered.csv` is suitable for plotting in ggplot2.
```bash
pepa-base -i ListVCF.txt -o Results -1 Parent1.vcf -2 Parent2.vcf -c 1000
```

Perform only the conversion from VCF files to the comparison table (similar to VCFtools). The output file `<basename>_Tabulated.csv` is suitable for visual inspection of the data.
```bash
pepa-table -i ListVCF.txt -o Results -1 Parent1.vcf -2 Parent2.vcf -c 1000
```

Convert a GTF file into a .anno file. This is a more readable genome annotation format, you can see an example (S. pombe nuclear genome) in the Examples folder.
```bash
pepa-gtf -I NCBIannotation.gtf -O Results
```

This is a utility script that splits VCF files (BG-zipped) into separate, single-sample VCF files. Many other tools can perform this action, but this is especially suited for computers with limited resources
The flag -b specifies how many samples to process at the same time, making the code much slower for small values of -b .  
Smaller values of -b are suitable for low-memory computers, while high numbers are for computers with more resources. 
The output of this file can be used for  `pepa-paint` by running the command  `*.vcf > ListVCF.txt`
```bash
pepa-split -I MultiSampleVCFfile.vcf.gz -b 20
```

---
