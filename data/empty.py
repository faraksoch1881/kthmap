import pandas as pd

# Load the CSV file
df = pd.read_csv('source2_filt.csv')

# Check for empty fields
empty_fields = df.isnull().sum().sum()  # Count the total number of NaN values

if empty_fields > 0:
    print(f"There are {empty_fields} empty fields (empty cells) in the CSV file.")
else:
    print("There are no empty fields in the CSV file.")

