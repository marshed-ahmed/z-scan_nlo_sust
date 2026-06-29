"""
File selection and loading module for experimental data.

This module provides functionality to categorize, sort, and load different types
of data files (CSVs, images) organized by brand/category.
"""

import os
import re
import pandas as pd
from collections import defaultdict

# Module-level logger (optional but recommended)
import logging
logger = logging.getLogger(__name__)

# Constants
CATEGORY_MAP = {
    'calculated': 'Calculated CSVs',
    'csv': 'Regular CSVs',
    'ca_oa': 'CA/OA CSVs',
    'png': 'PNG Images',
    'svg': 'SVG Images',
    'other': 'Other Files'
}

VALID_CATEGORIES = ['calculated', 'csv', 'ca_oa', 'png', 'svg', 'other']


class DataLoader:
    """
    A class to manage loading and accessing data files by brand and category.
    
    This replaces the global `category_dataframes` variable to avoid state issues
    when importing the module multiple times.
    
    Example:
    --------
    >>> loader = DataLoader()
    >>> loader.load_files('BrandX', '/path/to/data', 'ca_oa')
    >>> df_list = loader.get_dataframes('BrandX', 'ca_oa')
    """
    
    def __init__(self):
        """Initialize an empty data store."""
        self._data = defaultdict(lambda: defaultdict(list))
    
    def reset(self, brand_name=None, category=None):
        """
        Reset stored data.
        
        Parameters:
        -----------
        brand_name : str or None
            If provided, reset only this brand. If None, reset everything.
        category : str or None
            If provided with brand_name, reset only this category.
        """
        if brand_name is None:
            self._data.clear()
        elif category is None:
            self._data[brand_name].clear()
        else:
            self._data[brand_name][category] = []
    
    def categorize_files(self, files):
        """
        Categorize files based on their extensions/names.
        
        Parameters:
        -----------
        files : list of str
            List of file paths
            
        Returns:
        --------
        dict
            Dictionary mapping category keys to lists of file paths
        """
        categories = defaultdict(list)
        for file in files:
            fname = os.path.basename(file).lower()
            if fname.endswith('_calculated.csv'):
                categories['calculated'].append(file)
            elif fname.endswith('_ca_oa.csv'):
                categories['ca_oa'].append(file)
            elif fname.endswith('.csv'):
                categories['csv'].append(file)
            elif fname.endswith('.png'):
                categories['png'].append(file)
            elif fname.endswith('.svg'):
                categories['svg'].append(file)
            else:
                categories['other'].append(file)
        return categories
    
    @staticmethod
    def number_then_alpha_key(file_path):
        """
        Sort key: extract number from filename, then sort alphabetically.
        
        Returns:
        --------
        tuple
            (number, lowercase_filename) where number is int or float('inf')
        """
        filename = os.path.splitext(os.path.basename(file_path))[0]
        match = re.search(r'\d+', filename)
        number = int(match.group()) if match else float('inf')
        return (number, filename.lower())
    
    def _process_file(self, file_path, category_key, brand_name):
        """
        Process a single file: load if CSV, store reference otherwise.
        
        Parameters:
        -----------
        file_path : str
            Path to the file
        category_key : str
            Category of the file ('calculated', 'csv', 'ca_oa', etc.)
        brand_name : str
            Brand identifier
        """
        filename = os.path.basename(file_path)
        df = None
        
        try:
            # Load based on file type
            if file_path.endswith('_calculated.csv'):
                df = pd.read_csv(file_path)
                logger.info(f"Loaded calculated CSV: {filename}")
                
            elif file_path.endswith('_ca_oa.csv'):
                df = pd.read_csv(file_path, header=None, usecols=[0, 1], names=['ca', 'oa'])
                logger.info(f"Loaded CA/OA CSV: {filename}")
                
            elif file_path.endswith('.csv') and category_key == 'csv':
                df = pd.read_csv(file_path)
                logger.info(f"Loaded CSV: {filename} (shape: {df.shape})")
                
            elif file_path.endswith(('.png', '.svg')):
                # Image files - don't load, just store reference
                logger.info(f"Found image file: {filename}")
                
            else:
                logger.debug(f"Skipping file: {filename}")
            
            # Store in data structure
            self._data[brand_name][category_key].append({
                'filename': filename,
                'dataframe': df,
                'path': file_path
            })
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            # Still store a reference with error info
            self._data[brand_name][category_key].append({
                'filename': filename,
                'dataframe': None,
                'path': file_path,
                'error': str(e)
            })
    
    def load_files(self, brand_name, folder_path, category_key, recursive=True):
        """
        Load all files of a specific category from a folder.
        
        Parameters:
        -----------
        brand_name : str
            Brand identifier for organizing loaded data
        folder_path : str
            Directory to search
        category_key : str
            One of: 'calculated', 'csv', 'ca_oa', 'png', 'svg', 'other'
        recursive : bool
            If True, search subdirectories recursively
            
        Returns:
        --------
        self
            Returns self for method chaining
            
        Raises:
        -------
        FileNotFoundError
            If folder_path doesn't exist
        ValueError
            If category_key is invalid
        """
        folder_path = os.path.abspath(folder_path)
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Path does not exist: {folder_path}")
        
        if category_key not in VALID_CATEGORIES:
            raise ValueError(f"category_key must be one of {VALID_CATEGORIES}, got '{category_key}'")
        
        # Find all matching files
        matched_files = []
        
        if recursive:
            for root, _, files in os.walk(folder_path):
                full_paths = [os.path.join(root, f) for f in files]
                categories = self.categorize_files(full_paths)
                if category_key in categories:
                    matched_files.extend(categories[category_key])
        else:
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            full_paths = [os.path.join(folder_path, f) for f in files]
            categories = self.categorize_files(full_paths)
            if category_key in categories:
                matched_files.extend(categories[category_key])
        
        if not matched_files:
            logger.warning(f"No files found for category '{category_key}' in {folder_path}")
            return self
        
        # Sort files
        matched_files = sorted(matched_files, key=self.number_then_alpha_key)
        
        # Process each file
        for fpath in matched_files:
            self._process_file(fpath, category_key, brand_name)
        
        logger.info(f"Loaded {len(self._data[brand_name][category_key])} files "
                   f"under brand '{brand_name}', category '{category_key}'")
        
        return self
    
    def get_dataframes(self, brand_name=None, category=None):
        """
        Retrieve loaded dataframes.
        
        Parameters:
        -----------
        brand_name : str or None
            If provided, return only this brand's data. If None, return all.
        category : str or None
            If provided with brand_name, return only specific category.
            
        Returns:
        --------
        dict or list
            Depending on parameters:
            - (None, None): dict of all brands
            - (brand, None): dict of categories for that brand
            - (brand, category): list of file dicts for that brand/category
        """
        if brand_name is None:
            return dict(self._data)
        
        if brand_name not in self._data:
            return {} if category is None else []
        
        if category is None:
            return dict(self._data[brand_name])
        
        return list(self._data[brand_name].get(category, []))
    
    def get_dataframe_by_number(self, brand_name, category, number):
        """
        Get a specific dataframe by extracting number from filename.
        
        Parameters:
        -----------
        brand_name : str
        category : str
        number : int
            The number to match in filename
            
        Returns:
        --------
        dict or None
            The file dict containing 'filename', 'dataframe', 'path'
        """
        files = self._data[brand_name].get(category, [])
        for file_dict in files:
            match = re.search(r'\d+', file_dict['filename'])
            if match and int(match.group()) == number:
                return file_dict
        return None
    
    def get_dataframes_by_number_range(self, brand_name, category, start_num, end_num):
        """
        Get dataframes whose extracted numbers fall within a range.
        
        Parameters:
        -----------
        brand_name : str
        category : str
        start_num : int
        end_num : int (inclusive)
        
        Returns:
        --------
        list
            List of file dicts matching the number range
        """
        files = self._data[brand_name].get(category, [])
        filtered = []
        for file_dict in files:
            match = re.search(r'\d+', file_dict['filename'])
            if match:
                num = int(match.group())
                if start_num <= num <= end_num:
                    filtered.append(file_dict)
        return filtered
    
    def get_summary(self):
        """
        Get a summary of all loaded data.
        
        Returns:
        --------
        dict
            Nested dictionary with counts per brand and category
        """
        summary = {}
        for brand, categories in self._data.items():
            summary[brand] = {}
            for cat, files in categories.items():
                summary[brand][cat] = len(files)
        return summary
    
    def validate_integrity(self, brand_name, category):
        """
        Check for missing or corrupted files in loaded data.
        
        Returns:
        --------
        list
            List of issues found
        """
        issues = []
        files = self._data[brand_name].get(category, [])
        
        for file_dict in files:
            path = file_dict.get('path')
            if not path or not os.path.exists(path):
                issues.append(f"Missing file: {file_dict['filename']}")
            elif file_dict.get('dataframe') is None and file_dict['filename'].endswith('.csv'):
                if 'error' in file_dict:
                    issues.append(f"Load error for {file_dict['filename']}: {file_dict['error']}")
                else:
                    issues.append(f"DataFrame not loaded: {file_dict['filename']}")
        
        return issues
    
    def print_summary(self):
        """Print a human-readable summary of loaded data."""
        summary = self.get_summary()
        if not summary:
            print("No data loaded.")
            return
        
        for brand, categories in summary.items():
            print(f"\n📁 Brand: {brand}")
            for cat, count in categories.items():
                display_name = CATEGORY_MAP.get(cat, cat)
                print(f"   {display_name}: {count} files")


# For backward compatibility, create a default instance
_default_loader = None

def get_loader():
    """
    Get the default DataLoader instance (singleton pattern).
    
    Use this for simple scripts; create your own DataLoader instance
    for more complex applications.
    """
    global _default_loader
    if _default_loader is None:
        _default_loader = DataLoader()
    return _default_loader


# Backward compatibility functions (for existing code)
def categorize_files(files):
    """Backward compatibility wrapper."""
    return get_loader().categorize_files(files)

def number_then_alpha_key(file_path):
    """Backward compatibility wrapper."""
    return DataLoader.number_then_alpha_key(file_path)

def process_file_with_brand(file_path, category_key, brand_name):
    """Backward compatibility wrapper."""
    return get_loader()._process_file(file_path, category_key, brand_name)

def load_category_files(brand_name, folder_path, category_key):
    """Backward compatibility wrapper."""
    return get_loader().load_files(brand_name, folder_path, category_key)

def get_dataframes(brand_name=None, category=None):
    """Backward compatibility wrapper."""
    return get_loader().get_dataframes(brand_name, category)

# Export the main class and helper functions
__all__ = [
    'DataLoader',
    'get_loader',
    'CATEGORY_MAP',
    'VALID_CATEGORIES',
    # Backward compatibility
    'categorize_files',
    'number_then_alpha_key',
    'process_file_with_brand',
    'load_category_files',
    'get_dataframes'
]