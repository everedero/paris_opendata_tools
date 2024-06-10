# essaye d'établir la carte des passages piétons qui nécessitent la loi lom
# attention ca ne prend pas en compte le sens du traffic donc il faut refaire un tri à la main derriere...
#
import geopandas
import pandas
from paris_requests import BackendApi
import logging

# Custom logger
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handler to the logger
logger.addHandler(handler)

crs_api_database = 4326 # WGS 84, World Geodetic System, latitude and longitude
crs_2d = 3857 # Pseudo-Mercator, 2d projection, allows to work in meters

light_file = "data/signalisation-tricolore.geojson"
road_file = "data/troncon-voie.geojson"

logger.debug("Starting opening data files")
df_light = geopandas.read_file(light_file, rows = 25)
df_road = geopandas.read_file(road_file, rows = 10)
logger.info("Database opened")

# Convert coordinates
df_light.to_crs(crs_2d, inplace=True)
df_road.to_crs(crs_2d, inplace=True)

print(df_road)
print(df_road["geom_x_y"].iloc[0])
#df_road.plot()
#import matplotlib.pyplot as plt
#plt.show()

if 0:

    # Convert back to geographic crs
    df_joined_parks.to_crs(crs_api_database, inplace=True)
    df_light.to_crs(crs_api_database, inplace=True)

    # Export to GeoJSON
    output_carrouf = "data/result_carrouf.geojson"
    (df_joined_parks[df_joined_parks["potential_issue"] == True]).to_file(output_parks, driver="GeoJSON")
    (df_light[df_light["objectid"].isin(list_ids)]).to_file(output_piets, driver="GeoJSON")
