import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Load cleaned data
jan_cleaned = pd.read_csv('jan_cleaned.csv')
feb_cleaned = pd.read_csv('feb_cleaned.csv')
ytd_cleaned = pd.read_csv('ytd_cleaned.csv')

# Streamlit App
st.title('Financial Data Analysis Case Study')

# Dropdown menu for selecting the data set
dataset = st.sidebar.selectbox('Select Data Set', ('January', 'February', 'Year-to-Date'))

# Load the selected data set
if dataset == 'January':
    data = jan_cleaned
    st.header('Data for January')
elif dataset == 'February':
    data = feb_cleaned
    st.header('Data for February')
else:
    data = ytd_cleaned
    st.header('Year-to-Date Data')

# Add "All" option to the brand list
brands = ["All"] + list(data['Brand'].unique())
selected_brand = st.selectbox('Select Brand to Display', brands)

# Filter the data based on the selected brand
if selected_brand != "All":
    filtered_data = data[data['Brand'] == selected_brand]
else:
    filtered_data = data

# Display selected data set for the chosen brand
st.dataframe(filtered_data)

# Visualizations
st.header('Visualizations')

# Dropdown menu for selecting the category under visualizations
category = st.selectbox('Select Category for Visualization', ('Dollars', 'Units', 'MQLs'))

# Double bar chart for selected category (Dollars, Units, or MQLs)
st.subheader(f'Forecasted {category} vs Final Bookings Actual {category}')
st.markdown('###### Here data is presented showing the forecasted bookings side by side for each brand with the final bookings')

# Filter and prepare the data, dropping rows with any NaN values in Bookings Forecast or Final Bookings Actual
filtered_category_data = filtered_data[filtered_data['Category'] == category][['Brand', 'Bookings Forecast', 'Final Bookings Actual']].dropna(subset=['Bookings Forecast', 'Final Bookings Actual'])
# Drop rows where both Bookings Forecast and Final Bookings Actual are zero
filtered_category_data = filtered_category_data[(filtered_category_data['Bookings Forecast'] != 0) | (filtered_category_data['Final Bookings Actual'] != 0)]
# Set the Brand as the index
filtered_category_data = filtered_category_data.set_index('Brand')
# Create the bar chart using matplotlib
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_alpha(0)  # Make the figure background transparent
ax.patch.set_alpha(0)   # Make the axes background transparent
filtered_category_data.plot(kind='bar', ax=ax)
ax.set_title(f"Forecasted {category} vs Final Bookings Actual {category}", color='white')
ax.set_xlabel("Brand", color='white')
ax.set_ylabel(f"{category}", color='white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.spines['bottom'].set_color('white')
ax.spines['top'].set_color('white')
ax.spines['left'].set_color('white')
ax.spines['right'].set_color('white')
plt.xticks(rotation=70, color='white')
plt.yticks(color='white')
# Move legend outside the plot
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False, labelcolor='white')
st.pyplot(fig)

# New chart for brands that met budget and those that did not, showing the percentage difference
st.subheader(f'Percentage Bookings to Budget for {category}')
st.markdown('###### This Data shows by what percentage each brand either hit or missed forecast')

# Filter and prepare the data for budget comparison
budget_data = filtered_data[filtered_data['Category'] == category][['Brand', 'Bookings Budget', 'Final Bookings Actual']].dropna(subset=['Bookings Budget', 'Final Bookings Actual'])
# Calculate the percentage difference from budget
budget_data['Percentage Difference'] = ((budget_data['Final Bookings Actual'] - budget_data['Bookings Budget']) / budget_data['Bookings Budget']) * 100
# Set the Brand as the index
budget_data = budget_data.set_index('Brand')
# Determine the colors for each bar
colors = ['tab:orange' if x < 0 else 'tab:blue' for x in budget_data['Percentage Difference']]
# Create the percentage difference bar chart using matplotlib
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_alpha(0)  # Make the figure background transparent
ax.patch.set_alpha(0)   # Make the axes background transparent
budget_data['Percentage Difference'].plot(kind='bar', color=colors, ax=ax)
ax.set_title(f"Percentage Bookings to Budget for {category}", color='white')
ax.set_xlabel("Brand", color='white')
ax.set_ylabel("Percentage Difference (%)", color='white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.spines['bottom'].set_color('white')
ax.spines['top'].set_color('white')
ax.spines['left'].set_color('white')
ax.spines['right'].set_color('white')
plt.xticks(rotation=90, color='white')
plt.yticks(color='white')
st.pyplot(fig)

# New donut chart for final bookings actual information using Plotly
st.subheader(f'Brand Percentage of Company by {category}')
st.markdown('###### Each brand in the company is represented in this donut chart to show how much of the final '
            'bookings each brand did by percentage.')

# Filter and prepare the data for the donut chart
donut_data = filtered_data[filtered_data['Category'] == category][['Brand', 'Final Bookings Actual']].dropna(subset=['Final Bookings Actual'])
donut_data = donut_data[donut_data['Final Bookings Actual'] > 0]  # Exclude brands with zero data
# Create the donut chart using Plotly
fig = go.Figure(data=[go.Pie(labels=donut_data['Brand'], values=donut_data['Final Bookings Actual'], hole=.4, hoverinfo="label+percent", textinfo='none')])
fig.update_layout(
    annotations=[dict(text='Bookings', x=0.5, y=0.5, font_size=20, showarrow=False)],
    showlegend=True,
    legend=dict(
        x=1,
        y=1,
        traceorder="normal",
        font=dict(
            size=12,
            color="white"
        ),
        bgcolor='rgba(0,0,0,0)',
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white')
)
st.plotly_chart(fig)


if __name__ == '__app__':
    st.run()