import folium
import pandas as pd
import branca.colormap as cm  # To create the color ramp
import altair as alt
import json
from folium.features import VegaLite  # Correct import
import numpy as np
from numpy.linalg import LinAlgError  # Make sure to import this

# Load CSV data
source1 = pd.read_csv('data/filt_data/source1_filt.csv')
source2 = pd.read_csv('data/filt_data/source2_filt.csv')


# Load the GeoJSON files
with open('data/contour/2019.geo.cont.geojson') as f:
    geojson_ud1 = json.load(f)

with open('data/contour/2024.geo.cont.geojson') as f:
    geojson_ud2 = json.load(f)



source2['Date'] = pd.to_datetime(source2['Date'])
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

def create_chart(id_value):
    # Ensure id_value is treated as an integer to match column names in source2
    chart_data = pd.DataFrame({
        'Date': source2['Date'],
        'Value': source2[str(int(id_value))] / np.cos(np.radians(34)) # Cast id_value to int
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
    v2 = f"v₂(LoS) = {filt_slope_text}"
  

   # Create a scatter plot with a linear regression line (just for demonstration)
    scatter_plot = alt.Chart(chart_data).mark_circle(size=60).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d', labelAngle=90)),  # Rotate x-axis labels
        y=alt.Y('Value:Q', title='Subsidence Rate (mm/yr)')  # Quantitative axis
    ).properties(
        width=300,  # Adjusted width to fit within the popup
        height=200
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
        width=300,
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
        width=300,
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
    "CARTO Dark": 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    "CARTO Voyager": 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    "CARTO Positron": 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    "OpenStreetMap": 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    "Imagery":'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
}

for name, tile_url in tiles.items():
    folium.TileLayer(tiles=tile_url, attr="&copy; CARTO", name=name).add_to(my_map)




# Restrict the map bounds similar to Leaflet
bounds = [[27.58173, 85.223921], [27.769427, 85.468825]]
#my_map.fit_bounds(bounds)
# Set the max bounds to restrict zooming out
#my_map.options['maxBounds'] = bounds




for i, row in source1.iterrows():
    vis_json, slope = create_chart(row['id'])
    
    # Create a text to display slope
    slope_text = f"Slope: {slope:.2f}" if slope is not None else "Slope: Not available"

    # Create the popup with HTML content
    popup_content = folium.Popup(max_width=500)
    popup_content.add_child(VegaLite(vis_json, width=400, height=300))

    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=5,
        fill=True,
        fill_opacity=0.7,
        popup=popup_content
    ).add_to(my_map)

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


# Step 3: Add the GeoJSON layers to the map
geojson_layer1 =folium.GeoJson(
    geojson_ud1,
    name='2019',
    show=False,
    popup=get_popup,  # Add popup functionality
    style_function=style_function 
).add_to(my_map)

# Bind popups to the features in geojson_data1
for feature in geojson_ud1['features']:
    geojson_layer1.add_child(
        folium.GeoJsonTooltip(fields=['UD.geo.tif'], aliases=['Value:'], localize=True)
    )


geojson_layer2=folium.GeoJson(
    geojson_ud2,
    name='2024',
    show=False,
    popup=get_popup,  # Add popup functionality
    style_function=style_function
).add_to(my_map)


# Bind popups to the features in geojson_data2
for feature in geojson_ud2['features']:
    geojson_layer2.add_child(
        folium.GeoJsonTooltip(fields=['UD.geo.tif'], aliases=['Value:'], localize=True)
    )

# Add the color map legend to the bottom right of the map
#colormap.add_to(my_map)
colormap_line.add_to(my_map)

# Add layer control to toggle between base maps
folium.LayerControl(collapsed=False).add_to(my_map)


# Save the map to an HTML file
my_map.save('index.html')
