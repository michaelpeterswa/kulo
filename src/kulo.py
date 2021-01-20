# michaelpeterswa
# kulo.py

import geojson
from shapely.geometry import shape, MultiPolygon, Polygon, Point

input_file = "..\data\Washington_Large_Fires_1973-2019.geojson"


def loadData(filename):
    """
    Loads GeoJson Data from "filename"
    """
    with open(filename) as f:
        data = geojson.load(f)
    return data

def returnAcreage(fire):
    """
    return acreage of a fire
    """
    return fire["properties"]["ACRES"]

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
    return polygon.centroid.coords

def isMultiPolygonal(fire):
    """
    return true if the object is a MultiPolygon
    """
    return True if fire["geometry"]["type"] == "MultiPolygon" else False
    


if __name__ == "__main__":
    fire_data = loadData(input_file)
    fire_data = fire_data["features"]
    results = []
    for fire in fire_data:
        poly = createPolygonFromMulti(fire) if isMultiPolygonal(fire) else createPolygon(fire)
        fire_centroid = generateCentroid(poly)
        results.append((list(fire_centroid), fire["properties"]))
    print(results)