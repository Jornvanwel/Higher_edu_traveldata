import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import os

# Read the shapefile of the Netherlands map
mapdf = gpd.read_file("https://stacks.stanford.edu/file/druid:st293bj4601/data.zip")

# Read the CSV file with geospatial data
df = pd.read_csv(r'Data/Geodata_prepared.csv')

# Create a 'geometry' column from 'latitude' and 'longitude'
df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Specify the order of categories
desired_order = ['wo', 'hbo']  # Replace with your actual category names

# Define language dictionaries
language_dicts = {
    'english': {
        'legend_names': {
            'hbo': 'Higher Education',
            'wo': 'University Education'
        },
        'watermark': "Created by J.D. van Wel",
        'output_file': '(EN) Nederland_afstand_HO.png'
    },
    'dutch': {
        'legend_names': {
            'hbo': 'Hoger Beroepsonderwijs',
            'wo': 'Wetenschappelijk Onderwijs'
        },
        'watermark': "Gemaakt door J.D. van Wel",
        'output_file': 'Nederland_afstand_HO.png'
    }
}

# Function to select language dictionary
def get_language_dict(language):
    return language_dicts.get(language.lower(), language_dicts['english'])

# Example: Select English language
selected_language = 'english'  # Change to 'dutch' for Dutch
language_dict = get_language_dict(selected_language)

# Specify category colors
category_colors = {
    'hbo': {'edgecolor': '#D41159', 'facecolor': '#FF000000'},
    'wo': {'edgecolor': '#1AFF1A', 'facecolor': '#1AFF1A'}
}

# Ensure the CRS is set to WGS 84 (EPSG:4326) as this is typical for lat/long data
gdf.set_crs(epsg=4326, inplace=True)

# Transform to the same CRS
mapdf = mapdf.to_crs(epsg=28992)
gdf = gdf.to_crs(epsg=28992)

# Define buffer distances
buffer_distances = [10000, 15000, 20000]  # distances in meters
colors = ['#2cba00', '#a3ff00', '#fff400', '#ffa700']  # sharp green, light green, yellow, red

# Separate water bodies from other areas
water_bodies = mapdf[mapdf['TYPE_1'] == 'Water body']
other_areas = mapdf[mapdf['TYPE_1'] != 'Water body']

# Calculate the aspect ratio of the Netherlands map
bounds = mapdf.total_bounds  # [minx, miny, maxx, maxy]
aspect_ratio = (bounds[3] - bounds[1]) / (bounds[2] - bounds[0])

# Create a figure with two subplots side by side
fig, axs = plt.subplots(1, 2, figsize=(12, 6 * aspect_ratio), sharey=True)

for ax in axs:
    ax.set_aspect('equal')
    ax.set_axis_off()

# Plot buffers and maps in each subplot for each category
for ax, category in zip(axs, desired_order):
    # Get subset of data for the category
    subset = gdf[gdf['SOORT HO'] == category]

    # Plot buffers with decreasing distance, clipping them to the map and excluding water bodies
    previous_buffer = None
    for i, distance in enumerate(buffer_distances):
        current_buffer = subset.buffer(distance)
        current_buffer_clipped = gpd.clip(gpd.GeoDataFrame(geometry=current_buffer, crs=gdf.crs), other_areas)
        current_buffer_gdf = gpd.GeoDataFrame(geometry=[current_buffer_clipped.unary_union], crs=gdf.crs)
        
        if previous_buffer is not None:
            current_ring = gpd.overlay(current_buffer_gdf, previous_buffer, how='difference')
            current_ring = gpd.overlay(current_ring, water_bodies, how='difference')  # Exclude the water bodies
            current_ring.plot(ax=ax, color=colors[i], alpha=1)
        else:
            current_buffer_gdf = gpd.overlay(current_buffer_gdf, water_bodies, how='difference')  # Exclude the water bodies
            current_buffer_gdf.plot(ax=ax, color=colors[i], alpha=1)
        
        previous_buffer = current_buffer_gdf

    # Plot areas outside the largest buffer
    largest_buffer = subset.buffer(buffer_distances[-1])
    largest_buffer_clipped = gpd.clip(gpd.GeoDataFrame(geometry=largest_buffer, crs=gdf.crs), other_areas)
    largest_buffer_gdf = gpd.GeoDataFrame(geometry=[largest_buffer_clipped.unary_union], crs=gdf.crs)
    outside_largest_buffer = gpd.overlay(other_areas, largest_buffer_gdf, how='difference')
    outside_largest_buffer = gpd.overlay(outside_largest_buffer, water_bodies, how='difference')
    outside_largest_buffer.plot(ax=ax, color=colors[-1], alpha=1)

    # Plot the base map
    mapdf.plot(ax=ax, color="#FF000000", edgecolor="black", linewidth=0.5)

    # Plot points for the category
    subset.plot(ax=ax, marker='o', label=category, markersize=30, 
                edgecolor=category_colors[category]['edgecolor'], 
                facecolor=category_colors[category]['facecolor'], zorder=3)

# Create custom legend entries
legend_elements = [
    Patch(facecolor='#2cba00', edgecolor='#2cba00', label='<10 km', alpha=1),
    Patch(facecolor='#a3ff00', edgecolor='#a3ff00', label='10-15 km', alpha=1),
    Patch(facecolor='#fff400', edgecolor='#fff400', label='15-20 km', alpha=1),
    Patch(facecolor='#ffa700', edgecolor='#ffa700', label='>20 km', alpha=1)
]

point_legend_elements = [
    Line2D([0], [0], marker='o', color='w', label=language_dict['legend_names']['hbo'],
           markerfacecolor=category_colors['hbo']['edgecolor'], markersize=10, markeredgewidth=1.8, markeredgecolor=category_colors['hbo']['edgecolor']),
    Line2D([0], [0], marker='o', color='w', label=language_dict['legend_names']['wo'],
           markerfacecolor='none', markersize=10, markeredgewidth=1.8, markeredgecolor=category_colors['wo']['edgecolor'])
]

# Add the custom legend to the first plot
axs[0].legend(handles=legend_elements + point_legend_elements, loc='upper left', title=None)

# Add watermark
fig.text(0.98, 0.02, language_dict['watermark'], fontsize=8, color='gray',
         ha='right', va='bottom', alpha=0.7)

# Add a black edge to the entire figure
fig.patch.set_edgecolor('black')
fig.patch.set_linewidth(1)

fig.tight_layout()

# Ensure the output directory exists
output_dir = 'Visuals'
os.makedirs(output_dir, exist_ok=True)

# Save the figure with higher resolution
output_file_path = os.path.join(output_dir, language_dict['output_file'])
fig.savefig(output_file_path, dpi=720)

plt.show()
