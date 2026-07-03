# Z-Scan Data Analysis Pipeline

## Table of Contents
1. [Introduction](#1-introduction)
2. [Directory Structure](#2-directory-structure)
3. [Prerequisites](#3-prerequisites)
4. [Installation](#4-installation)
5. [How to Use](#5-how-to-use)
6. [File Structure Explained](#6-file-structure-explained)
7. [Output Files](#7-output-files)
8. [Troubleshooting](#8-troubleshooting)
9. [Customization Guide](#9-customization-guide)
10. [License & Acknowledgments](#10-license--acknowledgments)

---

## 1. Introduction

### 1.1 What is this Project?

This project is a **Python-based data analysis pipeline** for processing **Z-scan experimental data**. The Z-scan technique is a widely used method in nonlinear optics to measure the nonlinear refractive index and absorption coefficient of materials.

### 1.2 What Does It Do?

The pipeline takes raw CSV files containing `ca` (closed aperture) and `oa` (open aperture) data and performs:

1. **Data Loading** – Reads CSV files from your folder structure
2. **Normalization** – Normalizes CA and OA signals using baseline averaging
3. **Position Transformation** – Converts raw indices to physical Z-positions
4. **Smoothing** – Reduces noise using bin averaging with error estimation
5. **Curve Fitting** – Fits theoretical Z-scan formula to extract `Δφ` (phase shift)
6. **Visualization** – Generates individual plots and multi-page PDF reports
7. **Export** – Saves processed data, results, and statistics to CSV

### 1.3 Key Features

- ✅ **Batch Processing** – Process hundreds of files automatically
- ✅ **Error Estimation** – Each data point has standard deviation (error bars)
- ✅ **Multi-Page PDF Reports** – All plots organized in a single PDF
- ✅ **Structured Output** – Organized folders for original, processed, and graph data
- ✅ **Customizable** – Easy to adjust parameters for different experiments
- ✅ **Detailed Statistics** – R², RMSE, MAE, chi-squared, and more

---

## 2. Directory Structure

### 2.1 Project Structure

```
project/
├── data/
│   └── {brand_name}/
│       ├── 185.csv               # Original data saved (optional)
│       ├── 186.csv
│       └── ...
├── processed/
│   └── {brand_name}/
│       ├── 185(144.56mW).csv     # Processed data with errors
│       ├── 186(145.23mW).csv
│       ├── {brand_name}_results.csv  # Summary of all results
│       └── {brand_name}_analysis.pdf # Multi-page PDF report
├── graph/
│   └── {brand_name}/
│       ├── 185(144.56mW).png     # Individual plots
│       ├── 186(145.23mW).png
│       └── ...
├── logs/
│   └── {brand_name}_analysis.log # Processing logs
├── select_file.py                # File loading module
├── file_process.py               # Core processing functions
├── z_formulae.py                 # Z-scan theoretical formulas
├── process_data.py               # Main pipeline
├── run_analysis.py               # Configuration & execution
└── README.md                     # This file
```

### 2.2 Input Data Format

Your raw CSV files should be named like:
```
{number}_ca_oa.csv
```

Example: `185_ca_oa.csv`, `186_ca_oa.csv`, etc.

Each CSV should contain at least two columns (CA and OA data), with no header row.

---

## 3. Prerequisites

### 3.1 Required Python Packages

```bash
pip install numpy pandas matplotlib scipy scikit-learn
```

| Package | Version | Purpose |
|---------|---------|---------|
| `numpy` | ≥1.20.0 | Numerical operations |
| `pandas` | ≥1.3.0 | Data manipulation |
| `matplotlib` | ≥3.4.0 | Plotting and visualization |
| `scipy` | ≥1.7.0 | Curve fitting and optimization |
| `scikit-learn` | ≥0.24.0 | R² score calculation |

### 3.2 System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for large datasets)
- 500MB free disk space for output files

---

## 4. Installation

### 4.1 Clone or Download

```bash
# If using git
git clone https://your-repository-url.git
cd your-project-folder

# Or just copy all .py files to your project directory
```

### 4.2 Verify Installation

```python
python -c "import numpy, pandas, matplotlib, scipy, sklearn; print('All packages installed successfully!')"
```

### 4.3 Set Up Directory Structure

The script will automatically create the necessary directories when you run it. However, you can pre-create them:

```bash
mkdir -p data/{brand_name}
mkdir -p processed/{brand_name}
mkdir -p graph/{brand_name}
mkdir -p logs
```

---

## 5. How to Use

### 5.1 Quick Start (For Beginners)

**Step 1:** Place your CSV files in a folder (e.g., `/path/to/your/data/`)

**Step 2:** Open `run_analysis.py` and edit these lines:

```python
PROJECT_DIR = r"/home/yourname/project"  # Your project directory
BRAND = "your_brand_name"                # e.g., "calcirol"
DATA_FOLDER = r"/path/to/your/data"      # Folder with CSV files
```

**Step 3:** Adjust physical parameters:

```python
lmda = 655e-9          # Laser wavelength in meters
w0 = 1.81e-5           # Beam waist in meters
SAMPLE_LENGTH = 0.0017 # Sample thickness in meters (set to None for thin medium)
```

**Step 4:** Run the analysis:

```bash
python run_analysis.py
```

**Step 5:** Check your outputs:

- Processed data: `processed/{brand}/`
- Plots: `graph/{brand}/`
- Results summary: `processed/{brand}/{brand}_results.csv`
- PDF report: `processed/{brand}/{brand}_analysis.pdf`

### 5.2 Advanced Usage (For Power Users)

#### Customizing Parameters

You can modify these parameters in `run_analysis.py`:

```python
# Processing parameters
GROUP_SIZE = 10        # Number of points per bin for smoothing
Z_RANGE = (-0.03, 0.03)  # Z-range for filtering in meters
SAMPLE_LENGTH = 0.0017   # Sample thickness (None = thin medium)

# Physical parameters
lmda = 655e-9          # Wavelength
w0 = 1.81e-5           # Beam waist
z0 = np.pi * w0**2 / lmda  # Rayleigh length (auto-calculated)
```

#### Processing Multiple Brands

Create a batch script:

```python
# batch_run.py
from process_data import process_brand

brands = {
    'calcirol': '/path/to/calcirol/data',
    'aristo_d3': '/path/to/aristo/data',
    'other_brand': '/path/to/other/data'
}

for brand, folder in brands.items():
    print(f"\n{'='*60}")
    print(f"Processing: {brand}")
    print('='*60)
    
    results = process_brand(
        brand=brand,
        data_folder=folder,
        category='ca_oa',
        w0=1.81e-5,
        z0=0.00157,
        sample_length=0.0017,
        group_size=10,
        z_range=(-0.03, 0.03),
        project_dir="/home/yourname/project"
    )
```

#### Command Line Arguments

Add argument parsing to `run_analysis.py`:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--brand', type=str, required=True)
parser.add_argument('--data', type=str, required=True)
parser.add_argument('--w0', type=float, default=1.81e-5)
parser.add_argument('--z0', type=float, default=0.00157)
args = parser.parse_args()

results = process_brand(
    brand=args.brand,
    data_folder=args.data,
    category='ca_oa',
    w0=args.w0,
    z0=args.z0,
    sample_length=0.0017,
    group_size=10,
    z_range=(-0.03, 0.03),
    project_dir="/home/yourname/project"
)
```

Then run:
```bash
python run_analysis.py --brand calcirol --data /path/to/data
```

---

## 6. File Structure Explained

### 6.1 `select_file.py` – Data Loading Module

**Purpose:** Loads and organizes files by brand and category.

**Key Components:**

| Component | Description |
|-----------|-------------|
| `DataLoader` class | Main class for file management |
| `load_files()` | Recursively finds and loads CSV files |
| `categorize_files()` | Sorts files by type (ca_oa, calculated, csv, etc.) |
| `get_dataframes()` | Retrieves loaded DataFrames |

**How it works:**
1. Scans the specified folder recursively
2. Categorizes files by their extension/name pattern
3. Loads CA/OA files with only the first two columns
4. Stores files in a nested dictionary: `{brand: {category: [files]}}`

**Example:**
```python
from select_file import DataLoader

loader = DataLoader()
loader.load_files('calcirol', '/path/to/data', 'ca_oa')
files = loader.get_dataframes('calcirol', 'ca_oa')
```

---

### 6.2 `file_process.py` – Core Processing Functions

**Purpose:** Contains all the core data processing functions used in the pipeline.

**Key Functions:**

| Function | Description | Input | Output |
|----------|-------------|-------|--------|
| `normalize_ca_oa()` | Normalizes CA and OA signals | DataFrame with 'ca', 'oa' | DataFrame with normalized columns |
| `get_Z()` | Converts indices to physical Z positions | DataFrame with normalized data | DataFrame with 'z' column, x_pred |
| `smooth_signal()` | Bins and averages data to reduce noise | DataFrame, group_size | Smoothed DataFrame with errors |
| `select_range()` | Filters data within Z-range | DataFrame, column, bounds | Filtered DataFrame |
| `get_power_and_irradiance()` | Extracts power from filename | file_path, w0 | (num, power_mW, I0) |
| `compute_fit_stats()` | Calculates fit quality metrics | Observed, predicted, sigma | Dictionary of statistics |

**Processing Flow:**
```
Raw CSV → normalize_ca_oa() → get_Z() → smooth_signal() → select_range() → Fit
```

**Smoothing Detail:**
- Groups rows into bins of size `group_size`
- For each bin: calculates mean (position) and std (error)
- Returns: `z`, `{col}_mean`, `{col}_std`

---

### 6.3 `z_formulae.py` – Theoretical Z-Scan Formulas

**Purpose:** Defines the theoretical Z-scan equations for curve fitting.

**Functions:**

| Function | Formula | Use Case |
|----------|---------|----------|
| `z_formulae_thin(x, phi)` | `T = 1 + 4φx / ((1+x²)(9+x²))` | Thin medium (L << z0) |
| `z_formulae_thick(x, l, phi)` | `T = 1 + 0.25*ln(N/D)*φ` | Thick medium (L ≈ z0) |

**Parameters:**
- `x = z/z0` (normalized position)
- `φ` (phase shift, Δφ)
- `l = L/z0` (normalized sample length)

**Usage in fitting:**
```python
from z_formulae import z_formulae_thin
popt, pcov = curve_fit(z_formulae_thin, x_norm, Yax, sigma=sigma)
phi_fit = popt[0]
```

---

### 6.4 `process_data.py` – Main Pipeline

**Purpose:** Orchestrates the entire processing workflow.

**Key Functions:**

| Function | Description |
|----------|-------------|
| `process_single_file()` | Processes one CA/OA file through the full pipeline |
| `process_brand()` | Processes all files for a brand |
| `plot_single_result()` | Creates individual plot for one file |
| `create_multipage_pdf()` | Generates multi-page PDF report |
| `get_directories()` | Creates and returns directory paths |

**`process_single_file()` Flow:**
```
1. Get power from filename (get_power_and_irradiance)
2. Normalize CA/OA (normalize_ca_oa)
3. Get Z positions (get_Z)
4. Smooth signal (smooth_signal)
5. Filter by Z range (select_range)
6. Prepare for fitting (extract arrays)
7. Fit curve (curve_fit with z_formulae_thin)
8. Calculate statistics (compute_fit_stats)
9. Return results dictionary
```

**`process_brand()` Flow:**
```
1. Create directories
2. Load files (DataLoader)
3. For each file:
   a. Process file (process_single_file)
   b. Save original data (optional)
   c. Save processed CSV
   d. Save individual plot
   e. Store results
4. Save results CSV
5. Create multi-page PDF
6. Print summary
```

**Plotting Details:**
- Error bars from `normalized_ca/oa_std`
- Red line for theoretical fit
- Grid, minor ticks, and inward ticks for professional appearance

---

### 6.5 `run_analysis.py` – Configuration & Execution

**Purpose:** Entry point for running the analysis with your specific parameters.

**What to Configure:**

```python
# Paths
PROJECT_DIR = r"/home/yourname/project"  # Root directory
BRAND = "your_brand"                     # Brand name
DATA_FOLDER = r"/path/to/data"           # Folder with CSV files

# Physical Parameters
lmda = 655e-9      # Laser wavelength (m)
w0 = 1.81e-5       # Beam waist (m)
z0 = np.pi * w0**2 / lmda  # Rayleigh length (auto)

# Processing Parameters
GROUP_SIZE = 10         # Bin size for smoothing
Z_RANGE = (-0.03, 0.03) # Z-range for filtering
SAMPLE_LENGTH = 0.0017  # Sample thickness (m)
```

**Execution:**
```bash
python run_analysis.py
```

---

## 7. Output Files

### 7.1 Processed CSV Files

**Location:** `processed/{brand_name}/{num}({power}mW).csv`

**Columns:**
| Column | Description |
|--------|-------------|
| `z` | Position in meters |
| `normalized_ca/oa_mean` | Average signal value |
| `normalized_ca/oa_std` | Error/standard deviation |

**Example:**
```csv
z,normalized_ca/oa_mean,normalized_ca/oa_std
-0.030,0.950,0.012
-0.029,0.952,0.011
...
```

### 7.2 Results CSV

**Location:** `processed/{brand_name}/{brand_name}_results.csv`

**Columns:**
| Column | Description |
|--------|-------------|
| `filename` | Original filename |
| `num` | Extracted number from filename |
| `power_mW` | Laser power in milliwatts |
| `irradiance_GW_m2` | Irradiance in GW/m² |
| `sample_length_mm` | Sample thickness in mm |
| `rayleigh_range_mm` | Rayleigh length in mm |
| `delphi` | Fitted phase shift (Δφ) |
| `abs_delphi` | Absolute value of Δφ |
| `delphi_err` | Error in Δφ |
| `Zpv` | Peak-to-valley distance in meters |
| `Tpv` | Peak-to-valley height |
| `R_sq_reg` | R² from regression (percentage) |
| `R_sq_pearson` | R² from Pearson correlation (percentage) |
| `RMSE` | Root Mean Squared Error |
| `MAE` | Mean Absolute Error |
| `MAPE (%)` | Mean Absolute Percentage Error |
| `chi_sq` | Chi-squared |

### 7.3 Individual Plots

**Location:** `graph/{brand_name}/{num}({power}mW).png`

**Features:**
- Experimental data with error bars (blue dots)
- Theoretical fit (red line)
- Title with brand, power, and Δφ
- Professional styling with grid and ticks

### 7.4 Multi-Page PDF Report

**Location:** `processed/{brand_name}/{brand_name}_analysis.pdf`

**Features:**
- 4 rows × 2 columns per page
- Each entry shows CA and OA plots side-by-side
- CA plot: data with error bars + theoretical fit
- OA plot: raw OA data
- Page titles with brand name

---

## 8. Troubleshooting

### 8.1 Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Path doesn't exist | Check `DATA_FOLDER` path in `run_analysis.py` |
| `KeyError: 'normalized_ca/oa_mean'` | Smoothing failed | Check `group_size`; ensure data has enough points |
| `'z' is not defined` | Issue in `z_formulae.py` | Update `z_formulae.py` to correct version |
| `sigma has incorrect shape` | Sigma array mismatch | Add data cleaning before fitting |
| `Encountered all NA values` | No valid data after filtering | Widen `Z_RANGE` or adjust `group_size` |
| `name 'sample_length' is not defined` | Variable not passed | Add `sample_length` to function calls |

### 8.2 Debugging Tips

**1. Enable detailed logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**2. Add print statements in `process_single_file`:**
```python
print(f"   Debug: df_norm shape: {df_norm.shape}")
print(f"   Debug: processed_df shape: {processed_df.shape}")
print(f"   Debug: x_norm points: {len(x_norm)}")
```

**3. Check your data after each step:**
```python
# After normalization
print(df_norm.head())
# After smoothing
print(reduced_df.head())
# After filtering
print(processed_df.head())
```

**4. Verify physical parameters:**
```python
print(f"z0 = {z0*1000:.3f} mm")
print(f"sample_length/z0 = {sample_length/z0:.3f}")
```

### 8.3 Handling Missing Files

If some files fail, check:
- Filename format: `{number}_ca_oa.csv`
- File has at least 2 columns (CA and OA)
- No empty or corrupted files
- Sufficient data points (>1000 rows)

---

## 9. Customization Guide

### 9.1 Adding New Z-Scan Formulas

Add to `z_formulae.py`:

```python
def my_custom_formula(x, param1, param2):
    """Custom Z-scan formula"""
    return 1 + param1 * x / (1 + param2 * x**2)
```

Then in `process_data.py`:

```python
from z_formulae import my_custom_formula

# In process_single_file:
popt, pcov = curve_fit(my_custom_formula, x_norm, Yax, sigma=sigma)
```

### 9.2 Changing Plot Styles

Modify `plot_single_result()`:

```python
# Change colors
ax.errorbar(Xcm, Yax, yerr=yerr, fmt='o', color='#FF6B6B',  # Red
            ecolor='#FFB3B3', capsize=3)

# Change figure size
fig, ax = plt.subplots(figsize=(8, 6))  # Larger

# Add custom labels
ax.set_xlabel('Position (cm)', fontsize=14, fontweight='bold')
ax.set_ylabel('Transmittance', fontsize=14, fontweight='bold')
```

### 9.3 Adding New Statistics

In `process_single_file()`, after `fit_stats`:

```python
# Add custom statistic
fit_stats['my_custom_stat'] = np.mean(np.abs(Yax - Y_fit)) * 100

# Then in results dictionary:
'my_custom_stat': round(fit_stats['my_custom_stat'], 2)
```

### 9.4 Changing Directory Structure

Modify `get_directories()` in `process_data.py`:

```python
def get_directories(project_dir, brand):
    data_dir = os.path.join(project_dir, "raw_data", brand)       # Changed
    processed_dir = os.path.join(project_dir, "output", brand)    # Changed
    graph_dir = os.path.join(project_dir, "figures", brand)       # Changed
    # ...
```

### 9.5 Adding Parallel Processing

For faster batch processing:

```python
from multiprocessing import Pool

def process_file_wrapper(args):
    return process_single_file(*args)

# In process_brand:
with Pool(processes=4) as pool:
    results = pool.map(process_file_wrapper, file_args)
```

### 9.6 Exporting to Excel

```python
# Instead of CSV
results_df.to_excel(f"{brand}_results.xlsx", index=False)

# With formatting
with pd.ExcelWriter(f"{brand}_results.xlsx") as writer:
    results_df.to_excel(writer, sheet_name='Results', index=False)
    # Add another sheet for statistics
    results_df.describe().to_excel(writer, sheet_name='Statistics')
```

---

## 10. License & Acknowledgments

### 10.1 License

This project is distributed under the MIT License. Feel free to use, modify, and distribute it for academic or commercial purposes.

### 10.2 Acknowledgments

- **Z-scan Theory**: Sheik-Bahae et al., "Sensitive measurement of optical nonlinearities using a single beam," IEEE J. Quantum Electron. 26, 760-769 (1990)
- **Python Ecosystem**: NumPy, SciPy, pandas, Matplotlib, scikit-learn

### 10.3 Contact

For questions, issues, or feature requests, please create an issue in the repository or contact the maintainer.

---

## Appendix A: Example Output

### A.1 Console Output Sample

```
============================================================
CA/OA DATA ANALYSIS PIPELINE
============================================================
Brand: calcirol
Data folder: /home/user/Downloads/Data/Calcirol
Rayleigh length (z0): 1.57 mm
Sample length: 1.70 mm
============================================================

📁 Found 70 files to process
============================================================

[1/70] Processing: 185_ca_oa.csv
   💾 Saved original: 185.csv
   Debug: df_norm shape = (12000, 6)
   Debug: processed_df shape = (600, 7)
   Debug: Using 600 points for fitting
   ✅ Saved CSV: 185(144.56mW).csv
   ✅ Saved plot: 185(144.56mW).png

[2/70] Processing: 186_ca_oa.csv
   💾 Saved original: 186.csv
   ✅ Saved CSV: 186(145.23mW).csv
   ✅ Saved plot: 186(145.23mW).png

...

[70/70] Processing: 254_ca_oa.csv
   💾 Saved original: 254.csv
   ✅ Saved CSV: 254(168.90mW).csv
   ✅ Saved plot: 254(168.90mW).png

✅ Saved multi-page PDF to: /home/user/project/processed/calcirol/calcirol_analysis.pdf

📊 Saved results CSV: /home/user/project/processed/calcirol/calcirol_results.csv

============================================================
✅ ANALYSIS COMPLETE FOR CALCIROL
============================================================
   Processed: 70/70 files
   Results: /home/user/project/processed/calcirol/calcirol_results.csv
   PDF: /home/user/project/processed/calcirol/calcirol_analysis.pdf
   Graphs: /home/user/project/graph/calcirol

📈 SUMMARY STATISTICS:
   num  power_mW  abs_delphi  delphi_err  R_sq_reg
0  185    144.56       0.023       0.001     98.45
1  186    145.23       0.025       0.001     97.89
...
69 254    168.90       0.031       0.002     96.12

📊 Summary statistics saved.

✨ All done!
```

### A.2 Results CSV Sample

```csv
filename,num,power_mW,irradiance_GW_m2,sample_length_mm,rayleigh_range_mm,abs_delphi,delphi_err,Zpv,Tpv,R_sq_reg,RMSE
185_ca_oa.csv,185,144.56,1.2345,1.700,1.570,0.023,0.001,0.0085,0.1250,98.45,0.008
186_ca_oa.csv,186,145.23,1.2456,1.700,1.570,0.025,0.001,0.0084,0.1280,97.89,0.009
...
```

### A.3 Plot Description

Each individual plot shows:
- **X-axis**: Z position in cm
- **Y-axis**: Normalized transmittance (I/I₀)
- **Blue dots**: Experimental data with error bars
- **Red line**: Theoretical fit
- **Title**: Brand, file number, power, and Δφ value

---

## Appendix B: Quick Reference

### B.1 Key Parameters

| Parameter | Symbol | Typical Value | Unit |
|-----------|--------|---------------|------|
| Wavelength | λ | 655e-9 | m |
| Beam waist | w₀ | 1.81e-5 | m |
| Rayleigh length | z₀ | πw₀²/λ | m |
| Sample length | L | 0.0017 | m |
| Group size | - | 10 | points |
| Z-range | - | ±0.03 | m |

### B.2 Key Equations

**Z-Scan Formula (Thin Medium):**
```
T(x) = 1 + 4·Δφ·x / ((1+x²)(9+x²))
where x = z/z₀
```

**Power Calibration:**
```
P(mW) = -1467 + 12.6·N - 0.0242·N²
where N = number from filename
```

**Irradiance:**
```
I₀ = P / (π·w₀²)
```

### B.3 Quick Commands

| Task | Command |
|------|---------|
| Run analysis | `python run_analysis.py` |
| Check logs | `tail -f logs/{brand}_analysis.log` |
| View results | `cat processed/{brand}/{brand}_results.csv` |
| Open PDF | `evince processed/{brand}/{brand}_analysis.pdf` |

---
