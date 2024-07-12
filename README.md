# Higher Education Map Visuals

This project involves generating isochrones figures for a specific geographic area using geospatial data.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Dependencies and Licenses](#dependencies-and-licenses)
- [License](#license)

## Introduction

This project generates isochrones figures, which are maps that show areas reachable within a certain time from a specific point. These figures can be useful for various analyses, such as accessibility studies or urban planning. The project focuses on higher education institutions in the Netherlands, using geospatial data to visualize accessibility.

## Installation

Follow these steps to install the necessary dependencies and set up the project:

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/isochrones-project.git
    cd isochrones-project
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Go to [openrouteservice.org](https://openrouteservice.org/), create an account, and obtain an API key.

5. Add the API key as a system variable:
    ```bash
    setx OPENROUTE_API_KEY "YOUR_API_KEY"
    ```

## Configuration

Ensure that your API key is correctly set in your environment variables. You can verify this by running the following command in your terminal:
```bash
echo %OPENROUTE_API_KEY%  # On Windows
echo $OPENROUTE_API_KEY  # On MacOS/Linux
```

## Usage
To generate the figures you first need to run the geodata preparation and geodata traveltime preparation file.
```bash
python geodata_preparation.py
python geodata_traveltime_preparation.py
python geomap_traveltime_to_HO.py
```
This will create a visualization of the accessibility of higher education institutions based on travel times.

## Dependencies and Licenses

This project uses the following third-party libraries:

- **geocoder nominatim**: Used for geocoding addresses to geographic coordinates.

Repository: https://github.com/osm-search/Nominatim
The Python source code is available under a GPL license version 3 or later. The Lua configuration files for osm2pgsql are released under the Apache License, Version 2.0. All other files are under a GPLv2 license.

- **openrouteservices**: Provides isochrones and routing services.

Website: https://openrouteservice.org
License: © openrouteservice.org by HeiGIT | Map data © OpenStreetMap contributors

- **DUO-data**: Contains addresses of higher education institutions.

Website: https://duo.nl/open_onderwijsdata/hoger-onderwijs/adressen/hogescholen-en-universiteiten.jsp
The example data file is based on the open dataset from duo.nl.

# License
This project is licensed under the MIT License. See the LICENSE file for details.