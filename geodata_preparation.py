import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Initialize Nominatim API with a user agent and increased timeout
geolocator = Nominatim(user_agent="myGeocoder", timeout=10)

# Read the CSV file
df = pd.read_csv(r"Data\Locaties hoger onderwijs.csv", sep=',')

# Create address dictionary for each row
df['address'] = df.apply(lambda row: {
    'street': row['STRAATNAAM'],
    'postalcode': row['POSTCODE'],
    'city': row['PLAATSNAAM'],
    'country': 'Netherlands'
}, axis=1)

# Apply rate limiter to the geocode function
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2, max_retries=3, error_wait_seconds=10)

# Function to handle geocoding with retries and logging
def geocode_with_logging(address):
    try:
        return geocode(address)
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return None

# Apply the geocoding function to the address column
df['location'] = df['address'].apply(geocode_with_logging)

# Extract latitude and longitude from the location
df['latitude'] = df['location'].apply(lambda loc: loc.latitude if loc else None)
df['longitude'] = df['location'].apply(lambda loc: loc.longitude if loc else None)

# Save the resulting dataframe to a CSV file
df.to_csv(r"Data\Geodata_prepared.csv", index=False)

# Print the dataframe to verify the results
print(df)
