import json
import folium
import overpy
from constants import RADIUS, TAG, QUERY_TEMPLATE, NTH_POINT

#from source_code.constants import NTH_POINT

api = overpy.Overpass()

with open('TRASA1.geojson', encoding='utf-8-sig') as geojson:
    data = json.load(geojson)
    geometry = data.get('geometry')

# coordinates in route file are stored in (latitude, longitude) order
# it must be swapped
coordinates = []
for lat, lon in geometry.get('coordinates'):
    coordinates.append((lon, lat))

# calculate the middle point when the map loads
middle_idx = len(coordinates) // 2
center = coordinates[middle_idx]

# create a map pointing at middle route with initial zoom of 6
my_map = folium.Map(location=center, zoom_start=8)
folium.PolyLine(coordinates).add_to(my_map)

# query every 500th point (from 4464) which is about 75 km for this route
for latitude, longitude in coordinates[::NTH_POINT]:
    result = api.query(
        QUERY_TEMPLATE.format(
            tag=TAG, radius=RADIUS, lat=latitude, lon=longitude
        )
    )

    # place found fuel stations as markers on the map
    for node in result.nodes:
        folium.map.Marker([node.lat, node.lon],
                          popup=node.tags.get('brand', TAG)).add_to(my_map)

my_map.save('map11.html')
