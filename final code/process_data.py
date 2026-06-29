"""
Simple processing functions for CA/OA data analysis.
Imports functions from file_process.py and select_file.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.optimize import curve_fit
from datetime import datetime

# Import your existing functions
from file_process import (
    normalize_ca_oa, 
    get_Z, 
    smooth_signal, 
    select_range, 
    get_power_and_irradiance,
    compute_fit_stats
)
from z_formulae import (
    z_formulae_thick,
    z_formulae_thin
)

from select_file import DataLoader, get_loader


# ============================================
# CONFIGURATION
# ============================================

def get_directories(project_dir, brand):
    """Create and return directory paths for a brand."""
    data_dir = os.path.join(project_dir, "data", brand)
    processed_dir = os.path.join(project_dir, "processed", brand)
    graph_dir = os.path.join(project_dir, "graph", brand)
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(graph_dir, exist_ok=True)
    
    return data_dir, processed_dir, graph_dir


# ============================================
# MAIN PROCESSING FUNCTIONS
# ============================================

def process_single_file(df, file_path, w0, z0=0.001, sample_length=None, group_size=10, z_range=None):
    """
    Process a single CA/OA file through the entire pipeline.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with 'ca' and 'oa' columns
    file_path : str
        Path to original file (for extracting power)
    w0 : float
        Beam waist radius (meters)
    z0 : float
        Rayleigh length (meters)
    group_size : int
        Size for smoothing groups
    z_range : tuple
        (min_z, max_z) for filtering
        
    Returns:
    --------
    dict
        Dictionary containing:
        - 'processed_df': final processed DataFrame
        - 'num': extracted number from filename
        - 'power_mW': laser power in mW
        - 'I0': irradiance
        - 'x_pred': predicted x position from get_Z
        - 'fit_delphi': fitted phase shift
        - 'fit_delphi_err': error in phase shift
        - 'fit_stats': dictionary of fit statistics
        - 'y_fit': fitted Y values
    """
    
    # 1. Get power from filename
    num, power_mW, I0 = get_power_and_irradiance(file_path, w0)
    
    # 2. Normalize CA/OA
    df_norm = normalize_ca_oa(df)
    
    # 3. Get Z positions
    df_z, x_pred = get_Z(df_norm)
    
    # 4. Smooth signal
    reduced_df = smooth_signal(df_z, group_size, 'z', 
                               ['normalized_ca', 'normalized_oa', 'normalized_ca/oa'])
    
    # 5. Filter by Z range
    processed_df = select_range(reduced_df, 'z', z_range[0], z_range[1])
    
    if processed_df.empty:
        raise ValueError("No data after filtering")
    
    # 6. Prepare for fitting
    Xax = processed_df['z'].to_numpy()
    x_norm = Xax/z0
    Yax = processed_df['normalized_ca/oa_mean'].to_numpy()
    sigma = processed_df['normalized_ca/oa_std'].to_numpy()
    
 # 7. Fit curve
    if sample_length is not None and sample_length > z0:
        # Thick medium
        l_norm = sample_length / z0
        
        # Create wrapper with l_norm fixed
        def thick_fit(x, phi):
            return z_formulae_thick(x, l_norm, phi)
        
        popt, pcov = curve_fit(thick_fit, x_norm, Yax, sigma=sigma, p0=[1.0])
        delphi = popt[0]
        delphi_err = np.sqrt(pcov[0][0])
        Y_fit = thick_fit(x_norm, delphi)
    else:
        # Thin medium
        popt, pcov = curve_fit(z_formulae_thin, x_norm, Yax, sigma=sigma, p0=[1.0])
        delphi = popt[0]
        delphi_err = np.sqrt(pcov[0][0])
        Y_fit = z_formulae_thin(x_norm, delphi)
    
    # 8. Calculate fit statistics
    fit_stats = compute_fit_stats(Yax, Y_fit, sigma=sigma)
    
    # Add additional parameters
    fit_stats['abs_delphi'] = abs(delphi)
    fit_stats['delphi_err'] = delphi_err
    fit_stats['delphi'] = delphi
    fit_stats['Tpv'] = np.max(Y_fit) - np.min(Y_fit)
    fit_stats['Zpv'] = abs(Xax[np.argmin(Y_fit)] - Xax[np.argmax(Y_fit)])
    
    return {
        'processed_df': processed_df,
        'num': num,
        'power_mW': power_mW,
        'I0': I0,
        'x_pred': x_pred,
        'fit_delphi': delphi,
        'fit_delphi_err': delphi_err,
        'fit_stats': fit_stats,
        'y_fit': Y_fit,
        'x_values': Xax
    }


def save_processed_data(processed_df, num, power_mW, processed_dir):
    """Save processed DataFrame to CSV."""
    csv_path = os.path.join(processed_dir, f"{num}({power_mW:.2f}mW).csv")
    processed_df.to_csv(csv_path, index=False)
    return csv_path


# ============================================
# PLOTTING FUNCTIONS
# ============================================

def plot_single_result(processed_df, fit_result, filename, brand, output_dir):
    """
    Create and save a single plot for a file.
    
    Parameters:
    -----------
    processed_df : pd.DataFrame
        Processed DataFrame
    fit_result : dict
        Results from process_single_file
    filename : str
        Original filename
    brand : str
        Brand name for title
    output_dir : str
        Directory to save plot
        
    Returns:
    --------
    str
        Path to saved plot
    """
    num = fit_result['num']
    power_mW = fit_result['power_mW']
    delphi = fit_result['fit_stats']['abs_delphi']
    delphi_err = fit_result['fit_delphi_err']
    R_sq = fit_result['fit_stats']['R_sq_reg']
    
    # Prepare data
    Xcm = fit_result['x_values'] * 100  # Convert to cm
    Yax = processed_df['normalized_ca/oa_mean'].to_numpy()
    Y_fit = fit_result['y_fit']
    yerr = processed_df['normalized_ca/oa_std'].to_numpy()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Plot data with error bars
    ax.errorbar(Xcm, Yax, yerr=yerr, fmt='o', color='#0C359E',
                ecolor='#6bb6ff', elinewidth=0.9, markersize=5,
                capsize=3, mfc='white', label='Experimental Data')
    
    # Plot fit
    ax.plot(Xcm, Y_fit, '-', color='red', linewidth=2,
            label=f'Fit (|$\Delta\phi$| = {delphi:.3f} $\pm$ {delphi_err:.3f})')
    
    # Labels and styling
    ax.set_xlabel('Z (cm)', fontsize=12)
    ax.set_ylabel('Normalized Transmittance (I/I₀)', fontsize=12)
    ax.set_title(f'{brand} - {num}.csv\nPower: {power_mW:.2f} mW', fontsize=11)
    ax.set_xlim(-1, 1)
    ax.legend(fontsize=10, loc='best')
    
    # ===== FORMATTED TICKERS=====
    ax.grid(True, linestyle='--', linewidth=0.7, alpha=0.5)
    ax.minorticks_on()
    ax.tick_params(direction='in', top=True, right=True,
                   which='major', length=6, width=1.5)
    ax.tick_params(direction='in', top=True, right=True,
                   which='minor', length=3, width=1.0)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
    
    plt.tight_layout()
    
    # Save
    plot_path = os.path.join(output_dir, f"{num}({power_mW:.2f}mW).png")
    fig.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    return plot_path

def create_multipage_pdf(entries_data, output_path, rows=4, cols=2, 
                          page_title=None, brand=None):
    """
    Create multi-page PDF with multiple plots per page.
    """
    plots_per_page = rows * cols
    entries_per_page = plots_per_page // 2
    total_pages = (len(entries_data) + entries_per_page - 1) // entries_per_page
    current_page = 1
    
    with PdfPages(output_path) as pdf:
        fig = None
        axs = None
        
        for i, entry in enumerate(entries_data):
            # Start new page if needed
            if i % entries_per_page == 0:
                if fig is not None:
                    plt.tight_layout()
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close(fig)
                
                fig, axs = plt.subplots(rows, cols, 
                                       figsize=(cols * 4.5, rows * (4.5 / 1.615)))
                axs = axs.flatten()
                
                # Add main title
                if page_title:
                    fig.suptitle(page_title, fontsize=14, fontweight='bold', y=0.98)
                
                # Add page number and date
                date_str = datetime.now().strftime("%Y-%m-%d")
                fig.text(0.95, 0.02, f'Page {current_page}/{total_pages}', 
                        fontsize=8, ha='right')
                fig.text(0.02, 0.02, f'Date: {date_str}', fontsize=8, ha='left')
                
                # Add brand name if provided
                if brand:
                    fig.text(0.5, 0.02, f'Brand: {brand}', fontsize=8, ha='center')
                
                current_page += 1
            
            # Get axes for this entry
            local_idx = i % entries_per_page
            ax_ca = axs[2 * local_idx]
            ax_oa = axs[2 * local_idx + 1]
            
            # Plot CA data
            _plot_ca_on_axes(ax_ca, entry)
            
            # Plot OA data
            _plot_oa_on_axes(ax_oa, entry)
        
        # Save last page
        if fig is not None:
            # Remove unused subplots
            used_plots = plots_per_page if len(entries_data) % entries_per_page == 0 \
                        else (len(entries_data) % entries_per_page) * 2
            for j in range(used_plots, plots_per_page):
                fig.delaxes(axs[j])
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
    
    print(f"✅ Saved multi-page PDF to: {output_path}")


def _plot_ca_on_axes(ax, entry):
    """Helper: Plot CA data on given axes."""
    processed_df = entry['processed_df']
    fit_result = entry['fit_result']
    power_mW = fit_result['power_mW']
    delphi = fit_result['fit_stats']['abs_delphi']
    delphi_err = fit_result['fit_delphi_err']
    
    Xcm = fit_result['x_values'] * 100
    Yax = processed_df['normalized_ca/oa_mean'].to_numpy()
    Y_fit = fit_result['y_fit']
    yerr = processed_df['normalized_ca/oa_std'].to_numpy()
    
    ax.errorbar(Xcm, Yax, yerr=yerr, fmt='.', color='#0C359E',
                ecolor='#6bb6ff', elinewidth=0.9, markersize=4,
                mfc='white', label='CA Data')
    ax.plot(Xcm, Y_fit, '-', color='red', linewidth=2, label='Theoretical Fit')
    ax.set_title(f'CA: {power_mW:.2f} mW\n|Δφ|={delphi:.3f} ± {delphi_err:.3f}', fontsize=10)
    ax.set_xlim(-3, 3)
    ax.set_xlabel("Z (cm)", fontsize=10)
    ax.set_ylabel("I/I₀", fontsize=10)
    ax.legend(fontsize=8)


def _plot_oa_on_axes(ax, entry):
    """Helper: Plot OA data on given axes."""
    processed_df = entry['processed_df']
    filename = entry['filename']
    power_mW = entry['fit_result']['power_mW']
    
    Xcm = entry['fit_result']['x_values'] * 100
    Yoa = processed_df['normalized_oa_mean'].to_numpy() if 'normalized_oa_mean' in processed_df.columns else None
    
    if Yoa is not None:
        ax.plot(Xcm, Yoa, '.', color='green', markersize=4, 
                mfc='white', label='OA Data')
    
    ax.set_title(f'OA: {power_mW:.2f} mW ({filename})', fontsize=10)
    ax.set_xlim(-3, 3)
    ax.set_xlabel("Z (cm)", fontsize=10)
    ax.set_ylabel("I/I₀", fontsize=10)
    ax.legend(fontsize=8)


# ============================================
# BATCH PROCESSING FUNCTION
# ============================================

def process_brand(brand, data_folder, category, w0, z0, 
                  group_size, z_range=None, sample_length=None, 
                  project_dir=None, save_intermediate=True):
    """
    Process all CA/OA files for a brand.
    
    Parameters:
    -----------
    brand : str
        Brand name (e.g., 'calcirol')
    data_folder : str
        Path to folder containing the CSV files
    w0 : float
        Beam waist radius in meters (default: 100e-6)
    z0 : float
        Rayleigh length in meters (default: 0.001)
    group_size : int
        Size for smoothing groups (default: 10)
    z_range : tuple
        (min_z, max_z) range for filtering (default: (-0.03, 0.03))
    project_dir : str or None
        Project directory. If None, uses parent of data_folder
        
    Returns:
    --------
    pd.DataFrame
        Results DataFrame for all processed files
    """
    
    # Setup directories
    if project_dir is None:
        project_dir = os.path.dirname(os.path.dirname(data_folder))
    
    data_dir, processed_dir, graph_dir = get_directories(project_dir, brand)
    
    # Load files using your select_file.py
    loader = DataLoader()
    loader.load_files(brand, data_folder, category, recursive=True)
    
    entries = loader.get_dataframes(brand, category)
    
    if not entries:
        print(f"❌ No files found in {data_folder}")
        return pd.DataFrame()
    
    print(f"\n📁 Found {len(entries)} files to process")
    print("=" * 60)
    
    results = []
    pdf_entries = []
    
    for idx, entry in enumerate(entries):
        filename = entry['filename']
        file_path = entry['path']
        df = entry['dataframe']
        
        print(f"\n[{idx+1}/{len(entries)}] Processing: {filename}")
        
        try:
            # Get power information
            num, power_mW, I0 = get_power_and_irradiance(file_path, w0)
            
            # 1. Save ORIGINAL dataframe
            if save_intermediate:
                original_path = os.path.join(data_dir, f"{num}.csv")
                df.to_csv(original_path, index=False)
                print(f"   💾 Saved original: {os.path.basename(original_path)}")
            # Process file
            result = process_single_file(df, file_path, w0, z0, sample_length, group_size, z_range)
            
            # Save processed CSV
            csv_path = save_processed_data(result['processed_df'], 
                                          result['num'], 
                                          result['power_mW'], 
                                          processed_dir)
            print(f"   ✅ Saved CSV: {os.path.basename(csv_path)}")
            
            # Save individual plot
            plot_path = plot_single_result(result['processed_df'], result, 
                                          filename, brand, graph_dir)
            print(f"   ✅ Saved plot: {os.path.basename(plot_path)}")
            
            # Convert W/m² to GW/m² (1 GW/m² = 1e9 W/m²)
            irradiance_GW = result['I0'] / 1e9

            # Calculate values in mm
            sample_length_mm = (sample_length * 1000) if sample_length else 0
            rayleigh_range_mm = z0 * 1000
            beam_waist_micro_m = w0 * 1e6
            

            # Store results
            results.append({
                'num': result['num'],
                'power_mW': round(result['power_mW'], 2),
                'irradiance_GW_m2': round(result['I0'] / 1e9, 4),
                'beam_waist_micro_m': round(beam_waist_micro_m, 4),
                'sample_length_mm': round(sample_length_mm, 3),
                'rayleigh_range_mm': round(rayleigh_range_mm, 3),
                'x_pred': round(result['x_pred'], 4),
                'delphi': round(result['fit_delphi'], 4),
                'abs_delphi': round(result['fit_stats']['abs_delphi'], 4),
                'delphi_err': round(result['fit_delphi_err'], 4),
    
                # ===== ADD Zpv and Tpv HERE =====
                'Zpv_mm': round(result['fit_stats']['Zpv'] * 1000, 4),  # Zpv in mm
                'Tpv': round(result['fit_stats']['Tpv'], 4),       # Tpv (peak-to-valley height)
    
                'R_sq_reg': round(result['fit_stats']['R_sq_reg'], 2),
                'R_sq_pearson': round(result['fit_stats']['R_sq_pearson'], 2),
                'R_sq_sklearn': round(result['fit_stats']['R_sq_sklearn'], 2),
                'RMSE': round(result['fit_stats']['RMSE'], 6),
                'MAE': round(result['fit_stats']['MAE'], 6),
                'MAPE (%)': round(result['fit_stats']['MAPE (%)'], 2),
                'chi_sq': round(result['fit_stats']['chi_sq'], 2),
                })            \
            # # Store results
            # results.append({
            #     'filename': filename,
            #     'filepath': os.path.dirname(file_path),
            #     'num': result['num'],
            #     'power_mW': result['power_mW'],
            #     'irradiance_W_m2': result['I0'],
            #     'x_pred': result['x_pred'],
            #     'delphi': result['fit_delphi'],
            #     'abs_delphi': result['fit_stats']['abs_delphi'],
            #     'delphi_err': result['fit_delphi_err'],
            #     **result['fit_stats']
            # })
            
            # Store for PDF
            pdf_entries.append({
                'processed_df': result['processed_df'],
                'fit_result': result,
                'filename': filename,
                'power_mW': result['power_mW']
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    # Save results CSV
    if results:
        results_df = pd.DataFrame(results)
        results_csv = os.path.join(project_dir, f"{brand}_results.csv")
        results_df.to_csv(results_csv, index=False)
        print(f"\n📊 Saved results CSV: {results_csv}")
        
        # Create multi-page PDF
        pdf_path = os.path.join(project_dir, f"{brand}_analysis.pdf")
        # create_multipage_pdf(pdf_entries, pdf_path)
        create_multipage_pdf(pdf_entries, pdf_path, 
                     rows=4, cols=2, 
                     page_title=f'{brand} - Z-Scan Analysis',
                     brand=brand)
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"✅ ANALYSIS COMPLETE FOR {brand.upper()}")
        print("=" * 60)
        print(f"   Processed: {len(results)}/{len(entries)} files")
        print(f"   Results: {results_csv}")
        print(f"   PDF: {pdf_path}")
        print(f"   Graphs: {graph_dir}")
        
        # Display summary stats
        print("\n📈 SUMMARY STATISTICS:")
        print(results_df[['num', 'power_mW', 'abs_delphi', 'delphi_err', 
                         'R_sq_reg']].to_string(index=False))
        
        return results_df
    else:
        print("\n❌ No files were successfully processed")
        return pd.DataFrame()