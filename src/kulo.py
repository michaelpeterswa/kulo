# michaelpeterswa
# kulo.py

import geojson

input_file = "..\data\Washington_Large_Fires_1973-2019.geojson"


def loadData(filename):
    """
    Loads GeoJson Data from "filename"
    """
    with open(filename) as f:
        data = geojson.load(f)
    return data

if __name__ == "__main__":
    max_acres = 0
    fire_data = loadData(input_file)
    fire_data = fire_data["features"]
    for fire in fire_data:
        acres = fire["properties"]["ACRES"]
        if acres > max_acres:
            max_acres = acres
    print(max_acres)