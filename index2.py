import folium
import pandas as pd
import branca.colormap as cm  # To create the color ramp
import altair as alt

# Load CSV data
csv_data = pd.read_csv('data/258_well_loc.csv')

# Remove rows with missing or invalid depth values
csv_data = csv_data.dropna(subset=['depth'])  # Drop rows with NaN in 'depth'


# Sort the data by depth to avoid threshold issues
csv_data = csv_data.sort_values(by='depth')


# Define the columns for the dates (after 'value')
date_columns = ['20170104', '20170128', '20170209', '20170304', '20170322', '20170415']

# define data for demonstration
source = pd.DataFrame(
    {
        'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
        'b': [28, 55, 43, 91, 81, 53, 19, 87, 52],
    }
)

# create an altair chart, then convert to JSON
chart = alt.Chart(csv_data).mark_bar().encode(x='SN', y='depth')
vis1 = chart.to_json()



# Initialize the Folium map centered within the same region
map_center = [27.675579, 85.346373]
my_map = folium.Map(location=map_center, zoom_start=12,tiles=None)

# Add base map layers similar to Leaflet
tiles = {
    "CARTO Dark": 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    "CARTO Voyager": 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    "CARTO Positron": 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    "OpenStreetMap": 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
}

for name, tile_url in tiles.items():
    folium.TileLayer(tiles=tile_url, attr="&copy; CARTO", name=name).add_to(my_map)



# Create a continuous color map (using "viridis" colormap)
colormap = cm.linear.RdYlBu_10.scale(csv_data['depth'].min(), csv_data['depth'].max())
colormap.caption = 'Depth Color Scale'

# Restrict the map bounds similar to Leaflet
bounds = [[27.58173, 85.223921], [27.769427, 85.468825]]
my_map.fit_bounds(bounds)
# Set the max bounds to restrict zooming out
my_map.options['maxBounds'] = bounds




# Add CSV circles with color based on depth and popup info
for i, row in csv_data.iterrows():
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=2,  # Circle size
        color=colormap(row['depth']),  # Color based on depth
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(max_width=400).add_child(folium.VegaLite(vis1, width=400, height=300)),
    ).add_to(my_map)



# Add the color map legend to the bottom right of the map
colormap.add_to(my_map)

# Add layer control to toggle between base maps
folium.LayerControl(collapsed=False).add_to(my_map)


# Save the map to an HTML file
my_map.save('map.html')
