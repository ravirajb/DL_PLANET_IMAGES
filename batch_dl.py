import os
import requests
from requests.auth import HTTPBasicAuth
import json

os.putenv("PL_API_KEY", "5c022171d55b47e4b74c3c3710e7e237")
#os.system("echo $PL_API_KEY")

# setup auth
session = requests.Session()
session.auth = (os.environ['PL_API_KEY'], '')

# the geo json geometry object we got from geojson.io
geo_json_geometry = {
  "type": "Polygon",
  "coordinates": [
    [
      [
        -122.52227783203125,
        40.660847697284815
      ],
      [
        -122.52227783203125,
        40.987154933797335
      ],
      [
        -122.01690673828124,
        40.987154933797335
      ],
      [
        -122.01690673828124,
        40.660847697284815
      ],
      [
        -122.52227783203125,
        40.660847697284815
      ]
    ]
  ]
}

# filter for items the overlap with our chosen geometry
geometry_filter = {
  "type": "GeometryFilter",
  "field_name": "geometry",
  "config": geo_json_geometry
}

# filter images acquired in a certain date range
date_range_filter = {
  "type": "DateRangeFilter",
  "field_name": "acquired",
  "config": {
    "gte": "2016-07-01T00:00:00.000Z",
    "lte": "2016-08-01T00:00:00.000Z"
  }
}

# filter any images which are more than 50% clouds
cloud_cover_filter = {
  "type": "RangeFilter",
  "field_name": "cloud_cover",
  "config": {
    "lte": 0.5
  }
}

# create a filter that combines our geo and date filters
# could also use an "OrFilter"
redding_reservoir = {
  "type": "AndFilter",
  "config": [geometry_filter, date_range_filter, cloud_cover_filter]
}


# Stats API request object
stats_endpoint_request = {
  "interval": "day",
  "item_types": ["REOrthoTile"],
  "filter": redding_reservoir
}

# Search API request object
search_endpoint_request = {
  "item_types": ["REOrthoTile"],
  "filter": redding_reservoir
}


# fire off the POST request
result = \
  requests.post(
    'https://api.planet.com/data/v1/quick-search',
    auth=HTTPBasicAuth(os.environ['PL_API_KEY'], ''),
    json=search_endpoint_request)


#print result.text

out_json = json.loads(result.text)
i=0

for feature in out_json['features']: 
	if i == 0:
		item_id = feature['id']
	i=i+1
	print feature['id']

item_id = "20160707_195147_1057916_RapidEye-1"
item_type = "REOrthoTile"
asset_type = "visual"


# request an item
item = \
  session.get(
    ("https://api.planet.com/data/v1/item-types/" +
    "{}/items/{}/assets/").format(item_type, item_id))

# extract the activation url from the item for the desired asset
item_activation_url = item.json()[asset_type]["location"]
print item_activation_url

response = session.get(item_activation_url)

print response.status_code

with open('./file01.tiff', 'wb') as f:
	for chunk in response.iter_content(1024):
		f.write(chunk)