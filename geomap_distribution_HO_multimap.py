import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from matplotlib.gridspec import GridSpec
import os

# Read the shapefile of the Netherlands map
mapdf = gpd.read_file("https://stacks.stanford.edu/file/druid:st293bj4601/data.zip")

# Read the CSV file with geospatial data
df = pd.read_csv(r'Data/Geodata_prepared.csv')

# Create a 'geometry' column from 'latitude' and 'longitude'
df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Ensure the CRS is set to WGS 84 (EPSG:4326)
gdf.set_crs(epsg=4326, inplace=True)

# Transform the coordinate reference system to match the map's CRS
mapdf = mapdf.to_crs(epsg=28992)
gdf = gdf.to_crs(epsg=28992)

# Specify the order of categories and their colors
categories_subsets = [['wo'], ['hbo']]
category_colors = {
    'hbo': {'edgecolor': '#D41159', 'facecolor': '#FF000000'},
    'wo': {'edgecolor': '#CCBB44', 'facecolor': '#CCBB44'}
}

# Define language dictionaries
language_dicts = {
    'english': {
        'legend_names': {
            'hbo': 'Higher Education',
            'wo': 'University Education'
        },
        'watermark': "Created by J.D. van Wel",
        'output_file': '(EN) Nederland_verdeling_HO_subplots.png'
    },
    'dutch': {
        'legend_names': {
            'hbo': 'Hoger Beroepsonderwijs',
            'wo': 'Wetenschappelijk Onderwijs'
        },
        'watermark': "Gemaakt door J.D. van Wel",
        'output_file': 'Nederland_verdeling_HO_subplots.png'
    }
}

# Function to select language dictionary
def get_language_dict(language):
    return language_dicts.get(language.lower(), language_dicts['english'])

# Example: Select Dutch language
selected_language = 'english'  # Change to 'english' for English
language_dict = get_language_dict(selected_language)

# Calculate the aspect ratio of the Netherlands map
bounds = mapdf.total_bounds
aspect_ratio = (bounds[3] - bounds[1]) / (bounds[2] - bounds[0])

# Create a figure with a grid of subplots
fig = plt.figure(figsize=(12, 6 * aspect_ratio))
gs = GridSpec(2, 2, height_ratios=[1, 0.1], width_ratios=[1, 1])

axes = [fig.add_subplot(gs[i, j]) for i in range(0, 2, 2) for j in range(2)]
legend_axes = [fig.add_subplot(gs[i, j]) for i in range(1, 2, 2) for j in range(2)]

# Plot each subset of categories in its respective subplot
for ax, categories in zip(axes, categories_subsets):
    mapdf.plot(ax=ax, color="white", edgecolor="black", zorder=1, linewidth=0.5)
    for category in categories:
        subset = gdf[gdf['SOORT HO'] == category]
        subset.plot(ax=ax, marker='o', label=category, markersize=20, 
                    edgecolor=category_colors[category]['edgecolor'], 
                    facecolor=category_colors[category]['facecolor'], zorder=3)
    ax.set_aspect('equal')
    ax.set_axis_off()

# Add legends to each corresponding subplot
for ax, categories, legend_ax in zip(axes, categories_subsets, legend_axes):
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=language_dict['legend_names'][category], 
                          markersize=10, 
                          markerfacecolor=category_colors[category]['facecolor'],
                          markeredgecolor=category_colors[category]['edgecolor']) 
               for category in categories]
    legend = legend_ax.legend(handles=handles, loc='center', ncol=1, markerscale=0.8, fontsize=14, frameon=False)
    legend_ax.add_artist(legend)
    legend_ax.set_axis_off()

plt.subplots_adjust(wspace=0.05, hspace=0.1)  # Adjust the space between plots

# Add a black border around the entire figure
fig.patch.set_edgecolor('black')
fig.patch.set_linewidth(1)

plt.tight_layout()

# Add watermark
fig.text(0.98, 0.02, language_dict['watermark'], fontsize=8, color='gray',
         ha='right', va='bottom', alpha=0.7)

# Ensure the output directory exists
output_dir = 'Visuals'
os.makedirs(output_dir, exist_ok=True)

# Save the figure with higher resolution
output_file_path = os.path.join(output_dir, language_dict['output_file'])
fig.savefig(output_file_path, dpi=720)

plt.show()
