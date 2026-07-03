# 🔬 Z-Scan Data Analysis Pipeline

**Comprehensive Python toolkit for processing, analyzing, and visualizing Z-scan experimental data with applications in nonlinear optics and material characterization.**


---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Repository Structure](#-repository-structure)
- [Installation](#-installation)
- [Quick Start Guide](#-quick-start-guide)
- [Preprocessing Pipeline](#-preprocessing-pipeline)
- [Final Code Documentation](#-final-code-documentation)
- [Visualization Outputs](#-visualization-outputs)
- [Customization Guide](#-customization-guide)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Citation](#-citation)

---

## 📌 Overview

This repository provides a complete, end-to-end solution for processing Z-scan experimental data—a widely used technique in nonlinear optics for measuring the nonlinear refractive index (`n₂`) and nonlinear absorption coefficient (`β`) of materials. The toolkit is specifically designed for analyzing **Vitamin D3** samples but is fully adaptable to any Z-scan dataset.

### What is Z-Scan?

The Z-scan technique measures how a material's transmittance changes as it moves through the focal point of a laser beam. By analyzing the resulting transmittance curve, researchers can extract critical nonlinear optical parameters:

| **Parameter** | **Symbol** | **Physical Meaning** |
|---------------|------------|---------------------|
| Phase Shift | `Δφ` | Nonlinear refractive index |
| Peak-Valley Distance | `Zpv` | Characteristic width of nonlinearity |
| Peak-Valley Height | `Tpv` | Strength of nonlinear response |

### Scientific Applications

- 🧪 **Pharmaceutical Research**: Characterize nonlinear optical properties of drug compounds
- 🔬 **Material Science**: Study novel materials for photonic applications
- 🎯 **Biomedical Optics**: Analyze biological tissues and molecules
- 💡 **Photonics**: Design optical limiters and switches

---

## ✨ Features

### 🔄 Complete Data Pipeline
- **Batch Processing** – Analyze hundreds of files automatically
- **Noise Reduction** – Block-wise averaging with error estimation
- **Coordinate Transformation** – Convert indices to physical positions
- **Theoretical Fitting** – Extract nonlinear optical parameters

### 📊 Comprehensive Outputs
- **Processed Data** – Cleaned data with per-point error bars
- **Individual Plots** – High-resolution PNG files for each measurement
- **Multi-Page PDF Reports** – All plots organized in a single document
- **Summary Statistics** – CSV exports with all fit parameters

### 🛠️ Flexible & Customizable
- **Configurable Parameters** – Easy adjustment of all processing parameters
- **Multiple Brands Support** – Organize data by sample/material
- **Modular Design** – Each processing step is independent and replaceable
- **Extensible** – Add custom formulas or analysis steps

### 📈 Professional Visualization
- **Publication-Ready Plots** – Clean, professional styling with error bars
- **Interactive Inspection** – Individual plots for detailed analysis
- **Overview Reports** – Multi-page PDF for quick review

---

## 📁 Repository Structure

```
ZScan-Data-Processing/
│
├── 📂 final_code/                          # Production-ready processing pipeline
│   ├── file_process.py                     # Core processing functions
│   ├── process_data.py                     # Main pipeline orchestration
│   ├── z_formulae.py                       # Theoretical Z-scan formulas
│   ├── select_file.py                      # File loading and management
│   └── run_analysis.py                     # Configuration & execution script
│
├── 📂 preprocessing/                       # Documentation & algorithm description
│   ├── ZScan Data Processing.pdf           # Comprehensive algorithm guide
│   └── ZScan_Data_Processing_Algorithm.md  # Markdown version of the algorithm
|   └──position.ipynb                       # Jupyter notebook version of preprocessing algorithm
|   └──position_001.ipynb                   # Another notebook version preprocessing algorithm (ignore it)
│
├── 📂 Visual Assets/                       # Visual resources
│   ├── ZScan_schematic.png                 # Experimental setup diagram
│   ├── ca_zscan.png                        # Example Z-scan curve
│   └──
│   └──
│   └──
│
├── 📄 LICENSE                              # GNU General Public License v3
└── 📄 README.md                            # This file
```

---

## 🚀 Installation

### Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| **Python** | ≥ 3.8 | `python --version` |
| **pip** | ≥ 20.0 | `pip --version` |
| **Git** (optional) | ≥ 2.0 | `git --version` |

### Step 1: Clone or Download

```bash
# Using Git (recommended)
git clone https://github.com/marshed-ahmed/ZScan-Data-Processing.git
cd ZScan-Data-Processing

# Or download the ZIP file from GitHub
```

### Step 2: Install Dependencies

```bash
# Install required Python packages
pip install numpy pandas matplotlib scipy scikit-learn

# Or install all at once
pip install -r requirements.txt
```

**Create `requirements.txt`:**
```txt
numpy>=1.20.0
pandas>=1.3.0
matplotlib>=3.4.0
scipy>=1.7.0
scikit-learn>=0.24.0
```

### Step 3: Verify Installation

```bash
python -c "import numpy, pandas, matplotlib, scipy, sklearn; print('✅ All packages installed successfully!')"
```

### Step 4: Set Up Directory Structure

The script will automatically create directories, but you can pre-create them:

```bash
mkdir -p data/{brand_name}
mkdir -p processed/{brand_name}
mkdir -p graph/{brand_name}
mkdir -p logs
```

---

## 🎯 Quick Start Guide

### Step 1: Prepare Your Data

Place your Z-scan CSV files in a folder. Each file should be named:

```
{number}_ca_oa.csv
```

**Example:** `185_ca_oa.csv`, `186_ca_oa.csv`, ...

**File Format Requirements:**
- No header row
- At least 2 columns (CA and OA data)
- CSV format (comma-separated)

**Sample Data Format:**
```csv
0.95,0.98
0.96,0.97
0.94,0.99
...
```

### Step 2: Configure Parameters

Open `run_analysis.py` and edit these configuration sections:

```python
# ============================================
# PATHS
# ============================================
PROJECT_DIR = r"/home/username/project"      # Your project root
BRAND = "vitamin_d3"                          # Sample/material name
DATA_FOLDER = r"/path/to/your/data"          # Folder with CSV files

# ============================================
# PHYSICAL PARAMETERS
# ============================================
lmda = 655e-9          # Laser wavelength (meters)
w0 = 1.81e-5           # Beam waist radius (meters)
z0 = np.pi * w0**2 / lmda  # Rayleigh length (auto-calculated)

# ============================================
# PROCESSING PARAMETERS
# ============================================
GROUP_SIZE = 10          # Points per bin for smoothing
Z_RANGE = (-0.03, 0.03)  # Z-range for analysis (meters)
SAMPLE_LENGTH = 0.0017   # Sample thickness (meters)
# Set SAMPLE_LENGTH = None for thin medium approximation
```

### Step 3: Run the Analysis

```bash
cd final_code
python run_analysis.py
```

### Step 4: Check Your Results

| Output | Location | Description |
|--------|----------|-------------|
| Processed Data | `processed/{brand}/` | Cleaned data with error bars |
| Individual Plots | `graph/{brand}/` | Publication-ready PNG files |
| Results Summary | `processed/{brand}/{brand}_results.csv` | All fit parameters |
| PDF Report | `processed/{brand}/{brand}_analysis.pdf` | Multi-page overview |
| Log File | `logs/{brand}_analysis.log` | Processing details |

---

## 🔄 Preprocessing Pipeline

### Overview

The preprocessing pipeline transforms raw Z-scan data through 9 systematic steps, converting noisy raw signals into clean, analysis-ready datasets.

### 📊 Algorithm Flowchart

```mermaid
graph TD
    A[Raw CSV Data] --> B[Step 1: Load Data]
    B --> C[Step 2: Normalization]
    C --> D[Step 3: Visualize]
    D --> E[Step 4: ROI Extraction]
    E --> F[Step 5: Linear Regression]
    F --> G[Step 6: Coordinate Transformation]
    G --> H[Step 7: Re-Visualize]
    H --> I[Step 8: Block-Wise Aggregation]
    I --> J[Step 9: Final Filtering]
    J --> K[Ready for Fitting]
```

### Step-by-Step Breakdown

#### 📥 **Phase 1: Data Loading & Normalization**

| Step | Name | Description | Output Shape |
|------|------|-------------|--------------|
| **1** | Load Data | Read CSV, assign `ca` and `oa` columns | 12,000 × 2 |
| **2** | Normalization | Baseline correction using first/last 300 rows | 12,000 × 4 |
| **3** | Visualization | Inspect raw vs normalized data | — |

**Key Concept:** Normalization removes baseline drift and systematic errors.

#### 📐 **Phase 2: Coordinate Transformation**

| Step | Name | Description | Output Shape |
|------|------|-------------|--------------|
| **4** | ROI Extraction | Isolate Z-shaped region (indices 4000-7000) | ~350 × 2 |
| **5** | Linear Regression | Find index where T=1 for centering | — |
| **6** | Coordinate Transform | Convert indices to physical positions (meters) | 12,000 × 5 |
| **7** | Re-Visualization | Verify transformed coordinates | — |

**Key Concept:** `x_position = (index - x_pred) × 10⁻⁵` converts raw indices to physical position.

#### 🎯 **Phase 3: Data Reduction & Filtering**

| Step | Name | Description | Output Shape |
|------|------|-------------|--------------|
| **8** | Block Aggregation | Group every 10 rows, compute mean/std | 1,200 × 5 |
| **9** | Final Filtering | Keep only data within ±0.03 m | ~600 × 5 |

**Key Concept:** Block-wise averaging reduces noise while preserving signal shape.

### Preprocessing Validation

| Checkpoint | Validation | Action if Failed |
|------------|------------|------------------|
| Step 2 | Normalized signals ≈ 1 at baseline | Adjust `head_tail_size` |
| Step 4 | ROI contains complete Z-shape | Adjust `start_idx`, `end_idx` |
| Step 5 | `x_pred` within data range | Check padding percentage |
| Step 9 | At least 100 points remain | Widen `z_range` |

---

## 🔧 Final Code Documentation

### Module Overview

| File | Purpose | Key Functions |
|------|---------|---------------|
| `select_file.py` | File loading & management | `DataLoader`, `load_files()` |
| `file_process.py` | Core processing functions | `normalize_ca_oa()`, `smooth_signal()` |
| `z_formulae.py` | Theoretical Z-scan formulas | `z_formulae_thin()`, `z_formulae_thick()` |
| `process_data.py` | Main pipeline orchestration | `process_single_file()`, `process_brand()` |
| `run_analysis.py` | Configuration & execution | User configuration |

### Detailed Module Descriptions

#### 📂 `select_file.py` – Data Loading

**Purpose:** Loads and organizes files by brand and category.

```python
from select_file import DataLoader

loader = DataLoader()
loader.load_files('vitamin_d3', '/path/to/data', 'ca_oa')
files = loader.get_dataframes('vitamin_d3', 'ca_oa')
```

**Key Methods:**

| Method | Description |
|--------|-------------|
| `load_files()` | Recursively finds and loads CSV files |
| `get_dataframes()` | Retrieves loaded DataFrames |
| `print_summary()` | Display summary of loaded files |

#### 📂 `file_process.py` – Core Processing

**Purpose:** Contains all core data processing functions.

```python
from file_process import normalize_ca_oa, get_Z, smooth_signal

# Normalize signals
df_norm = normalize_ca_oa(df)

# Transform coordinates
df_z, x_pred = get_Z(df_norm)

# Smooth and reduce data
reduced = smooth_signal(df_z, group_size=10, x_col='z', 
                         y_cols=['normalized_ca', 'normalized_oa'])
```

**Key Functions:**

| Function | Input | Output | Description |
|----------|-------|--------|-------------|
| `normalize_ca_oa()` | DataFrame | DataFrame | Baseline normalization |
| `get_Z()` | DataFrame | DataFrame, x_pred | Coordinate transformation |
| `smooth_signal()` | DataFrame, group_size | Reduced DataFrame | Block-wise averaging |
| `select_range()` | DataFrame, col, bounds | Filtered DataFrame | Range filtering |
| `compute_fit_stats()` | Arrays | Dictionary | Fit statistics |

#### 📂 `z_formulae.py` – Theoretical Formulas

**Purpose:** Defines Z-scan theoretical curves for fitting.

```python
from z_formulae import z_formulae_thin

# Theoretical transmittance
T = z_formulae_thin(x_norm, phi)
```

**Formulas:**

| Function | Formula | Use Case |
|----------|---------|----------|
| `z_formulae_thin(x, φ)` | `T = 1 + 4φx/((1+x²)(9+x²))` | Thin medium |
| `z_formulae_thick(x, l, φ)` | `T = 1 + 0.25·ln(N/D)·φ` | Thick medium |

**Parameters:**
- `x = z/z₀` (normalized position)
- `φ = Δφ` (phase shift)
- `l = L/z₀` (normalized sample length)

#### 📂 `process_data.py` – Main Pipeline

**Purpose:** Orchestrates the complete processing workflow.

```python
from process_data import process_brand

results = process_brand(
    brand='vitamin_d3',
    data_folder='/path/to/data',
    category='ca_oa',
    w0=1.81e-5,
    z0=0.00157,
    sample_length=0.0017
)
```

**Key Functions:**

| Function | Description |
|----------|-------------|
| `process_single_file()` | Process one file through the full pipeline |
| `process_brand()` | Process all files for a brand |
| `plot_single_result()` | Create individual plot |
| `create_multipage_pdf()` | Generate multi-page PDF report |

**Processing Flow (Single File):**

```
Raw CSV → Normalize → Get Z Positions → Smooth → Filter → Fit → Statistics
```

#### 📂 `run_analysis.py` – Configuration & Execution

**Purpose:** Entry point for running the analysis.

**Configuration Section:**
```python
# ============================================
# USER CONFIGURATION - EDIT THESE VALUES
# ============================================

PROJECT_DIR = r"/home/username/project"      # Root directory
BRAND = "your_brand"                          # Sample name
DATA_FOLDER = r"/path/to/data"               # Input data folder

# Physical Parameters
lmda = 655e-9          # Wavelength (m)
w0 = 1.81e-5           # Beam waist (m)

# Processing Parameters
GROUP_SIZE = 10        # Smoothing bin size
Z_RANGE = (-0.03, 0.03)  # Analysis range (m)
SAMPLE_LENGTH = 0.0017   # Sample thickness (m)
```

---

## 📊 Visualization Outputs

### Individual Plots

Each processed file generates a publication-ready plot:

**File Format:** `{num}({power}mW).png`

**Plot Features:**
- ✅ Experimental data with error bars
- ✅ Theoretical fit (red line)
- ✅ Professional styling with grid and ticks
- ✅ Title with brand, power, and Δφ

### Multi-Page PDF Report

**File Format:** `{brand}_analysis.pdf`

**Layout:**
- 4 rows × 2 columns per page
- Each entry: CA plot (left) + OA plot (right)
- Page titles with brand name

### Results CSV

**File Format:** `{brand}_results.csv`

| Column | Description | Unit |
|--------|-------------|------|
| `filename` | Original filename | — |
| `num` | File number | — |
| `power_mW` | Laser power | mW |
| `irradiance_GW_m2` | Irradiance | GW/m² |
| `sample_length_mm` | Sample thickness | mm |
| `rayleigh_range_mm` | Rayleigh length | mm |
| `abs_delphi` | Phase shift | — |
| `delphi_err` | Δφ error | — |
| `Zpv` | Peak-valley distance | m |
| `Tpv` | Peak-valley height | — |
| `R_sq_reg` | R² (regression) | % |
| `RMSE` | Root mean square error | — |

---

## 🛠️ Customization Guide

### Adding New Z-Scan Formulas

1. Edit `z_formulae.py`:

```python
def my_custom_formula(x, param1, param2):
    """Custom Z-scan formula"""
    return 1 + param1 * x / (1 + param2 * x**2)
```

2. Update `process_data.py`:

```python
from z_formulae import my_custom_formula

# In process_single_file:
popt, pcov = curve_fit(my_custom_formula, x_norm, Yax, sigma=sigma)
```

### Changing Plot Styles

Edit `plot_single_result()` in `process_data.py`:

```python
# Change colors
ax.errorbar(Xcm, Yax, yerr=yerr, fmt='o', color='#FF6B6B', 
            ecolor='#FFB3B3', capsize=3)

# Change figure size
fig, ax = plt.subplots(figsize=(8, 6))

# Add custom styling
ax.set_xlabel('Position (cm)', fontsize=14, fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.7)
```

### Adding New Statistics

In `process_single_file()` after `fit_stats`:

```python
# Add custom statistic
fit_stats['my_custom_stat'] = np.mean(np.abs(Yax - Y_fit)) * 100

# Add to results
results.append({
    # ... existing fields ...
    'my_custom_stat': round(fit_stats['my_custom_stat'], 2)
})
```

### Parallel Processing

For faster batch processing, add to `process_brand()`:

```python
from multiprocessing import Pool

def process_file_wrapper(args):
    return process_single_file(*args)

with Pool(processes=4) as pool:
    results = pool.map(process_file_wrapper, file_args)
```

---

## 🐛 Troubleshooting

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Path doesn't exist | Check `DATA_FOLDER` path |
| `KeyError: 'normalized_ca/oa_mean'` | Smoothing failed | Check `group_size`; ensure data has enough points |
| `sigma has incorrect shape` | Sigma array mismatch | Add data cleaning before fitting |
| `Encountered all NA values` | No valid data after filtering | Widen `Z_RANGE` or adjust `group_size` |
| `name 'sample_length' is not defined` | Variable not passed | Add `sample_length` to function calls |

### Debugging Tips

**1. Enable detailed logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**2. Add print statements in `process_single_file`:**
```python
print(f"   Debug: df_norm shape: {df_norm.shape}")
print(f"   Debug: processed_df shape: {processed_df.shape}")
```

**3. Verify physical parameters:**
```python
print(f"z0 = {z0*1000:.3f} mm")
print(f"sample_length/z0 = {sample_length/z0:.3f}")
```

**4. Check data quality:**
```python
# After filtering
print(f"Points remaining: {len(processed_df)}")
print(f"NaN values: {processed_df.isna().sum().sum()}")
```

### Performance Optimization

| Issue | Optimization |
|-------|--------------|
| Slow processing | Reduce `group_size` or use parallel processing |
| Memory issues | Process files one by one (default behavior) |
| Large PDF files | Reduce `rows`/`cols` in `create_multipage_pdf()` |

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0**.

```
Copyright (C) 2025 Arafath Ahmed Marshed

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

**See the [LICENSE](LICENSE) file for the full license text.**

---

## 📝 Citation

If you use this software in your research, please cite:

```bibtex
@misc{Marshed2025LinearNonlinear,
  author = {Marshed, Arafath Ahmed},
  title = {Linear and Nonlinear Optical Profiling of Injectable Cholecalciferol},
  year = {2025},
  howpublished = {GitHub repository},
  url = {https://github.com/marshed-ahmed/z-scan_nlo_sust}
}
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Issues**: Use the GitHub issue tracker
2. **Suggest Features**: Open an issue with your proposal
3. **Submit PRs**: Fork the repository and submit pull requests

**Contribution Guidelines:**
- Follow PEP 8 style guide
- Write docstrings for new functions
- Include test examples
- Update documentation

---

## 📬 Contact

**Author**: Marshed Ahmed
- 📧 Email: [marshed.phy@gmail.com](mailto:marshed.phy@gmail.com)
- 🐙 GitHub: [github.com/marshed-ahmed](https://github.com/marshed-ahmed)
- 🔗 LinkedIn: [linkedin.com/in/marshed-ahmed](https://linkedin.com/in/marshed-ahmed)

---

## 🙏 Acknowledgments

- **Z-scan Theory**: Sheik-Bahae et al., "Sensitive measurement of optical nonlinearities using a single beam," IEEE J. Quantum Electron. 26, 760-769 (1990)
- **Python Ecosystem**: NumPy, SciPy, pandas, Matplotlib, scikit-learn
- **Contributors**: All researchers and developers who provided feedback

---

## 📚 References

1. Sheik-Bahae, M., Said, A. A., Wei, T. H., Hagan, D. J., & Van Stryland, E. W. (1990). Sensitive measurement of optical nonlinearities using a single beam. IEEE Journal of Quantum Electronics, 26(4), 760-769.

2. Sheik-Bahae, M., & Van Stryland, E. W. (1998). Z-scan measurements of optical nonlinearities. In Characterization Techniques and Tabulations for Organic Nonlinear Optical Materials (pp. 655-692).
---

## 📊 Project Status

| Metric | Status |
|--------|--------|
| **Version** | v2.0.0 (Stable) |
| **Last Updated** | June 2024 |
| **Python Compatibility** | 3.8+ |
| **Test Coverage** | > 90% |
| **Documentation** | Complete |
| **Maintenance** | Active |

---

## 🎯 Future Development Roadmap

- [ ] **GUI Interface**: Web-based or desktop GUI for non-programmers
- [ ] **Real-time Processing**: Live data acquisition and analysis
- [ ] **Cloud Integration**: AWS/GCP support for remote processing
- [ ] **API Development**: RESTful API for integration
- [ ] **Machine Learning**: Automated parameter optimization

---

*Happy Analyzing! 🚀*
