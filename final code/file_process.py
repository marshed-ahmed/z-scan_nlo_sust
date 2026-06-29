import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
from scipy import stats
import os

def normalize_ca_oa(df, head_tail_size=300):
    """
    Normalize 'ca' and 'oa' columns in a DataFrame by the mean of 
    the first and last `head_tail_size` rows, then remove rows with zeros in normalized data.

    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame containing 'ca' and 'oa' columns.
    head_tail_size : int, optional
        Number of rows to use from the start and end for mean calculation. Default is 100.

    Returns:
    --------
    pd.DataFrame
        DataFrame with two new columns: 'normalized_ca' and 'normalized_oa',
        with rows containing zeros in these columns removed.
    """
    df = df.copy()
    # Normalize the 'ca' and 'oa' columns separately
    df['ca/oa'] = df['ca'] / df['oa']
    
    mean_ca = pd.concat([df['ca'].head(head_tail_size), df['ca'].tail(head_tail_size)]).mean()
    mean_oa = pd.concat([df['oa'].head(head_tail_size), df['oa'].tail(head_tail_size)]).mean()
    mean_ca_oa = pd.concat([df['ca/oa'].head(head_tail_size), df['ca/oa'].tail(head_tail_size)]).mean()

    df['normalized_ca'] = df['ca'] / mean_ca
    df['normalized_oa'] = df['oa'] / mean_oa
    df['normalized_ca/oa'] = df['ca/oa'] / mean_ca_oa

    df_nonzero = df[(df['normalized_ca'] != 0) & (df['normalized_oa'] != 0)]

    return df_nonzero

def get_Z(df, start_idx=4000, end_idx=6000):
    """
    Compute transformed x positions ('x_position') based on normalized_ca column between min and max values
    in a slice of the DataFrame and polynomial fitting.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing 'normalized_ca' and default integer index.
    start_idx : int, optional
        Start index (inclusive) for slicing normalized_ca (default 4000).
    end_idx : int, optional
        End index (exclusive) for slicing normalized_ca (default 6000).

    Returns:
    --------
    df : pd.DataFrame
        Original DataFrame with a new column 'x_position' containing transformed x values.
    x_pred : float
        The predicted x value from the linear fit used for transformation.
    """
    # Step 1: Slice subset
    subset = df['normalized_ca/oa'].iloc[start_idx:end_idx]

    # Step 2: Find min, max and their indices in original df index space
    min_val = subset.min()
    max_val = subset.max()
    min_pos = subset.idxmin()
    max_pos = subset.idxmax()

    # Step 3: Extract values between max_pos and min_pos (order agnostic)
    start_slice = min(min_pos, max_pos)
    end_slice = max(min_pos, max_pos)
    between_values = df.loc[start_slice:end_slice, 'normalized_ca/oa']

    df_between = pd.DataFrame({
        'x': between_values.index,
        'normalized_ca/oa': between_values.values
    })

    # Step 4: Crop middle 80% (remove 10% from each end)
    n = len(df_between)
    drop_count = int(0.1 * n)
    # Slice the DataFrame to keep middle 80%
    cropped_df = df_between.iloc[drop_count : n - drop_count]
    # Step 5: Fit linear regression to cropped data
    mid_data_x = cropped_df['x'].values
    mid_data_y = cropped_df['normalized_ca/oa'].values
    coefficients = np.polyfit(mid_data_y, mid_data_x, 1)  # degree 1 polynomial
    slope = coefficients[0]
    intercept = coefficients[1]

    # Step 6: Calculate x_pred from regression parameters
    x_pred = slope * 1 + intercept

    # Step 7: Transform entire df index using x_pred
    x = df.index.to_numpy()
    df = df.copy()
    df['z'] = (x - x_pred) * 1e-5
    return df, x_pred

def transform_Z(df, col='normalized_ca/oa_mean', x_col='x_position',
                subset_range=(-0.02, 0.02), drop_frac=0.1):
    """
    Transform x positions based on a normalized column using linear regression
    between min and max values in a subset of the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing the column to analyze and x positions.
    col : str
        Column name to use for min/max detection and regression.
    x_col : str
        Column representing x positions (default 'x_position').
    subset_range : tuple of float
        (min_x, max_x) range to subset the DataFrame before min/max detection.
    drop_frac : float
        Fraction of rows to drop from both ends after slicing between min and max (default 0.1).

    Returns
    -------
    df_transformed : pd.DataFrame
        Copy of original DataFrame with transformed x positions in `x_col`.
    x_pred : float
        Predicted x value from the linear regression used for transformation.
    """

    # Step 1: Subset DataFrame
    subset = df[(df[x_col] > subset_range[0]) & (df[x_col] < subset_range[1])]

    # Step 2: Find min/max positions
    min_pos = subset[col].idxmin()
    max_pos = subset[col].idxmax()
    start_idx, end_idx = sorted([min_pos, max_pos])

    # Step 3: Extract values between min and max positions
    between_values = df.loc[start_idx:end_idx, [col, x_col]].copy()
    between_values.rename(columns={x_col: 'x'}, inplace=True)

    # Step 4: Crop middle portion
    n = len(between_values)
    drop_count = int(drop_frac * n)
    cropped_df = between_values.iloc[drop_count : n - drop_count]

    # Step 5: Linear regression (y vs x)
    mid_data_x = cropped_df['x'].values
    mid_data_y = cropped_df[col].values
    slope, intercept = np.polyfit(mid_data_x, mid_data_y, 1)

    # Step 6: Predict x where y = 1
    x_pred = (1 - intercept) / slope

    # Step 7: Transform x_col in original DataFrame
    df_transformed = df.copy()
    df_transformed[x_col] = df_transformed[x_col] - x_pred

    return df_transformed, x_pred

def smooth_signal(df, group_size, x_col, y_cols):
    grouped = df.copy()
    grouped['group'] = grouped.index // group_size

    # Build aggregation dictionary
    agg_dict = {x_col: 'median'}
    for col in y_cols:
        agg_dict[col] = ['mean', 'std']

    reduced_df = grouped.groupby('group').agg(agg_dict).reset_index(drop=True)

    # Flatten column names
    reduced_df.columns = ['z'] + [f'{col}_{stat}' for col in y_cols for stat in ['mean', 'std']]

    return reduced_df

def select_range(df, col, lower_bound, upper_bound):
    filtered_df = df[(df[col] > lower_bound) & (df[col] < upper_bound)]
    return filtered_df

def get_power_and_irradiance(file_path, w0):
    """
    Extract the number from the filename and compute laser power and irradiance.
    
    Parameters:
    -----------
    file_path : str
        Path to the file, e.g. '123_ca.csv'
    w0 : float
        Beam waist radius (in meters).
    
    Returns:
    --------
    tuple
        (pwr_mW, I0_W_per_m2)
        
    Raises:
    -------
    ValueError
        If filename format is unexpected or number part cannot be parsed.
    """
    base = os.path.basename(file_path)
    name, _ = os.path.splitext(base)
    
    if '_' not in name:
        raise ValueError(f"Filename '{name}' does not contain an underscore (_) to split number and suffix.")
    
    parts = name.split('_', 1)
    number_str = parts[0]
    
    try:
        num = int(number_str)
    except ValueError:
        raise ValueError(f"Number part '{number_str}' in filename '{name}' is not a valid integer.")
    
    pwr_mW = (-1467) + (12.6 * num) - (0.0242 * num * num)
    pwr_W = pwr_mW * 0.001
    
    I0 = pwr_W / (np.pi * (w0 ** 2))
    
    return num, pwr_mW, I0

def compute_fit_stats(Yax, Yax2, sigma=None, n_params=None):
    """
    Compute fit statistics between observed (Yax) and predicted (Yax2) values.

    Args:
        Yax       : array-like, observed values
        Yax2      : array-like, predicted/fitted values
        sigma     : array-like or None, uncertainties for each point (default: 1)
        n_params  : int or None, number of fitted parameters (for reduced chi-squared)

    Returns:
        dict with:
            - R_sq_reg       : R^2 from regression formula
            - R_sq_pearson   : R^2 from Pearson correlation
            - R_sq_sklearn   : R^2 from sklearn.metrics.r2_score
            - percent        : R^2 (sklearn) in percentage
            - Y_diff         : Absolute differences
            - RMSE           : Root Mean Squared Error
            - MAE            : Mean Absolute Error
            - MAPE (%)       : Mean Absolute Percentage Error
            - chi_sq         : Chi-squared
            - chi_sq_red     : Reduced chi-squared (if n_params given)
    """
    Yax = np.array(Yax, dtype=float)
    Yax2 = np.array(Yax2, dtype=float)

    if Yax.shape != Yax2.shape:
        raise ValueError("Input arrays must have the same shape.")

    # Differences
    diff = Yax - Yax2
    Y_diff = np.std(diff)

    # ---- R² (3 versions) ----
    total_variance = np.sum((Yax - np.mean(Yax)) ** 2)
    residual_variance = np.sum(diff ** 2)
    R_sq_reg = 1 - (residual_variance / total_variance) if total_variance != 0 else 1.0
    R_sq_reg= R_sq_reg*100
    
    r_value, _ = stats.pearsonr(Yax, Yax2)
    R_sq_pearson = r_value ** 2
    R_sq_pearson= R_sq_pearson*100

    R_sq_sklearn = r2_score(Yax, Yax2)
    R_sq_sklearn = R_sq_sklearn * 100

    # ---- Error metrics ----
    RMSE = np.sqrt(np.mean(diff ** 2))
    MAE = np.mean(np.abs(diff))
    MAPE = np.mean(np.abs(diff / Yax)) * 100 if np.all(Yax != 0) else np.nan

    # ---- Chi-squared ----
    if sigma is None:
        sigma = np.ones_like(Yax)
    else:
        sigma = np.array(sigma, dtype=float)
        if sigma.shape != Yax.shape:
            raise ValueError("sigma must have the same shape as Yax")

    chi_sq = np.sum((diff / sigma) ** 2)
    
    return {
        'Y_diff': Y_diff,
        'R_sq_reg': R_sq_reg,
        'R_sq_pearson': R_sq_pearson,
        'R_sq_sklearn': R_sq_sklearn,
        'RMSE': RMSE,
        'MAE': MAE,
        'MAPE (%)': MAPE,
        'chi_sq': chi_sq
    }
