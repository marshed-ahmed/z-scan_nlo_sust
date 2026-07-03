# ⚙️ Z-Scan Data Processing: Preprocessing Algorithm

## Overview

This document outlines the comprehensive **9-step preprocessing pipeline** designed to transform raw Z-Scan data into clean, analysis-ready datasets. The algorithm handles everything from raw signal normalization to coordinate transformation and data reduction.

---

## 📊 Data Flow Summary

| **Phase** | **Step** | **Input** | **Output** | **Description** |
|-----------|----------|-----------|------------|-----------------|
| **Phase 1** | 1 | Raw CSV | Initial DataFrame | Load and assign column names |
| | 2 | Initial DataFrame | Normalized DataFrame | Baseline normalization of signals |
| | 3 | Normalized DataFrame | Plots | Visual inspection of raw vs normalized |
| **Phase 2** | 4 | Normalized DataFrame | ROI-extracted data | Isolate the Z-shaped signal region |
| | 5 | ROI Data | Linear regression params | Extract transformation parameters |
| | 6 | Normalized DataFrame | Transformed DataFrame | Convert indices to physical positions |
| | 7 | Transformed DataFrame | Plots | Verify coordinate transformation |
| **Phase 3** | 8 | Transformed DataFrame | Reduced DataFrame | Block-wise averaging for denoising |
| | 9 | Reduced DataFrame | Final Filtered Data | Isolate central region for analysis |

---

## Phase 1: Data Loading & Normalization

### Step 1: Load and Preprocess Data

The initial step loads raw data and assigns meaningful column names.

| **Action** | **Details** |
|------------|-------------|
| **Load Data** | Read CSV file without headers |
| **Assign Columns** | First column → `ca` (Closed Aperture) |
| | Second column → `oa` (Open Aperture) |
| **Initial Shape** | **12,000 rows × 2 columns** |

```python
# Data structure after loading
df = pd.read_csv(file_path, header=None, names=['ca', 'oa'])
```

---

### Step 2: Normalization of the Original Signal

Raw signals are normalized using baseline averages to remove systematic variations.

| **Action** | **Details** |
|------------|-------------|
| **Calculate Baseline Means** | For each signal (`ca` and `oa`) |
| | Use the **first 300 and last 300 rows** |
| | Compute: `mean_ca`, `mean_oa`, `mean_ca/oa` |
| **Normalize Signals** | `normalized_ca = ca / mean_ca` |
| | `normalized_oa = oa / mean_oa` |
| | `normalized_ca/oa = (ca/oa) / mean_ca/oa` |
| **Filter Data** | Remove rows where normalized values are zero |
| **Shape After Normalization** | **12,000 rows × 4 columns** |

**Columns Added:**
- `normalized_ca`
- `normalized_oa`
- `normalized_ca/oa`

---

### Step 3: Visualize Original and Normalized Data

Plots are generated to visually confirm the normalization process.

| **Plot Type** | **Purpose** |
|---------------|-------------|
| Raw signals (`ca`, `oa`) | Inspect raw data quality |
| Normalized signals | Verify baseline correction |
| Ratio plot (`ca/oa`) | Check signal-to-noise ratio |

---

## Phase 2: Coordinate Transformation

### Step 4: Identify Region of Interest (ROI)

Isolates the region containing the Z-shaped signal feature for precise analysis.

| **Action** | **Details** |
|------------|-------------|
| **Select Subset** | Extract rows **4000–7000** from `normalized_ca/oa` |
| **Find Extrema** | Locate `min` and `max` positions within subset |
| | Record `min_pos`, `max_pos` (original indices) |
| **Extract Data** | Get all data between `min_pos` and `max_pos` |
| **ROI Shape** | **~350 rows × 2 columns** |

```
Data: 0 ──────────────────── 4000 ── 7000 ────────────── 12000
                              ├── ROI ──┤
                                  ↓
                         z-shaped feature region
```

---

### Step 5: Linear Fit to Extract Transformation Parameters

Linear regression determines the index value where baseline transmittance = 1 (T=1).

| **Action** | **Details** |
|------------|-------------|
| **Define Cropping** | Add **10% padding** to ROI boundaries |
| **Extract Variables** | `y` = normalized transmittance (independent) |
| | `x` = index values (dependent) |
| **Linear Regression** | Fit: `x = m·y + b` |
| **Predict x** | Calculate `x_pred` where `y = 1` |
| **Formula** | `x_pred = (1 - intercept) / slope` |

**Purpose:** `x_pred` serves as the center point for coordinate transformation.

---

### Step 6: Coordinate Transformation

Original index values are converted to physical position coordinates.

| **Action** | **Details** |
|------------|-------------|
| **Define Function** | `x_position = (index - x_pred) × 10⁻⁵` |
| **Apply Transformation** | Transform all indices to positions |
| **Add Column** | Add `z` column to DataFrame |
| **Shape** | **12,000 rows × 5 columns** |

**Physical Interpretation:**
- `x_pred` → baseline position (T=1)
- Positive `x_position` → positions after beam focus
- Negative `x_position` → positions before beam focus

---

### Step 7: Visualize with Transformed Coordinates

Generate plots using physical `z` coordinates (in meters).

| **Plot Type** | **Details** |
|---------------|-------------|
| X-axis | `z` position (meters) |
| Y-axis | Normalized transmittance (`normalized_ca/oa`) |
| Verification | Confirm correct centering and scaling |

---

## Phase 3: Data Reduction & Filtering

### Step 8: Reduce Data Points Using Block-Wise Aggregation

Dataset is downsampled by grouping and averaging to reduce noise.

| **Action** | **Details** |
|------------|-------------|
| **Grouping** | Combine every **10 rows** into a group |
| **Aggregation** | For each group, compute: |
| | • **Mean** of all columns |
| | • **Standard deviation** of signal columns |
| **Reduced Shape** | **1,200 rows × 5 columns** |

**Formula:**
```python
reduced_df = smooth_signal(df_z, group_size=10, 
                           x_col='z', 
                           y_cols=['normalized_ca', 'normalized_oa', 'normalized_ca/oa'])
```

**Columns in Reduced DataFrame:**
| Column | Description |
|--------|-------------|
| `z` | Mean position in each group |
| `normalized_ca_mean` | Mean CA signal |
| `normalized_ca_std` | Standard deviation (error) |
| `normalized_oa_mean` | Mean OA signal |
| `normalized_oa_std` | Standard deviation (error) |
| `normalized_ca/oa_mean` | Mean ratio signal |
| `normalized_ca/oa_std` | Standard deviation (error) |

---

### Step 9: Filter Region of Interest (Final)

Isolate the central region for final plotting and curve fitting.

| **Action** | **Details** |
|------------|-------------|
| **Range Selection** | Filter where: `-0.03 < z < 0.03` (meters) |
| **Final Shape** | **~600 rows × 5 columns** |
| **Plot Final Signals** | Generate final plots with error bars |

**Purpose:** This filtered dataset is used for:
- Theoretical curve fitting
- Parameter extraction (`Δφ`, `Zpv`, `Tpv`)
- Statistical analysis

---

## 📈 Final Data Characteristics

| **Parameter** | **Value** | **Unit** |
|---------------|-----------|----------|
| Original rows | 12,000 | rows |
| Reduced rows | 1,200 | rows |
| Filtered rows | ~600 | rows |
| Z-range | ±0.03 | meters |
| Group size | 10 | rows/group |
| Error bars | Standard deviation | - |

---

## 🔧 Code Implementation

The preprocessing pipeline is implemented in `process_single_file()` function:

```python
def process_single_file(df, file_path, w0, z0=0.001, 
                        sample_length=None, group_size=10, 
                        z_range=(-0.03, 0.03)):
    """
    Complete preprocessing pipeline for a single Z-scan file.
    """
    # Step 1-2: Load & Normalize
    num, power_mW, I0 = get_power_and_irradiance(file_path, w0)
    df_norm = normalize_ca_oa(df)
    
    # Step 4-6: Coordinate Transformation
    df_z, x_pred = get_Z(df_norm)
    
    # Step 8: Data Reduction
    reduced_df = smooth_signal(df_z, group_size, 'z', 
                               ['normalized_ca', 'normalized_oa', 'normalized_ca/oa'])
    
    # Step 9: Final Filtering
    processed_df = select_range(reduced_df, 'z', z_range[0], z_range[1])
    
    return processed_df
```

---

## ✅ Validation Checkpoints

| **Checkpoint** | **Validation** | **Action if Failed** |
|----------------|----------------|---------------------|
| Step 2 | Normalized signals ≈ 1 at baseline | Adjust `head_tail_size` |
| Step 4 | ROI contains complete Z-shape | Adjust `start_idx`, `end_idx` |
| Step 5 | `x_pred` within data range | Check padding percentage |
| Step 8 | Reduced data retains signal shape | Adjust `group_size` |
| Step 9 | At least 100 points remain | Widen `z_range` |

---

## 📋 Summary

The preprocessing algorithm transforms raw 12,000-row datasets into clean, analysis-ready data through:

1. **Normalization** – Remove baseline variations
2. **Coordinate Transformation** – Convert indices to physical positions
3. **Data Reduction** – Denoise via block-wise averaging
4. **Filtering** – Isolate central region for fitting

**Result:** ~600 rows of high-quality data with error estimates, ready for theoretical curve fitting and parameter extraction.
