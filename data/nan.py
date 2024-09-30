import csv
total_empty_fields = 0
# Open the CSV file
with open('source2_filt.csv', 'r') as file:
    reader = csv.reader(file)
    for row_number, row in enumerate(reader, start=1):
        for col_number, value in enumerate(row, start=1):
            if value == '':
                print(f"Empty field found at Row {row_number}, Column {col_number}.")


# Open the CSV file
with open('source2_filt.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        # Count how many empty fields (empty strings) are in the row
        total_empty_fields += row.count('')

# Print the total number of empty fields
print(f"Total number of empty fields: {total_empty_fields}")