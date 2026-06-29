#!/usr/bin/env python
"""
Simple script to run CA/OA analysis.
"""
import numpy as np

from process_data import process_brand

# ============================================
# CONFIGURE YOUR PATHS HERE
# ============================================

# Option 1: Set paths directly
PROJECT_DIR = r"/home/marshed/adnan_tea"  # Your project directory

category = "ca_oa"
BRAND = "CD_W"  # Brand name
DATA_FOLDER = r"/home/marshed/Downloads/Tea/CD_W"  # Folder with CSV files

# Processing parameters (adjust if needed)
lmda = 655e-9 #wave length of laser in meter (red)
#F = #focal length of the lens
#D = #beam diameter
#w0 = ((2*lmda*F)/((np.pi)*D)) #formula for beam waist.
w0 = 2.1e-5 #beam waist for the above light in meters
z0 = (np.pi)*(w0*w0)/lmda # Rayleigh range
GROUP_SIZE = 10  # Smoothing group size
Z_RANGE = (-0.03, 0.03)  # Z range in meters
SAMPLE_LENGTH = 0.0017# sample thickness in meters

# ============================================
# RUN THE ANALYSIS
# ============================================

if __name__ == "__main__":
    
    print("=" * 60)
    print("CA/OA DATA ANALYSIS PIPELINE")
    print("=" * 60)
    print(f"Brand: {BRAND}")
    print(f"Data folder: {DATA_FOLDER}")
    print(f"Rayleigh length (z0): {z0*1000:.2f} mm")
    print(f"Sample length: {SAMPLE_LENGTH*1000:.2f} mm")
    print("=" * 60)
    
    # Run processing
    results = process_brand(
        brand=BRAND,
        category=category,
        data_folder=DATA_FOLDER,
        w0=w0,
        z0=z0,
        sample_length=SAMPLE_LENGTH,
        group_size=GROUP_SIZE,
        z_range=Z_RANGE,
        project_dir=PROJECT_DIR
    )
    
    # # Optional: Save summary statistics
    # if not results.empty:
    #     summary = results[['power_mW', 'abs_delphi', 'delphi_err', 'R_sq_reg']].describe()
    #     summary.to_csv(f"{PROJECT_DIR}/processed/{BRAND}/summary_stats.csv")
    #     print("\n📊 Summary statistics saved.")
    
    print("\n✨ All done!")
    