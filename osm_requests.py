import json
import overpass
import logging
import geopandas
import shapely

logger = logging.getLogger("main")

class OsmBackendApi:
    def __init__(self):
        self.api = overpass.API(timeout=600)
        self.crs_api = 4326 # WGS 84, World Geodetic System, latitude and longitude
        self.crs_2d = 3857 # Pseudo-Mercator, 2d projection, allows to work in meters

    def _point_to_bbox(self, point, distance, convert_crs=True):
        """
        Use convert_crs=True if input point is in geographical
        format, and convert_crs=False if you are already in 2d
        format.
        """
        if convert_crs:
            point = geopandas.GeoSeries(point, crs=self.crs_api)
            point = point.to_crs(self.crs_2d)
        else:
            point = geopandas.GeoSeries(point, crs=self.crs_2d)
        area = point.buffer(distance, cap_style="square")
        area = area.to_crs(self.crs_api)
        bbox = "({},{},{},{})".format(
            area.bounds.miny.iloc[0],
            area.bounds.minx.iloc[0],
            area.bounds.maxy.iloc[0],
            area.bounds.maxx.iloc[0])
        return(bbox)

    def _envelope_to_bbox(self, contour, convert_crs = False):
        """
        Return bbox string given a GeoSeries.envelope object
        """
        if convert_crs:
            bbox = geopandas.GeoSeries(contour, crs=self.crs_api)
            bbox = bbox.to_crs(self.crs_2d)
        else:
            bbox = geopandas.GeoSeries(contour, crs=self.crs_2d)
        bbox = bbox.get_coordinates()
        bbox = "({},{},{},{})".format(
            bbox.y.iloc[0],
            bbox.x.iloc[0],
            bbox.y.iloc[2],
            bbox.x.iloc[2])
        return(bbox)

    def _get_roads_with_bbox(self, bbox):
        req = ""
        list_ways = ["unclassified" ,"primary", "secondary", "tertiary",
                "residential"]
        req = [f"""{req}way["highway"="{type_way}"]{bbox};out geom;"""
                for type_way in list_ways]
        req = " ".join(req)
        # Adding roads with specific access
        list_ways = ["pedestrian", "living_street", "service", "unclassified",
                "footway"]
        req2 = ""
        req2 = [f"""{req2}way["highway"="{type_way}"]["motor_vehicle"="yes"]{bbox};out geom;"""
                for type_way in list_ways]
        req2 = " ".join(req2)
        req = f"{req}{req2}"
        response = self.api.Get(req)
        if len(response["features"]) == 0:
            return(None)
        df_roads = geopandas.GeoDataFrame.from_features(response, crs=self.crs_api)
        columns = ["geometry", "highway", "oneway", "name"]
        return(df_roads[columns])

    def get_roads_around(self, point, distance, convert_crs=True):
        bbox = self._point_to_bbox(point, distance, convert_crs)
        return(self._get_roads_with_bbox(bbox))

    def get_roads_inside(self, contour):
        req = ""
        bbox = self._envelope_to_bbox(contour)
        list_ways = ["unclassified" ,"primary", "secondary", "tertiary",
                "residential", "pedestrian", "living_street"]
        req = [f"""{req}way["highway"="{type_way}"]{bbox};out geom;"""
                for type_way in list_ways]
        req = " ".join(req)
        # Adding roads with specific access
        list_ways = ["pedestrian", "living_street", "service", "unclassified",
                "footway"]
        req2 = ""
        req2 = [f"""{req2}way["highway"="{type_way}"]["motor_vehicle"="yes"]{bbox};out geom;"""
                for type_way in list_ways]
        req2 = " ".join(req2)
        req = f"{req}{req2}"
        response = self.api.Get(req)
        if len(response["features"]) == 0:
            return(None)
        df_roads = geopandas.GeoDataFrame.from_features(response, crs=self.crs_api)
        columns = ["geometry", "highway", "oneway", "name"]
        return(df_roads[columns])

    def get_crossings_around(self, point, distance, convert_crs=True):
        req = ""
        bbox = self._point_to_bbox(point, distance, convert_crs)
        req = f"""nwr["highway"="crossing"]{bbox};"""
        response = self.api.Get(req)
        if len(response["features"]) == 0:
            return(None)
        df_crossings = geopandas.GeoDataFrame.from_features(response, crs=self.crs_api)
        return(df_crossings)

    def get_bike_parkings_around(self, point, distance, convert_crs=True):
        bbox = self._point_to_bbox(point, distance, convert_crs)

        object_type = """["amenity"="bicycle_parking"]"""
        response = self.api.Get(f"""area{object_type}{bbox};""" +\
                f"""node{object_type}{bbox};""")
        return(response)

    def get_roads_from_paris(self):
        bbox = "(48.8147689379391,2.2520118409403937,48.90411728261984,2.418553689636753)"
        return(self._get_roads_with_bbox(bbox))

from shapely.geometry import MultiPoint
if __name__ == "__main__":
    osm_crossings = "data/osm-crossings.geojson"
    ba = OsmBackendApi()
    df_roads = ba.get_roads_from_paris()

    #centers = shapely.Point(2.3466, 48.8614)
    #df_roads = ba.get_roads_around(centers, 8000)

    def linestring_to_multipoint(obj):
        obj2 = MultiPoint(obj.coords)
        return(obj2)

    df_roads["geometry"] = df_roads["geometry"].map(linestring_to_multipoint)

    # Transform dataframe to single points
    points = df_roads.explode(index_parts=False)
    # Linestring to multipoints
    df_roads = df_roads.explode()

    group = df_roads.merge(right=df_roads, how="inner", on="geometry")
    group = group[group["name_x"] != group["name_y"]]
    # Remove lines merged with themselves
    group.drop_duplicates(subset=["geometry"], keep='first', inplace=True,
            ignore_index=False)
    # Remove nans
    group = group[~group["name_x"].isna()]
    group.to_file(osm_crossings, driver="GeoJSON")
