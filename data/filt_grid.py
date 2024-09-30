import pandas as pd
import numpy as np

# Load your DataFrame
df = pd.read_csv('filt_output_removed_nanD.csv')

# Ensure no NaN values in important columns
df = df.dropna(subset=['lat', 'lon', 'value'])

# Define the earth radius in meters
earth_radius = 6371000  # Earth radius in meters

# Calculate the size of 1 degree of latitude and longitude in meters
lat_degree_meters = (2 * np.pi * earth_radius) / 360  # meters per degree of latitude
lon_degree_meters = (2 * np.pi * earth_radius * np.cos(np.radians(df['lat'].mean()))) / 360  # meters per degree of longitude

# Bin size in degrees for 200 meters
bin_size_lat = 500 / lat_degree_meters
bin_size_lon = 500 / lon_degree_meters

# Group by calculated bins without adding extra columns
# Using floor division to determine the bins
grouped = df.groupby([
    (df['lat'] // bin_size_lat),
    (df['lon'] // bin_size_lon)
])

# Initialize a list to store the indices of the rows to keep
indices_to_keep = []

# Iterate through each group
for name, group in grouped:
    if not group.empty:  # Check if the group is not empty
        idx_min = group['value'].idxmin()  # Get the index of the minimum value
        indices_to_keep.append(idx_min)  # Append to the list

# Filter the DataFrame to keep only the rows with minimum values in each bin
filtered_df = df.loc[indices_to_keep]

# Save the filtered DataFrame to a new CSV
filtered_df.to_csv('filt_output_removed_nan_grid.csv', index=False)

print("Filtered data saved to final_output_removed_nan_grid.csv")
