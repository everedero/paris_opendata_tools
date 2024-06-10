# Paris OpenData processing scripts

Using Paris OpenData geojson files to process some maps.

## Crossings with our without traffic lights

First, download the geojson files

    python3 download_crossing.py

Then run computing

    python3 crossing_light.py
