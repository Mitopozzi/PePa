#!/bin/bash
#run using conda build START/

# Create directories in the Conda environment to hold the script and related files
mkdir -p $PREFIX/bin
mkdir -p $PREFIX/src

# Copy the main pipeline scripts to the Conda environment's bin directory
cp PePa_PaintChr.bash $PREFIX/bin
cp PePa_BaseCode.bash $PREFIX/bin

# Make the main pipeline script executable
chmod +x $PREFIX/bin/PePa_PaintChr.bash

# Copy all required Python scripts for the pipeline parts
cp "$SRC_DIR/PePa_BC_VCFtoTable.py" $PREFIX/src/
cp "$SRC_DIR/PePa_BC_ComparisonTable.py" $PREFIX/src/
cp "$SRC_DIR/PePa_BC_ClusteringSNPs.py" $PREFIX/src/
cp "$SRC_DIR/PePa_BC_ClustCombine.py" $PREFIX/src/
cp "$SRC_DIR/PePa_PC_GeneToClustRep.py" $PREFIX/src/
cp "$SRC_DIR/PePa_PC_ExtracGTF.py" $PREFIX/src/
cp "$SRC_DIR/PePa_VCFsplitter.py" $PREFIX/src/


# Copy all required R scripts for the pipeline parts
# Adjust paths if R scripts are in a subfolder (e.g., src/r)
mv "$SRC_DIR/PePa_PC_GeneCountPerc.r" $PREFIX/src/
mv "$SRC_DIR/PePa_PC_GenomePaint.r" $PREFIX/src/
mv "$SRC_DIR/PePa_PC_ntPerc.r" $PREFIX/src/


# Symlink the main pipelines to make it globally executable in the environment
ln -s $PREFIX/bin/PePa_PaintChr.bash $PREFIX/bin/pepa-paint
ln -s $PREFIX/bin/PePa_BaseCode.bash $PREFIX/bin/pepa-base

# Symlink the minor scripts to make it globally executable in the environment
ln -s $PREFIX/src/PePa_PC_ExtracGTF.py $PREFIX/src/pepa-gtf
ln -s $PREFIX/src/PePa_VCFsplitter.py $PREFIX/src/pepa-split
