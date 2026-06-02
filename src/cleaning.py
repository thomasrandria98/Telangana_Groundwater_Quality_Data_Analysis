# cleaning.py
# Loads, inspects, standardises, and combines the 2018–2020 groundwater datasets.

import pandas as pd


# ── Data Loading ──────────────────────────────────────────────────────────────

def load_data():
    """Read the three annual CSV files and return them as separate DataFrames."""
    data_2018 = pd.read_csv("../Data/ground_water_quality_2018_post.csv")
    data_2019 = pd.read_csv("../Data/ground_water_quality_2019_post.csv")
    data_2020 = pd.read_csv("../Data/ground_water_quality_2020_post.csv")
    return data_2018, data_2019, data_2020


# ── Inspection ────────────────────────────────────────────────────────────────

def inspect_data(data_2018, data_2019, data_2020):
    """Print shape, dtypes, and the first few rows of each annual dataset."""
    for year, df in [("2018", data_2018), ("2019", data_2019), ("2020", data_2020)]:
        print(f"\n--- {year} Dataset Info ---")
        df.info()
        print(df.head())


# ── Column Standardisation ────────────────────────────────────────────────────

def compare_columns(data_2018, data_2019, data_2020):
    """
    Compare column names across the three datasets and report any differences.
    Returns True if all three column sets are identical.
    """
    col_2018 = set(data_2018.columns)
    col_2019 = set(data_2019.columns)
    col_2020 = set(data_2020.columns)

    all_match = col_2018 == col_2019 == col_2020
    print(f"All columns match: {all_match}")
    print("Only in 2018:", col_2018 - col_2019 - col_2020)
    print("Only in 2019:", col_2019 - col_2020 - col_2018)
    print("Only in 2020:", col_2020 - col_2018 - col_2019)
    print("\nSorted 2018 columns:", sorted(col_2018))
    print("Sorted 2019 columns:", sorted(col_2019))
    print("Sorted 2020 columns:", sorted(col_2020))
    return all_match


def standardise_2019_columns(data_2019):
    """
    Rename 2019 columns to match the 2018/2020 naming convention.
    The 2019 file uses different spacing and notation for several analytes.
    """
    column_rename = {
        "CO_-2 ": "CO3",
        "Ca+2":   "Ca",
        "Cl -":   "Cl",
        "EC":     "E.C",
        "F -":    "F",
        "HCO_ - ":"HCO3",
        "K+":     "K",
        "Mg+2":   "Mg",
        "NO3- ":  "NO3 ",
        "Na+":    "Na",
        "SO4-2":  "SO4",
    }
    return data_2019.rename(columns=column_rename)


# ── Concatenating the 3 datasets───────────────────────────────────────────────────────────────

def combine_data(data_2018, data_2019, data_2020):
    """Concatenate the three annual DataFrames into one, resetting the index."""
    return pd.concat([data_2018, data_2019, data_2020], ignore_index=True)


# ── Public helper (imported by analysis.py and visualisation.py) ──────────────

def get_combined_data():
    """
    Full pipeline: load → standardise → combine.
    Returns the merged DataFrame ready for analysis.
    """
    data_2018, data_2019, data_2020 = load_data()
    data_2019 = standardise_2019_columns(data_2019)
    return combine_data(data_2018, data_2019, data_2020)


# ── Script entry-point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    data_2018, data_2019, data_2020 = load_data()

    inspect_data(data_2018, data_2019, data_2020)
    compare_columns(data_2018, data_2019, data_2020)

    data_2019 = standardise_2019_columns(data_2019)
    compare_columns(data_2018, data_2019, data_2020)

    combined_df = combine_data(data_2018, data_2019, data_2020)
    combined_df.to_csv("../Data/combined_data.csv", index=False)

    print("\nMissing values per column:")
    print(combined_df.isnull().sum())


