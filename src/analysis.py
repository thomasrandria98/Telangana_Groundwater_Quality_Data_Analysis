# analysis.py
# Spatial aggregation and district-level groundwater analysis.
# Depends on cleaning.py for the combined dataset.

import pandas as pd
import geopandas as gpd

from cleaning import get_combined_data

# ── Constants ─────────────────────────────────────────────────────────────────

ANALYTE_COLUMNS = [
    "gwl", "pH", "E.C", "TDS", "CO3", "HCO3",
    "NO3 ", "K", "Na", "Ca", "Mg", "Cl", "SO4", "SAR",
]

# Districts that fall outside the Telangana study area
OUTSIDE_STUDY_AREA = {
    "ALLURI SITARAMA RAJU", "CHANDRAPUR", "ELURU", "GADCHIROLI",
    "HANUMAKONDA", "KALABURAGI", "KURNOOL", "NANDED", "NANDYAL",
    "NTR", "PALNADU", "PRAKASAM", "RAICH#R", "SUKMA", "Y<DGIR", "YAVATMAL",
}

# Polygon → groundwater naming corrections
DISTRICT_NAME_MAP = {
    "BHADRADRI KOTHAGUDEM": "BHADRADRI",
    "JAGTIAL":              "JAGITYAL",
    "JAYASHANKAR BHUPALPALLI": "BHUPALPALLY",
    "JOGULAMBA GADWAL":     "JOGULAMBA(GADWAL)",
    "MEDCHAL-MALKAJGIRI":   "MEDCHAL",
    "RANGA REDDY":          "RANGAREDDY",
    "PEDDAPALLI":           "PEDDAPALLY",
    "RAJANNA SIRCILLA":     "SIRCILLA",
    "WARANGAL":             "WARANGAL",
    "YADADRI BHUVANAGIRI":  "YADADRI",
    "MAHBUBNAGAR":          "MAHABUBNAGAR",
}

# Groundwater rows with split district names that need merging
WARANGAL_MERGE = {"WARANGAL (R)": "WARANGAL", "WARANGAL (U)": "WARANGAL"}


# ── GeoDataFrame Construction ─────────────────────────────────────────────────

def build_geodataframe(combined_df):
    """
    Convert the combined DataFrame to a GeoDataFrame using lat/long columns,
    cast analyte columns to numeric, and return it.
    """
    gdf = gpd.GeoDataFrame(
        combined_df,
        geometry=gpd.points_from_xy(combined_df.long_gis, combined_df.lat_gis),
        crs="EPSG:4326",
    )
    gdf[ANALYTE_COLUMNS] = gdf[ANALYTE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    return gdf


# ── District Summary Data  ──────────────────────────────────────────────────────────

def build_district_summary(gdf):
    """
    Group point data by district and calculate the mean for each analyte.
    Also merges split Warangal entries before aggregation.
    Returns a plain DataFrame indexed by district name (upper-case).
    """
    gdf = gdf.copy()
    gdf["district"] = gdf["district"].str.strip().replace(WARANGAL_MERGE)
    summary = gdf.groupby("district")[ANALYTE_COLUMNS].mean().reset_index()
    return summary


# ── Loading District Polygons and Standardising District names to match GW dataset ────────────────────────────────────────────────────────

def load_district_polygons(gpkg_path):
    """
    Read district boundary polygons from a GeoPackage, filter to the study
    area, and standardise district names to match the groundwater dataset.
    Returns a GeoDataFrame.
    """
    districts = gpd.read_file(gpkg_path)

    # Remove districts outside the study area
    districts = districts[
        ~districts["DISTRICT"].str.upper().isin(OUTSIDE_STUDY_AREA)
    ].copy()

    # Standardise names
    districts["DISTRICT"] = (
        districts["DISTRICT"].str.upper().replace(DISTRICT_NAME_MAP)
    )
    return districts


def report_district_mismatches(district_summary, districts_ts):
    """Print any district names present in one dataset but not the other."""
    gw = set(district_summary["district"].str.upper())
    poly = set(districts_ts["DISTRICT"])
    print("Groundwater only:", sorted(gw - poly))
    print("Polygon only:",     sorted(poly - gw))


# ── Spatial Join ──────────────────────────────────────────────────────────────

def merge_summary_with_polygons(districts_ts, district_summary):
    """
    Left-join district mean analyte values onto the polygon GeoDataFrame.
    Returns a GeoDataFrame ready for mapping.
    """
    return districts_ts.merge(
        district_summary,
        left_on="DISTRICT",
        right_on="district",
    )


# ── District-Level Filter ─────────────────────────────────────────────────────

def filter_by_district(gdf, district_name):
    """Return all point records belonging to the specified district."""
    return gdf[gdf["district"] == district_name].copy()


# ── Script entry-point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    GPKG_PATH = "../Data/District_boundary_Clipped_to_Study_Area.gpkg"
    CHOSEN_DISTRICT = "NAGARKURNOOL"

    combined_df = get_combined_data()

    gdf = build_geodataframe(combined_df)
    district_summary = build_district_summary(gdf)
    print(district_summary.head())

    districts_ts = load_district_polygons(GPKG_PATH)
    report_district_mismatches(district_summary, districts_ts)

    combined_district_map = merge_summary_with_polygons(districts_ts, district_summary)

    chosen_district_df = filter_by_district(gdf, CHOSEN_DISTRICT)
    print(f"\n{CHOSEN_DISTRICT} sample count: {len(chosen_district_df)}")
