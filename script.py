import argparse
import datetime

import ee
import geojson
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()

# Adding arguments
parser.add_argument("-i", "--input", help="Input GeoJson", required=True)
parser.add_argument(
    "-sd", "--start_date", help="Start Date in YYYY-MM-DD", required=True
)
parser.add_argument("-ed", "--end_date", help="End Date in YYYY-MM-DD", required=True)
parser.add_argument("-o", "--output", help="Output PNG", required=True)

# Read arguments from command line
args = parser.parse_args()
input = args.input
start_date = args.start_date
end_date = args.end_date
output = args.output

# Validate Start Date and End Date
try:
    sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")
except:
    raise Exception("Date should be in YYYY-MM-DD")

if sd > ed:
    raise Exception("Start Date should be earlier than the End Date")

# Load the GeoJSON file representing the inland water body
with open(input, "r") as f:
    geojson_data = geojson.load(f)

# Authenticate the Earth Engine API using the browser
ee.Authenticate()

# Initialize the Earth Engine API
ee.Initialize()

# Extract the geometry from the GeoJSON
geometry = ee.Geometry.Polygon(geojson_data["features"][0]["geometry"]["coordinates"])


# Load the MODIS water dataset
dataset = (
    ee.ImageCollection("MODIS/006/MOD44W")
    .filterDate(start_date, end_date)
    .select("water_mask")
)


# Function to calculate the water extent for each image
def calculate_water_extent(image):
    water = image.eq(1)
    area = water.multiply(ee.Image.pixelArea()).reduceRegion(
        reducer=ee.Reducer.sum(), geometry=geometry, scale=30, maxPixels=1e9
    )
    date = ee.Date(image.get("system:time_start")).format("YYYY-MM-dd")
    return ee.Feature(None, {"date": date, "water_area": area.get("water_mask")})


# Map the function over the image collection and convert to a FeatureCollection
water_extent_fc = dataset.map(calculate_water_extent).filter(
    ee.Filter.notNull(["water_area"])
)


# Get the data as a list of dictionaries
water_extent_list = water_extent_fc.getInfo()["features"]
water_extent_time_series = [
    {
        "date": feature["properties"]["date"],
        "water_area": feature["properties"]["water_area"],
    }
    for feature in water_extent_list
]

# Convert the dates and areas to separate lists for plotting
dates = [
    datetime.datetime.strptime(d["date"], "%Y-%m-%d") for d in water_extent_time_series
]
areas = [d["water_area"] for d in water_extent_time_series]

# Plot the time series
plt.figure(figsize=(10, 5))
plt.plot(dates, areas, marker="o", linestyle="-", color="b")
plt.xlabel("Date")
plt.ylabel("Surface Water Extent (square meters)")
plt.title("Surface Water Extent Time Series")
plt.grid(True)
plt.savefig(f"output/{output}")
plt.show()
