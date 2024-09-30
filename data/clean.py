import pandas as pd

# Load the CSV file
df = pd.read_csv('final_outputD.csv')

# Drop rows that contain any NaN values
df_cleaned = df.dropna()

# Save the cleaned DataFrame to a new CSV file
df_cleaned.to_csv('filt_output_removed_nan.csv', index=False)

print("Filtered CSV file 'filt_output_removed_nan.csv' has been created.")
