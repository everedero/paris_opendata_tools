# Paris OpenData processing scripts

Using Paris OpenData geojson files to process some maps.

## Crossings with our without traffic lights

Create a ./data folder to store the files.

First, download the geojson files

    python3 download_crossing.py

Optionally, download crossing cleanup data from osm

    python3 osm_requests.py

Then run computing

    python3 crossing_light.py
