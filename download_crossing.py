"""
Script to download data from opendata Paris and OSM
"""
import requests
import sys
import pathlib
from pathlib import Path
import logging as logger
import geopandas

light_file = "data/signalisation-tricolore.geojson"
road_file = "data/troncon-voie.geojson"

base_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/"
open_lights = f"{base_url}signalisation-tricolore/exports/geojson"
open_roads = f"{base_url}troncon_voie/exports/geojson"

datapath = Path("data")
# Create path if it does not exists
datapath.mkdir(exist_ok=True)

def save_data_from_paris(url, filename):
    p = Path(filename)
    if not p.exists():
        logger.info(f"{filename} does not exists, creating")
        print(filename)
        data = requests.get(url)
        with open(p, "w") as myfile:
            myfile.write(data.text)

save_data_from_paris(open_lights, light_file)
save_data_from_paris(open_roads, road_file)
