import pandas as pd

# Read the CSV file
df = pd.read_csv('filt_output_removed_nan_gridD.csv')

# Transpose the dataframe
df_transposed = df.transpose()

# Reset the index so that it writes the transposed DataFrame correctly
df_transposed.reset_index(inplace=True)

# Rename the first column to 'Date'
df_transposed.columns = ['Date'] + list(range(1, len(df_transposed.columns)))

# Save the transposed DataFrame to a new CSV file
df_transposed.to_csv('source2_grid.csv', index=False)

print("Transposition complete. The new file is saved as 'source2_grid.csv'.")
