# visualisation.py
# All plotting and mapping for the groundwater quality project.
# Depends on cleaning.py and analysis.py.

import matplotlib.pyplot as plt

from cleaning import get_combined_data
from analysis import (
    ANALYTE_COLUMNS,
    build_geodataframe,
    build_district_summary,
    load_district_polygons,
    merge_summary_with_polygons,
    filter_by_district,
)

# ── Constants ─────────────────────────────────────────────────────────────────

GPKG_PATH       = "../Data/District_boundary_Clipped_to_Study_Area.gpkg"
CHOSEN_DISTRICT = "NAGARKURNOOL"
FIGURES_DIR     = "../Figures/"
GRAPHS_DIR      = "../Graphs/"


# ── Classification Bar Chart ──────────────────────────────────────────────────

def plot_classification_frequency(combined_df):
    """Bar chart showing how many samples fall into each water-quality class."""
    counts = combined_df["Classification"].value_counts()

    plt.figure(figsize=(10, 6))
    plt.bar(counts.index, counts.values)
    plt.xlabel("Groundwater Classification")
    plt.ylabel("Number of Samples")
    plt.title("Groundwater Classification Frequency")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}Groundwater_Classification_Frequency.png")
    plt.show()


# ── Choropleth Maps ───────────────────────────────────────────────────────────

def plot_district_choropleth(combined_district_map, column, label,
                             vmin, vmax, title, filename):
    """
    Generic helper: draw a choropleth map for any analyte column and save it.
    """
    ax = combined_district_map.plot(
        column=column,
        legend=True,
        cmap="YlOrRd",
        legend_kwds={"label": label, "orientation": "vertical"},
        vmin=vmin,
        vmax=vmax,
    )
    ax.set_title(title, fontsize=12, pad=15)
    plt.savefig(f"{FIGURES_DIR}{filename}")
    plt.show()


def plot_tds_map(combined_district_map):
    plot_district_choropleth(
        combined_district_map,
        column="TDS",
        label="TDS (mg/L)",
        vmin=0, vmax=2000,
        title="Average Groundwater TDS by District (Telangana) 2018–2020",
        filename="Mean_TDS_per_District.png",
    )


def plot_nitrate_map(combined_district_map):
    plot_district_choropleth(
        combined_district_map,
        column="NO3 ",
        label="Nitrate (mg/L)",
        vmin=0, vmax=400,
        title="Average Groundwater Nitrate Concentrations by District (Telangana) 2018–2020",
        filename="Mean_Nitrate_per_District.png",
    )


# ── District Bar Charts ───────────────────────────────────────────────────────

def plot_district_bar(district_summary, column, ylabel):
    """Horizontal bar chart ranking all districts by a single analyte mean."""
    district_summary.sort_values(by=column, ascending=False).plot.bar(
        x="district", y=column
    )
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.show()


# ── Per-Well Time Series ──────────────────────────────────────────────────────

def plot_well_nitrate_timeseries(combined_df, district_name=CHOSEN_DISTRICT):
    """
    For every monitoring well in the chosen district, plot nitrate (NO3)
    concentration over time and save the figure to GRAPHS_DIR.
    """
    # Extract year from the 'season' column  (e.g. "POST MONSOON 2019" → "2019")
    combined_df = combined_df.copy()
    combined_df["year"] = combined_df["season"].str.split().str[-1]

    district_df = combined_df[combined_df["district"] == district_name]
    wells = district_df["sno"].unique().tolist()

    for well in wells:
        well_df = district_df[district_df["sno"] == well].sort_values("year")

        plt.figure(figsize=(8, 4))
        plt.style.use("default")
        plt.plot(well_df["year"], well_df["NO3 "], marker="o")
        plt.grid(True)
        plt.title(f"Well {well} — {district_name}")
        plt.ylabel("Nitrate (mg/L)")
        plt.xlabel("Year")
        plt.tight_layout()
        plt.savefig(f"{GRAPHS_DIR}well_{well}.png", dpi=300)
        plt.show()
        plt.close()


# ── District Point Maps & Histograms ─────────────────────────────────────────

def plot_district_spatial(chosen_district_gdf):
    """Scatter map of all sample points in the chosen district."""
    chosen_district_gdf.plot()
    plt.title(f"Sample Locations — {CHOSEN_DISTRICT}")
    plt.show()


def plot_analyte_spatial_and_hist(chosen_district_gdf, column, label, cmap="YlOrRd"):
    """Choropleth scatter + histogram for a single analyte within a district."""
    chosen_district_gdf.plot(column=column, legend=True, cmap=cmap)
    plt.title(f"{label} — {CHOSEN_DISTRICT}")
    plt.show()

    chosen_district_gdf[column].hist(bins=20)
    plt.xlabel(label)
    plt.title(f"{label} Distribution — {CHOSEN_DISTRICT}")
    plt.tight_layout()
    plt.show()


# ── Script entry-point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Load and prepare data
    combined_df     = get_combined_data()
    gdf             = build_geodataframe(combined_df)
    district_summary = build_district_summary(gdf)
    districts_ts    = load_district_polygons(GPKG_PATH)
    combined_district_map = merge_summary_with_polygons(districts_ts, district_summary)
    chosen_district_gdf   = filter_by_district(gdf, CHOSEN_DISTRICT)

    # 2. Classification overview
    plot_classification_frequency(combined_df)

    # 3. Regional choropleths
    plot_tds_map(combined_district_map)
    plot_district_bar(district_summary, "TDS", "TDS (mg/L)")

    plot_nitrate_map(combined_district_map)
    plot_district_bar(district_summary, "NO3 ", "Nitrate (mg/L)")

    # 4. District-level spatial and distributional plots
    plot_district_spatial(chosen_district_gdf)
    plot_analyte_spatial_and_hist(chosen_district_gdf, "TDS",   "TDS (mg/L)")
    plot_analyte_spatial_and_hist(chosen_district_gdf, "NO3 ",  "Nitrate (mg/L)", cmap="Reds")

    # 5. Per-well time series
    plot_well_nitrate_timeseries(combined_df, CHOSEN_DISTRICT)
