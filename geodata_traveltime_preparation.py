import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import openrouteservice
from shapely.geometry import shape
import time
import os

# Load the point data
df = pd.read_csv(r'Data\Geodata_prepared.csv')

# Create a 'geometry' column from 'latitude' and 'longitude'
df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Replace with your OpenRouteService API key
api_key = os.getenv("OPENROUTE_API_KEY")

# Initialize the OpenRouteService client
client = openrouteservice.Client(key=api_key)
profile = 'driving-car'  # Mode of transport
range_type = 'time'  # 'time' or 'distance'
range = [600, 900, 1200, 1500, 1800, 2700]  # Time in seconds (10, 20, and 30 minutes)

# Initialize an empty list to collect isochrone data
iso_data_list = []

for index, row in gdf[gdf['longitude'].notna()].iterrows():
    location = (row['longitude'], row['latitude'])
    print(row['INSTELLINGSNAAM'])
    # Request isochrones from the OpenRouteService API
    isochrones = client.isochrones(
        locations=[location],
        profile=profile,
        range_type=range_type,
        range=range,
        smoothing=10
    )

    # Convert isochrones to GeoDataFrame
    features = isochrones['features']
    geometries = [shape(feature['geometry']) for feature in features]
    isochrone_gdf = gpd.GeoDataFrame(geometry=geometries)

    # Add additional information to the GeoDataFrame
    isochrone_gdf['latitude'] = row['latitude']
    isochrone_gdf['longitude'] = row['longitude']
    isochrone_gdf['INSTELLINGSNAAM'] = row['INSTELLINGSNAAM']
    isochrone_gdf['SOORT HO'] = row['SOORT HO']

    # Add the range information
    isochrone_gdf['range'] = [feature['properties']['value'] for feature in features]

    # Append the data to the list
    iso_data_list.append(isochrone_gdf)
    time.sleep(3)

# Concatenate all isochrone GeoDataFrames into a single DataFrame
all_isochrones_gdf = pd.concat(iso_data_list, ignore_index=True)

# Optionally, save the combined DataFrame to a file
all_isochrones_gdf.to_file('Data\\all_isochrones.geojson', driver='GeoJSON')
