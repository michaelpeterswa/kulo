# michaelpeterswa
# kulo.py

import geojson
import datetime
import numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from keras.models import Sequential 
from keras.layers import Dense
from keras.callbacks import TensorBoard

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
    lat_amt = 100
    long_amt = 200
    results = []
    for fire in fire_data:
        poly = createPolygonFromMulti(fire) if isMultiPolygonal(fire) else createPolygon(fire)
        fire_centroid = generateCentroid(poly)
        results.append((fire_centroid, fire["properties"]))
    normalized_fire_data = normalizeFireData(results, max_acreage, lat_amt, long_amt)

    #-----------------------------
    X = normalized_fire_data[:,0:2]
    y = normalized_fire_data[:,2]
    model = Sequential()
    model.add(Dense(4, input_dim=2, activation='relu'))
    model.add(Dense(4, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer='adam')

    log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)

    model.fit(X, y, batch_size=5, epochs=1000, callbacks=[tensorboard_callback], verbose=0)
    results = model.evaluate(X, y)

    model.save("kulo_model")

    print("Loss: ", results)

    test_lat = 48.383549
    test_long = -120.009935

    samples = [(test_lat / lat_amt, test_long / long_amt)]
    npsamples = np.array(samples)
    predictions = model.predict(samples)
    result_acres = predictions[0][0] * max_acreage

    print("final result for: (", test_lat, ",", test_long, ") at ", result_acres, "acres" )