import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import os

# Read the shapefile of the Netherlands map
mapdf = gpd.read_file("https://stacks.stanford.edu/file/druid:st293bj4601/data.zip")

# Read the CSV file with geospatial data
df = pd.read_csv(r'Data/Geodata_prepared.csv')

# Create a 'geometry' column from 'latitude' and 'longitude'
df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Define the order of categories
desired_order = ['wo', 'hbo']

# Define language dictionaries
language_dicts = {
    'english': {
        'legend_names': {
            'hbo': 'Higher Education',
            'wo': 'University Education'
        },
        'watermark': "Created by J.D. van Wel",
        'output_file': '(EN) Nederland_verdeling_HO.png'
    },
    'dutch': {
        'legend_names': {
            'hbo': 'Hoger Beroepsonderwijs',
            'wo': 'Wetenschappelijk Onderwijs'
        },
        'watermark': "Gemaakt door J.D. van Wel",
        'output_file': 'Nederland_verdeling_HO.png'
    }
}

# Function to select language dictionary
def get_language_dict(language):
    return language_dicts.get(language.lower(), language_dicts['english'])

# Example: Select English language
selected_language = 'english'  # Change to 'dutch' for Dutch
language_dict = get_language_dict(selected_language)

# Define category colors
category_colors = {
    'hbo': {'edgecolor': '#D41159', 'facecolor': '#FF000000'},
    'wo': {'edgecolor': '#1AFF1A', 'facecolor': '#1AFF1A'}
}

# Ensure the CRS is set to WGS 84 (EPSG:4326) as this is typical for lat/long data
gdf.set_crs(epsg=4326, inplace=True)

# Transform the coordinate reference system to match the map's CRS
mapdf = mapdf.to_crs(epsg=28992)
gdf = gdf.to_crs(epsg=28992)

# Calculate the aspect ratio of the Netherlands map
bounds = mapdf.total_bounds  # [minx, miny, maxx, maxy]
aspect_ratio = (bounds[3] - bounds[1]) / (bounds[2] - bounds[0])

# Plot the base map
fig, ax = plt.subplots(figsize=(6, 6 * aspect_ratio))
mapdf.plot(ax=ax, color="white", edgecolor="black", linewidth=0.5)

# Plot each category separately
for category in desired_order:
    if category in gdf['SOORT HO'].unique():
        subset = gdf[gdf['SOORT HO'] == category]
        subset.plot(ax=ax, marker='o', label=language_dict['legend_names'][category], markersize=30, 
                    edgecolor=category_colors[category]['edgecolor'], 
                    facecolor=category_colors[category]['facecolor'], zorder=3)
    else:
        print(f"Warning: Category '{category}' not found in data.")

# Customize legend
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, loc='upper left', markerscale=1.4, fontsize=10)
ax.set_axis_off()

# Add a black edge to the entire figure
rect = plt.Rectangle(
    (0, 0), 1, 1, transform=ax.transAxes, 
    linewidth=2, edgecolor='black', facecolor='none'
)
ax.add_patch(rect)

plt.tight_layout()

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
