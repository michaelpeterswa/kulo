# michaelpeterswa
# kulo.py

import geojson
import numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point


input_file = "..\data\Washington_Large_Fires_1973-2019.geojson"


def loadData(filename):
    """
    Loads GeoJson Data from "filename"
    """
    with open(filename) as f:
        data = geojson.load(f)
    return data

def returnMaxAcreage(fire_data):
    """
    return maximum acreage
    """
    fire_max = 0
    for fire in fire_data:
        if fire["properties"]["ACRES"] >= fire_max:
            fire_max = fire["properties"]["ACRES"]

    return fire_max

def createPolygon(fire):
    """
    create a Polygon object from list of points
    """
    points = []
    for coordinate in fire["geometry"]["coordinates"][0]:
        points.append(tuple(coordinate))
    polygon = Polygon(points)
    return polygon

def createPolygonFromMulti(fire):
    """
    https://gis.stackexchange.com/questions/166934/python-library-for-converting-geojson-multi-polygon-to-polygon
    """
    multipolygon = [x.buffer(0) for x in shape(fire["geometry"]).buffer(0).geoms]
    max_poly = max(multipolygon, key=lambda a: a.area)
    return max_poly

def generateCentroid(polygon):
    """
    calculate and return centroid of a polygon
    """
    return list(polygon.centroid.coords)

def isMultiPolygonal(fire):
    """
    return true if the object is a MultiPolygon
    """
    return True if fire["geometry"]["type"] == "MultiPolygon" else False

def normalizeFireData(fire_data, max_acres, lat_div=100, long_div=200):
    fire_data_list = []
    for fire in fire_data:
        fire_size = fire[1]["ACRES"] / max_acreage
        fire_lat = fire[0][0][1] / lat_div
        fire_long = fire[0][0][0] / long_div
        fire_data_list.append([fire_lat, fire_long, fire_size])
    fire_data_nparray = np.array(fire_data_list)
    return fire_data_nparray
    

if __name__ == "__main__":
    fire_data = loadData(input_file)
    fire_data = fire_data["features"]
    max_acreage = returnMaxAcreage(fire_data)
    results = []
    for fire in fire_data:
        poly = createPolygonFromMulti(fire) if isMultiPolygonal(fire) else createPolygon(fire)
        fire_centroid = generateCentroid(poly)
        results.append((fire_centroid, fire["properties"]))
    normalized_fire_data = normalizeFireData(results, max_acreage)
    print(normalized_fire_data)