# **Example Commands to Run *pepa***

The example files can be run using the following commands:

## *1. For Chromosome Painting:*
```bash
pepa-paint -i List.txt -o Pombe -1 EBC091.vcf.gz -2 EBC411.vcf.gz -c 100 -A Annotation.anno -C 1
```
## *2. To generate only tables:*
```bash
pepa-base -i List.txt -o Pombe -1 EBC091.vcf.gz -2 EBC411.vcf.gz -c 100
```

Please use the file *_Clustered.csv if you want to make your custom plot through ggplot2 in R.
