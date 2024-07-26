import pandas as pd

# Load the Excel workbook
file_path = 'TBH Case Study - Analyst.xlsx'  # Make sure this is the correct path to your file
workbook = pd.ExcelFile(file_path)


def clean_data(df, month):
    # Drop rows past row 227
    df = df.iloc[:227]

    # Drop completely empty columns
    df = df.dropna(axis=1, how='all')

    # Forward fill the brand column
    df['Brand'] = df['Brand'].ffill()

    # Drop rows where the brand is 'Other'
    df = df[df['Brand'] != 'Other']

    # Rename 'MQLs*' to 'MQLs'
    df.loc[df['Brand'] == 'MQLs*', 'Brand'] = 'MQLs'

    # Only keep relevant columns and rename them for consistency
    # Select and rename columns based on the timeframe
    if month == 'Jan':
        df = df[['Brand', 'Jan Bookings Budget', 'Jan Bookings Forecast', 'Jan Final Bookings Actual']]
        df.columns = ['Brand', 'Bookings Budget', 'Bookings Forecast', 'Final Bookings Actual']
    elif month == 'Feb':
        df = df[['Brand', 'Feb Bookings Budget', 'Feb Bookings Forecast', 'Feb MM Bookings Actual']]
        df.columns = ['Brand', 'Bookings Budget', 'Bookings Forecast', 'Final Bookings Actual']
    else:
        df = df[['Brand', 'Cons Bookings Budget', 'Cons Bookings Forecast', 'Cons Final Bookings Actual']]
        df.columns = ['Brand', 'Bookings Budget', 'Bookings Forecast', 'Final Bookings Actual']

    # Create a new dataframe to hold cleaned data
    cleaned_df = pd.DataFrame(columns=['Brand', 'Category', 'Bookings Budget', 'Bookings Forecast', 'Final Bookings Actual'])

    current_brand = None
    current_rows = {}

    # Iterate over each row in the dataframe
    for _, row in df.iterrows():
        brand = row['Brand']
        # If we encounter a new brand
        if brand not in ['MQLs', 'Units', 'Dollars']:
            if current_brand:
                # Ensure all categories have been added for the previous brand
                for category in ['MQLs', 'Units', 'Dollars']:
                    if category not in current_rows:
                        current_rows[category] = {
                            'Brand': current_brand,
                            'Category': category,
                            'Bookings Budget': 0,
                            'Bookings Forecast': 0,
                            'Final Bookings Actual': 0
                        }
                # Add all the rows for the current brand to the cleaned dataframe
                for row_to_add in current_rows.values():
                    cleaned_df = pd.concat([cleaned_df, pd.DataFrame([row_to_add])], ignore_index=True)
            # Start processing the new brand
            current_brand = brand
            current_rows = {}
        # Determine the category based on the brand name
        category = 'MQLs' if 'MQLs' in brand else ('Units' if 'Units' in brand else ('Dollars' if 'Dollars' in brand else None))
        if category:
            # Add the row data to the current_rows dictionary for the determined category
            current_rows[category] = {
                'Brand': current_brand,
                'Category': category,
                'Bookings Budget': row['Bookings Budget'],
                'Bookings Forecast': row['Bookings Forecast'],
                'Final Bookings Actual': row['Final Bookings Actual']
            }
    # Ensure the last processed brand is added to the cleaned dataframe
    if current_brand:
        for category in ['MQLs', 'Units', 'Dollars']:
            if category not in current_rows:
                current_rows[category] = {
                    'Brand': current_brand,
                    'Category': category,
                    'Bookings Budget': 0,
                    'Bookings Forecast': 0,
                    'Final Bookings Actual': 0
                }
        for row_to_add in current_rows.values():
            cleaned_df = pd.concat([cleaned_df, pd.DataFrame([row_to_add])], ignore_index=True)

    return cleaned_df

# Load the relevant sheets
jan_final_by_product_df = pd.read_excel(file_path, sheet_name='Jan Final by Product')
feb_final_by_product_df = pd.read_excel(file_path, sheet_name='Feb Final by Product')
ytd_final_by_product_df = pd.read_excel(file_path, sheet_name='Con YTD Final by Prod DET')

# Apply cleaning to each dataframe
jan_cleaned = clean_data(jan_final_by_product_df, 'Jan')
feb_cleaned = clean_data(feb_final_by_product_df, 'Feb')
ytd_cleaned = clean_data(ytd_final_by_product_df, 'YTD')

# Drop 'Procentive' and 'Billcare' brands from January cleaned data due to them being reported on February
jan_cleaned = jan_cleaned[~jan_cleaned['Brand'].isin(['Procentive', 'Billcare'])]

# Combine duplicate brands
jan_cleaned = jan_cleaned.groupby(['Brand', 'Category']).sum().reset_index()
feb_cleaned = feb_cleaned.groupby(['Brand', 'Category']).sum().reset_index()
ytd_cleaned = ytd_cleaned.groupby(['Brand', 'Category']).sum().reset_index()

# Display the cleaned data
print("January Cleaned Data")
print(jan_cleaned.head(20))

print("\nFebruary Cleaned Data")
print(feb_cleaned.head(20))

print("\nYear-to-Date Cleaned Data")
print(ytd_cleaned.head(20))

# Save cleaned data for use in Streamlit app
jan_cleaned.to_csv('jan_cleaned.csv', index=False)
feb_cleaned.to_csv('feb_cleaned.csv', index=False)
ytd_cleaned.to_csv('ytd_cleaned.csv', index=False)