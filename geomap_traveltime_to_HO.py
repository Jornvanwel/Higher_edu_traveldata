import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import os
from matplotlib.gridspec import GridSpec

# Read the shapefile of the Netherlands map
mapdf = gpd.read_file("https://stacks.stanford.edu/file/druid:st293bj4601/data.zip")

# Define language dictionaries
language_dicts = {
    'english': {
        'legend_names': {
            'hbo': 'Higher Education',
            'wo': 'University Education'
        },
        'watermark': "Created by J.D. van Wel",
        'output_file': '(EN) Nederland_reistijd_HO.png'
    },
    'dutch': {
        'legend_names': {
            'hbo': 'Hoger Beroepsonderwijs',
            'wo': 'Wetenschappelijk Onderwijs'
        },
        'watermark': "Gemaakt door J.D. van Wel",
        'output_file': 'Nederland_reistijd_HO.png'
    }
}

# Function to select language dictionary
def get_language_dict(language):
    return language_dicts.get(language.lower(), language_dicts['english'])

# Example: Select Dutch language
selected_language = 'english'  # Change to 'dutch' for Dutch
language_dict = get_language_dict(selected_language)

# Read the CSV file with geospatial data
df = pd.read_csv(r'Data/Geodata_prepared.csv')

# Create a 'geometry' column from 'latitude' and 'longitude'
df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Load the travel time polygons from GeoJSON
travel_time_gdf = gpd.read_file(r'Data/all_isochrones.geojson')

# Ensure the CRS is set to WGS 84 (EPSG:4326) as this is typical for lat/long data
gdf.set_crs(epsg=4326, inplace=True)
travel_time_gdf.set_crs(epsg=4326, inplace=True)

# Transform to the same CRS
mapdf = mapdf.to_crs(epsg=28992)
gdf = gdf.to_crs(epsg=28992)
travel_time_gdf = travel_time_gdf.to_crs(epsg=28992)

# Define travel time ranges and colors
travel_time_ranges = [600, 900, 1200, 1500, 1800, 2700]  # travel times in seconds
colors = ['#B5EB84', '#E7F7B5', '#FFFF8C', '#FFE763', '#FFAE4A', '#FF8239', '#CE0000']

# Separate water bodies from other areas
water_bodies = mapdf[mapdf['TYPE_1'] == 'Water body']
other_areas = mapdf[mapdf['TYPE_1'] != 'Water body']

# Specify the order of categories and their colors
desired_order = ['wo', 'hbo']
category_colors = {
    'hbo': {'edgecolor': '#0F67B1', 'facecolor': '#0F67B1'},
    'wo': {'edgecolor': '#FF4191', 'facecolor': '#FF4191'}
}

# Define the aspect ratio
aspect_ratio = 1.5
fig = plt.figure(figsize=(12, 6 * aspect_ratio))
gs = GridSpec(1, 2, height_ratios=[1], width_ratios=[1, 1])

# Plot the maps
axes = [fig.add_subplot(gs[0, j]) for j in range(2)]

for idx, (ax, category) in enumerate(zip(axes, desired_order)):
    range_subset = travel_time_gdf[travel_time_gdf['SOORT HO'] == category]
    gdf_subset = gdf[gdf['SOORT HO'] == category]
    other_areas.plot(ax=ax, color="white", edgecolor="black")
    ax.set_aspect('equal')

    # Plot buffers with decreasing travel time, clipping them to the map and excluding water bodies
    previous_buffer = None
    for i, travel_time in enumerate(travel_time_ranges):
        current_buffer = range_subset[range_subset['range'] == travel_time]['geometry']
        current_buffer_clipped = gpd.clip(gpd.GeoDataFrame(geometry=current_buffer, crs=gdf.crs), other_areas)
        current_buffer_gdf = gpd.GeoDataFrame(geometry=[current_buffer_clipped.unary_union], crs=gdf.crs)

        if previous_buffer is not None:
            current_ring = gpd.overlay(current_buffer_gdf, previous_buffer, how='difference')
            current_ring.plot(ax=ax, color=colors[i], alpha=1)
        else:
            current_buffer_gdf = gpd.overlay(current_buffer_gdf, water_bodies, how='difference')
            current_buffer_gdf.plot(ax=ax, color=colors[i], alpha=1)

        previous_buffer = current_buffer_gdf

    outside_buffer = gpd.overlay(gpd.GeoDataFrame(geometry=[other_areas.unary_union], crs=gdf.crs), previous_buffer, how='difference')
    outside_buffer.plot(ax=ax, color='red', alpha=1, zorder=2)

    # Plot the rest of the map
    mapdf.plot(ax=ax, color="#FF000000", edgecolor="black", linewidth=0.5)
    gdf_subset.plot(ax=ax, marker='o', label=language_dict['legend_names'].get(category, category), markersize=30,
                    edgecolor=category_colors[category]['edgecolor'],
                    facecolor=category_colors[category]['facecolor'], zorder=3)

    if idx == 0:  # Only add the legend to the left subplot
        legend_elements = [
            Patch(facecolor='#B5EB84', edgecolor='#B5EB84', label='<10 min', alpha=1),
            Patch(facecolor='#E7F7B5', edgecolor='#E7F7B5', label='10-15 min', alpha=1),
            Patch(facecolor='#FFFF8C', edgecolor='#FFFF8C', label='15-20 min', alpha=1),
            Patch(facecolor='#FFE763', edgecolor='#FFE763', label='20-25 min', alpha=1),
            Patch(facecolor='#FFAE4A', edgecolor='#FFAE4A', label='25-30 min', alpha=1),
            Patch(facecolor='#FF8239', edgecolor='#FF8239', label='30-45 min', alpha=1),
            Patch(facecolor='#CE0000', edgecolor='#CE0000', label='>45 min', alpha=1)
        ]

        point_legend_elements = [
            Line2D([0], [0], marker='o', color='w', label=language_dict['legend_names']['hbo'],
                   markerfacecolor=category_colors['hbo']['facecolor'], markersize=10, markeredgewidth=1.8, markeredgecolor=category_colors['hbo']['edgecolor']),
            Line2D([0], [0], marker='o', color='w', label=language_dict['legend_names']['wo'],
                   markerfacecolor=category_colors['wo']['facecolor'], markersize=10, markeredgewidth=1.8, markeredgecolor=category_colors['wo']['edgecolor'])
        ]

        ax.legend(handles=legend_elements + point_legend_elements, title='Travel Time in Minutes', loc='upper left')

    ax.set_axis_off()
    fig.tight_layout()

# Add watermark
fig.text(0.96, 0.04, language_dict['watermark'], fontsize=8, color='gray',
         ha='right', va='bottom', alpha=0.7)

# Ensure the output directory exists
output_dir = 'Visuals'
os.makedirs(output_dir, exist_ok=True)

# Save the figure with higher resolution
output_file_path = os.path.join(output_dir, language_dict['output_file'])
fig.savefig(output_file_path, dpi=720)

plt.show()
