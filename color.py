import folium
import pandas as pd
import branca.colormap as cm  # To create the color ramp
import altair as alt
import json
from folium.features import VegaLite  # Correct import
import numpy as np
from numpy.linalg import LinAlgError  # Make sure to import this
import json
from folium.plugins import Geocoder
from folium.plugins import GroupedLayerControl


# Test Load CSV data


# Real Load CSV data
source1 = pd.read_csv('data/filt_data/asc1.csv')
source2 = pd.read_csv('data/filt_data/asc2.csv')
source2['Date'] = pd.to_datetime(source2['Date'])

dsc1 = pd.read_csv('data/filt_data/dsc1.csv')
dsc2 = pd.read_csv('data/filt_data/dsc2.csv')
dsc2['Date'] = pd.to_datetime(dsc2['Date'])

kkn4 = pd.read_csv('data/filt_data/kkn4.csv')
kkn4['Date'] = pd.to_datetime(kkn4['Date'])

nast = pd.read_csv('data/filt_data/nast.csv')
nast['Date'] = pd.to_datetime(nast['Date'])
k = kkn4
n = nast

# Load your GeoJSON files
# Load the GeoJSON files
with open('data/contour/2019.geo.cont.geojson') as f:
    geojson_ud1 = json.load(f)

with open('data/contour/2024.geo.cont.geojson') as f:
    geojson_ud2 = json.load(f)



# End Test




# Create a continuous color map (using "viridis" colormap)
colormap = cm.linear.RdYlBu_10.scale(source1['value'].min(), source1['value'].max())
colormap.caption = 'Subsidence Rate (mm/yr)'

#ContourColor

values = [feature['properties']['UD.geo.tif'] for feature in geojson_ud1['features']]
values += [feature['properties']['UD.geo.tif'] for feature in geojson_ud2['features']]

# Calculate the minimum and maximum values
min_value = min(values)
max_value = max(values)

# Create a colormap based on the calculated min and max values
colormap_line = cm.linear.viridis.scale(min_value, max_value)
colormap_line.caption = 'Contour Maps (mm/yr)'
#End Scale

# Initialize the Folium map centered within the same region
map_center = [27.675579, 85.346373]
my_map = folium.Map(location=map_center, zoom_start=12,tiles=None)
Geocoder().add_to(my_map)





def create_chart(id_value):
    # Ensure id_value is treated as an integer to match column names in source2
    chart_data = pd.DataFrame({
        'Date': source2['Date'],
        'Value': source2[str(int(id_value))] / np.cos(np.radians(33.99)) # Cast id_value to int
    })
    
    # Assuming chart_data is already available
    chart_data['Days'] = (chart_data['Date'] - chart_data['Date'].min()).dt.days
    
    # Normalize the data
    x = chart_data['Days'].values
    y = chart_data['Value'].values
    
    # Optional normalization
    x_mean, x_std = np.mean(x), np.std(x)
    y_mean, y_std = np.mean(y), np.std(y)
    
    if y_std == 0 or np.isnan(y_std):  # Check for zero or NaN standard deviation
        print("Standard deviation of y is zero, cannot normalize.")
        print(id_value)
        return None, None
    
    x_norm = (x - x_mean) / x_std
    y_norm = (y - y_mean) / y_std
    
    try:
        slope, intercept = np.polyfit(x_norm, y_norm, 1)  # Fit line: y = mx + b
        slope = slope * (y_std / x_std)  # Rescale slope to original data
        intercept = y_mean - slope * x_mean
    except LinAlgError as e:
        print(f"Linear fit failed: {e}")
        slope, intercept = None, None

    slope_per_year = slope * 365  # Approximate days in a year
    slope_year = f"{slope_per_year:.3f} mm/yr"  # Slope formatted

    # Fetch corresponding value from source1 based on id_value
    filt_slope_value = source1[source1['id'] == id_value]['value'].values[0]  # Get the corresponding 'value'
    filt_slope_text = f"{filt_slope_value:.3f} mm/yr"  # Format as filtered slope
  

    # Unicode subscripts for v₁ and v₂
    v1 = f"v₁ = {slope_year}"
    v2 = f"v₂(filt) = {filt_slope_text}"
  

   # Create a scatter plot with a linear regression line (just for demonstration)
    scatter_plot = alt.Chart(chart_data).mark_circle(size=60).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d', labelAngle=45)),  # Rotate x-axis labels
        y=alt.Y('Value:Q', title='Subsidence Rate (mm/yr)')  # Quantitative axis
    ).properties(
        width=250,  # Adjusted width to fit within the popup
        height=150
    )


    # Add the trendline
    trendline = scatter_plot.transform_regression('Date', 'Value').mark_line(color='red')

    # Combine the scatter plot with the trendline
    scatter_plot_with_trendline = scatter_plot + trendline


    # Create the first title (main title)
    title_chart = alt.Chart(pd.DataFrame({'text': ['2017 - 2024 Subsidence Rate']})).mark_text(
        align='center',
        baseline='bottom',
        font='Courier New',
        fontSize=16,
        fontWeight='bold'
    ).encode(
        text='text:N'
    ).properties(
        width=150,
        height=2
    )

    # Create the second title (subtitle with v₁ and v₂)
    subtitle_chart = alt.Chart(pd.DataFrame({'text': [f"{v1}, {v2}"]})).mark_text(
        align='center',
        baseline='top',
        font='Arial',
        fontSize=12,
        color='gray'
    ).encode(
        text='text:N'
    ).properties(
        width=150,
        height=2
    )


    # Vertically concatenate the titles and the scatter plot
    combined_chart = alt.vconcat(
        title_chart,
        subtitle_chart,
        scatter_plot_with_trendline,
        spacing=5
    ).configure_title(
        anchor='start'  # Apply title configuration to the entire chart
    )

    # Convert the chart to JSON for VegaLite rendering
    vis_json = combined_chart.to_json()

    return combined_chart.to_json(), slope  # Return chart JSON and slope


# Add base map layers similar to Leaflet
tiles = {
    "OpenStreetMap": 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    "CARTO Dark": 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    "CARTO Voyager": 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    "CARTO Positron": 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    "Imagery":'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
}

feature_groups = []


# Iterate through the tile layers and create unique feature groups like fg1, fg2, etc.
for i, (name, tile_url) in enumerate(tiles.items(), start=1):
    fg = folium.FeatureGroup(name=name)  # Create a named feature group (fg1, fg2, etc.)
    folium.TileLayer(
        tiles=tile_url,
        attr="&copy; CARTO",  # Customize attribution based on tile source
        name=name  # Layer name to show in LayerControl
    ).add_to(fg)
    
    # Add the FeatureGroup to the map and to the list for future reference
    my_map.add_child(fg)
    feature_groups.append(fg)  # Collect the feature groups in a list




# Restrict the map bounds similar to Leaflet
bounds = [[27.58173, 85.223921], [27.769427, 85.468825]]
my_map.fit_bounds(bounds)
# Set the max bounds to restrict zooming out
#my_map.options['maxBounds'] = bounds
dsc_map = folium.FeatureGroup(name='Descending')
data1 = folium.FeatureGroup(name='Ascending')
gnss = folium.FeatureGroup(name='GNSS')
data2 = folium.FeatureGroup(name='Hide',show=False)

for i, row in source1.iterrows():
    vis_json, slope = create_chart(row['id'])
    
    # Create a text to display slope
    slope_text = f"Slope: {slope:.2f}" if slope is not None else "Slope: Not available"

    # Create the popup with HTML content
    popup_content = folium.Popup(max_width=300)
    popup_content.add_child(VegaLite(vis_json, width=300, height=150))

    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=3,
        color=colormap(row['value']),  # Color based on depth
        fill=True,
        fill_opacity=0.7,
        popup=popup_content
    ).add_to(data1)


my_map.add_child(data1)
my_map.add_child(data2)



#Descending
def dsc_chart(id_value):
    # Ensure id_value is treated as an integer to match column names in source2
    chart_data = pd.DataFrame({
        'Date': dsc2['Date'],
        'Value': dsc2[str(int(id_value))] / np.cos(np.radians(33.98)) # Cast id_value to int
    })
    
    # Assuming chart_data is already available
    chart_data['Days'] = (chart_data['Date'] - chart_data['Date'].min()).dt.days
    
    # Normalize the data
    x = chart_data['Days'].values
    y = chart_data['Value'].values
    
    # Optional normalization
    x_mean, x_std = np.mean(x), np.std(x)
    y_mean, y_std = np.mean(y), np.std(y)
    
    if y_std == 0 or np.isnan(y_std):  # Check for zero or NaN standard deviation
        print("Standard deviation of y is zero, cannot normalize.")
        print(id_value)
        return None, None
    
    x_norm = (x - x_mean) / x_std
    y_norm = (y - y_mean) / y_std
    
    try:
        slope, intercept = np.polyfit(x_norm, y_norm, 1)  # Fit line: y = mx + b
        slope = slope * (y_std / x_std)  # Rescale slope to original data
        intercept = y_mean - slope * x_mean
    except LinAlgError as e:
        print(f"Linear fit failed: {e}")
        slope, intercept = None, None

    slope_per_year = slope * 365  # Approximate days in a year
    slope_year = f"{slope_per_year:.3f} mm/yr"  # Slope formatted

    # Fetch corresponding value from source1 based on id_value
    filt_slope_value = dsc1[dsc1['id'] == id_value]['value'].values[0]  # Get the corresponding 'value'
    filt_slope_text = f"{filt_slope_value:.3f} mm/yr"  # Format as filtered slope
  

    # Unicode subscripts for v₁ and v₂
    v1 = f"v₁ = {slope_year}"
    v2 = f"v₂(filt) = {filt_slope_text}"
  

   # Create a scatter plot with a linear regression line (just for demonstration)
    scatter_plot = alt.Chart(chart_data).mark_circle(size=60).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d', labelAngle=45)),  # Rotate x-axis labels
        y=alt.Y('Value:Q', title='Subsidence Rate (mm/yr)')  # Quantitative axis
    ).properties(
        width=250,  # Adjusted width to fit within the popup
        height=150
    )


    # Add the trendline
    trendline = scatter_plot.transform_regression('Date', 'Value').mark_line(color='red')

    # Combine the scatter plot with the trendline
    scatter_plot_with_trendline = scatter_plot + trendline


    # Create the first title (main title)
    title_chart = alt.Chart(pd.DataFrame({'text': ['2017 - 2024 Subsidence Rate']})).mark_text(
        align='center',
        baseline='bottom',
        font='Courier New',
        fontSize=16,
        fontWeight='bold'
    ).encode(
        text='text:N'
    ).properties(
        width=150,
        height=2
    )

    # Create the second title (subtitle with v₁ and v₂)
    subtitle_chart = alt.Chart(pd.DataFrame({'text': [f"{v1}, {v2}"]})).mark_text(
        align='center',
        baseline='top',
        font='Arial',
        fontSize=12,
        color='gray'
    ).encode(
        text='text:N'
    ).properties(
        width=150,
        height=2
    )


    # Vertically concatenate the titles and the scatter plot
    combined_chart = alt.vconcat(
        title_chart,
        subtitle_chart,
        scatter_plot_with_trendline,
        spacing=5
    ).configure_title(
        anchor='start'  # Apply title configuration to the entire chart
    )

    # Convert the chart to JSON for VegaLite rendering
    vis_json = combined_chart.to_json()

    return combined_chart.to_json(), slope  # Return chart JSON and slope


for i, row in dsc1.iterrows():
    vis_json, slope = dsc_chart(row['id'])
    
    # Create a text to display slope
    slope_text = f"Slope: {slope:.2f}" if slope is not None else "Slope: Not available"

    # Create the popup with HTML content
    popup_content = folium.Popup(max_width=300)
    popup_content.add_child(VegaLite(vis_json, width=300, height=150))

    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=3,
        color=colormap(row['value']),  # Color based on depth
        fill=True,
        fill_opacity=0.7,
        popup=popup_content
    ).add_to(dsc_map)


my_map.add_child(dsc_map)

# Function to style each feature based on the 'UD.geo.tif' value
def style_function(feature):
    value = feature['properties']['UD.geo.tif']
    return {
        'color': colormap_line(value),  # Use the colormap to assign colors
        'weight': feature['properties'].get('_weight', 1),
        'opacity': feature['properties'].get('_opacity', 0.5)
    }

# Function to create a popup with the value of 'UD.geo.tif'
def get_popup(feature):
    value = feature['properties']['UD.geo.tif']
    return folium.Popup(f'Value: {value}', parse_html=True)


fg2 = folium.FeatureGroup(name='2019',show=False)


# Step 3: Add the GeoJSON layers to the map
geojson_layer1 =folium.GeoJson(
    geojson_ud1,
    name='2019',
    popup=get_popup,  # Add popup functionality
    style_function=style_function 
).add_to(fg2)

# Bind popups to the features in geojson_data1
for feature in geojson_ud1['features']:
    geojson_layer1.add_child(
        folium.GeoJsonTooltip(fields=['UD.geo.tif'], aliases=['Value:'], localize=True)
    )

my_map.add_child(fg2)


fg3 = folium.FeatureGroup(name='2024',show=False)

geojson_layer2=folium.GeoJson(
    geojson_ud2,
    name='2024',
    popup=get_popup,  # Add popup functionality
    style_function=style_function
).add_to(fg3)


# Bind popups to the features in geojson_data2
for feature in geojson_ud2['features']:
    geojson_layer2.add_child(
        folium.GeoJsonTooltip(fields=['UD.geo.tif'], aliases=['Value:'], localize=True)
    )

my_map.add_child(fg3)


fg1 = folium.FeatureGroup(name='Hide',show=False)
my_map.add_child(fg1)



# Create Graph for GNSS

def create_graph(data, slope_text, station_name):
    # Ensure id_value is treated as an integer to match column names in source2
    chart_data = pd.DataFrame({
        'Date': data['Date'],
        'Value': data['Up'] 
    })
    
    # Assuming chart_data is already available
    chart_data['Days'] = (chart_data['Date'] - chart_data['Date'].min()).dt.days
    
    # Normalize the data
    x = chart_data['Days'].values
    y = chart_data['Value'].values
    
    # Optional normalization
    x_mean, x_std = np.mean(x), np.std(x)
    y_mean, y_std = np.mean(y), np.std(y)
    
    if y_std == 0 or np.isnan(y_std):  # Check for zero or NaN standard deviation
        print("Standard deviation of y is zero, cannot normalize.")
        print(id_value)
        return None, None
    
    x_norm = (x - x_mean) / x_std
    y_norm = (y - y_mean) / y_std
    
    try:
        slope, intercept = np.polyfit(x_norm, y_norm, 1)  # Fit line: y = mx + b
        slope = slope * (y_std / x_std)  # Rescale slope to original data
        intercept = y_mean - slope * x_mean
    except LinAlgError as e:
        print(f"Linear fit failed: {e}")
        slope, intercept = None, None

    slope_per_year = slope * 365  # Approximate days in a year
    slope_year = f"{slope_per_year:.3f} mm/yr"  # Slope formatted


  

    # Unicode subscripts for v₁ and v₂
    v1 = f"v₁ = {slope_year}"
    v2 = f"v₂(filt) ={slope_text} "
  

   # Create a scatter plot with a linear regression line (just for demonstration)
    scatter_plot = alt.Chart(chart_data).mark_circle(size=60).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d', labelAngle=45)),  # Rotate x-axis labels
        y=alt.Y('Value:Q', title='Subsidence Rate (mm/yr)')  # Quantitative axis
    ).properties(
        width=250,  # Adjusted width to fit within the popup
        height=150
    )


    # Add the trendline
    trendline = scatter_plot.transform_regression('Date', 'Value').mark_line(color='red')

    # Combine the scatter plot with the trendline
    scatter_plot_with_trendline = scatter_plot + trendline


    # Create the first title (main title)
    title_chart = alt.Chart(pd.DataFrame({'text': [station_name]})).mark_text(
        align='center',
        baseline='bottom',
        font='Courier New',
        fontSize=16,
        fontWeight='bold'
    ).encode(
        text='text:N'
    ).properties(
        width=150,
        height=2
    )

    # Create the second title (subtitle with v₁ and v₂)
    subtitle_chart = alt.Chart(pd.DataFrame({'text': [f"{v1}, {v2}"]})).mark_text(
        align='center',
        baseline='top',
        font='Arial',
        fontSize=12,
        color='gray'
    ).encode(
        text='text:N'
    ).properties(
        width=150,
        height=2
    )


    # Vertically concatenate the titles and the scatter plot
    combined_chart = alt.vconcat(
        title_chart,
        subtitle_chart,
        scatter_plot_with_trendline,
        spacing=5
    ).configure_title(
        anchor='start'  # Apply title configuration to the entire chart
    )

    # Convert the chart to JSON for VegaLite rendering
    vis_json = combined_chart.to_json()

    return combined_chart.to_json(), slope  # Return chart JSON and slope

def create_popup(data, slope_text, station_name):
    # Generate VegaLite JSON from Altair chart
    vis_json, slope = create_graph(data, slope_text, station_name)
    
    # Create the popup with HTML content
    popup_content = folium.Popup(max_width=300)
    
    # Add VegaLite chart to the popup
    popup_content.add_child(VegaLite(vis_json, width=300, height=150))
    
    return popup_content


station_kkn4 = "KKN4"
slope_kkn4 = "-0.261±0.955 mm/yr"

station_nast = "NAST"
slope_nast = "125±4.4 mm/yr"


folium.Marker([27.657, 85.328], popup=create_popup(n,slope_nast,station_nast), tooltip="NAST").add_to(gnss)
folium.Marker([27.801,  85.279], popup=create_popup(k,slope_kkn4,station_kkn4), tooltip="KKN4").add_to(gnss)
my_map.add_child(gnss)




# Add the color map legend to the bottom right of the map
colormap.add_to(my_map)
colormap_line.add_to(my_map)

#Reference
ref_location = [27.770668473560363, 85.3064407329075]
# Add a triangular marker
folium.RegularPolygonMarker(
    location=ref_location,
    number_of_sides=4,        # Number of sides for a triangle
    radius=5,                # Radius of the triangle
    color='black',              # Border color
    fill=True,                # Whether to fill the triangle
    fill_color='black',      # Fill color
    fill_opacity=1,         # Opacity of the fill
    popup='Reference Point'    # Popup content
).add_to(my_map)

# Add layer control to toggle between base maps
folium.LayerControl(collapsed=False).add_to(my_map)




GroupedLayerControl(
    groups={
        '<span style="font-size: 16px; color: green;"><strong>Ascending<br></strong></span><a href="https://www.example.com" target="_blank" style="font-size: 8px; color: red; text-decoration: none;"><strong>Click for Descending</strong></a> <br> Contour Maps': [fg3, fg2, fg1],  # Contour map layers
        'Map style': feature_groups,
        'InSAR': [dsc_map,data1,gnss,data2]
    },
    collapsed=False,  # Keep the layer control expanded by default
).add_to(my_map)

# Save the map to an HTML file
my_map.save('index.html')
