# essaye d'établir la carte des passages piétons qui nécessitent la loi lom
# attention ca ne prend pas en compte le sens du traffic donc il faut refaire un tri à la main derriere...
#
import geopandas
import pandas
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
osm_crossings = "data/osm-crossings.geojson"

if 1:
    logger.debug("Starting opening data files")
    df_light = geopandas.read_file(light_file)
    df_road = geopandas.read_file(road_file)
    logger.info("Database opened")

    # Convert coordinates
    df_light.to_crs(crs_2d, inplace=True)
    df_road.to_crs(crs_2d, inplace=True)

    # Roads to roads extremities
    from shapely.geometry import MultiPoint

    def only_road_side(obj):
        obj2 = MultiPoint([[obj.coords.xy[0][0], obj.coords.xy[1][0]],
            [obj.coords.xy[0][-1], obj.coords.xy[1][-1]]])
        return(obj2)

    df_road["geometry"] = df_road["geometry"].map(only_road_side)

    # Transform dataframe to single points
    points = df_road.explode(index_parts=False)

    # Lights by crossroads
    crosslight = df_light.dissolve(by="lib_voie")
    crosslight = crosslight.centroid

    # Export
    crossroad_points = points.to_crs(crs_api_database)
    crosslight = crosslight.to_crs(crs_api_database)

    crossroad_points.to_file("data/result_crossroad.geojson")
    crosslight.to_file("data/result_crosslight.geojson")

if 1:
    crossroad_points = geopandas.read_file("data/result_crossroad.geojson")
    crosslight = geopandas.read_file("data/result_crosslight.geojson")
    # Convert coordinates
    crossroad_points.to_crs(crs_2d, inplace=True)
    crosslight.to_crs(crs_2d, inplace=True)

if 1:
    from pathlib import Path
    if Path(osm_crossings).exists():
        print("OSM file found, cleaning crossroad data")

        crossroad_points_osm = geopandas.read_file(osm_crossings)
        crossroad_points_osm.to_crs(crs_2d, inplace=True)
        crossroad_points = crossroad_points.sjoin_nearest(right=crossroad_points_osm, how="inner",
                max_distance=20, rsuffix="_osm", distance_col="distance")

    print(crossroad_points)

if 1:
    df_merged = crossroad_points.sjoin_nearest(crosslight, how="left",
        max_distance=50, rsuffix="right", distance_col="margin")

    df_merged["crossing_light"] = (~df_merged["index_right"].isna())
    df_merged = df_merged.to_crs(crs_api_database)
    df_merged.to_file("data/result_crossroads_lights.geojson")
