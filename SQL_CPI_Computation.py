import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector

# The following code is used to connect to the database table located in my PC with a local SQL host
'''
# Connect to the mySQL database
cnx = mysql.connector.connect(user = 'root', password = 'PassWord', host = '127.0.0.1', database = 'ca2project')
sql_code = 'SELECT * FROM CPI_Quarterly'
df = pd.read_sql(sql_code, con = cnx)
'''

# The following replacement code is used to connect to the same table saved as a local csv file in the 'assets' folder
# Read the csv file into the pandas dataframe
path = 'assets/CPI_Quarterly.csv'
df = pd.read_csv(path, sep=',', skiprows=10, nrows=152)

# Rename the 'Data Series' to 'items' and remove empty spaces from the values in the column
df = df.rename(columns={'Data Series' : 'items'})
df['items'] = df['items'].str.strip()

# Trim the trailing spaces from the column headers
df.columns = df.columns.str.strip()

# Create a new column containing the difference in CPI value for '2023 2Q' and '2019 1Q'
df['diff'] = df['2023 2Q'] - df['2019 1Q']
df['diff'] = df['diff'].round(1)

# Extract the main categories for items and their corresponding rows
main_category = ['Food', 'Clothing & Footwear', 'Housing & Utilities', 'Household Durables & Services', 'Health Care', 'Transport', 'Communication', 'Recreation & Culture', 'Education', 'Miscellaneous Goods & Services']

# Create a new column with values 'Main' or 'Sub' dependent on the values in the 'items' columns
df['group'] = df['items'].apply(lambda x: 'Main' if x in main_category else 'Sub')

# Extract the subset of the dataframe containing only the values for the main categories
df_main = df[df['group'] == 'Main']
df_main_latest = df_main['2023 2Q'].reset_index()
price = np.array(df_main_latest['2023 2Q'])
items = np.array(df_main['items'])

try:
    # Initialize an empty list to store user inputs
    user_inputs = []
    print('\nEnter a numeric value between 0 to 100 for each of the CPI components '
          'based on the relative weight which you spend on the respective items\n')
    # Get 10 user inputs
    for i in range(len(items)):
        user_input = int(input(f'Value for {items[i]}: '))
        if 0 <= user_input <= 100:
            user_inputs.append(user_input)
        else:
            print("Invalid input! Please enter a numeric value between 0 and 100.")
            exit()

    # Calculate the sum of user inputs
    total_sum = sum(user_inputs)

    # Refactor the values to ensure the total sum is 100
    refactored_values = [(num / total_sum) * 100 for num in user_inputs]

    # Print the refactored values
    s='#'
    print(f'\n{s*40}\nYour CPI Weightage refactored to 100%:\n')
    for item, val in zip(items,refactored_values):
        print(f'{item}: {val:.1f}')
    print(f'\n{s*40}')
except ValueError:
    print("Invalid input! Please enter an integer.")
except Exception as e:
    print("An error occurred:", e)

refactored_values = np.array(refactored_values) / 100
CPI_user = np.sum(price * refactored_values)
CPI_2023  = 113.6
CPI_data = np.array([CPI_2023, CPI_user])


# Sorting the values in ascending order for better visualisation
sorted_indices = np.argsort(user_inputs)
sorted_user_inputs = np.array(user_inputs)[sorted_indices]
sorted_items = np.array(items)[sorted_indices]

# Define the figure and subplots
fig, axs = plt.subplots(1, 2, width_ratios=[5,4])

# Define the color and plot the pie chart with custom layout, text attribute, percentage labels and positioning
colors = ['#BAB0AC', '#9D755D', '#FF9DA6', '#B279A2', '#EECA3B', '#54A24B', '#72B7B2', '#E45756', '#F58518', '#4C78A8']
sector, _, __ = axs[0].pie(sorted_user_inputs, autopct="%1.1f%%", pctdistance=0.7, textprops={'size': 'large'}, startangle=90, colors = colors, wedgeprops=dict(width=0.7))

# Add the text labels with custom positioning, connecting lines and text borders
bbox_props = dict(boxstyle='square,pad=0.3', fc='w', ec='k', lw=0.8)
kw = dict(arrowprops=dict(arrowstyle='-'),
          bbox=bbox_props, zorder=0, va='center')

# Use the for loop to define the positioning for each element
for i, s in enumerate(sector):
    angle = (s.theta2 - s.theta1)/2. + s.theta1
    y = np.sin(np.deg2rad(angle))
    x = np.cos(np.deg2rad(angle))
    horizontalalignment = {-1: 'right', 1: 'left'}[int(np.sign(x))]
    connectionstyle = f'angle,angleA=0,angleB={angle}'
    kw['arrowprops'].update({'connectionstyle': connectionstyle})
    axs[0].annotate(sorted_items[i], xy=(x, y), fontsize=14, xytext=(1.2 * np.sign(x), 1.3 * y), ha=horizontalalignment, **kw)

axs[0].set_title('Your CPI Component Weights', fontsize=28, fontweight='bold', pad=65)
# Plot the bar chart with custom elements and add the chart title
xlabels  = ['General Household', 'You']
axs[1].bar(xlabels, CPI_data, label='Consumer Price Index', color = ['lightgray','tab:blue'], width=0.5)
axs[1].tick_params(axis='x', which='both', pad =20, bottom=False, labelsize=20)
axs[1].set_yticks([])
axs[1].spines['top'].set_visible(False)
axs[1].spines['bottom'].set_visible(True)
axs[1].spines['right'].set_visible(False)
axs[1].spines['left'].set_visible(False)
axs[1].set_ylim(60, 150)
axs[1].set_title('CPI Benchmark Comparison', fontsize=28, fontweight='bold', pad=0)

# Add the value labels for the bar chart
for i in range(0, 2):
    label_text = f'{CPI_data[i]:.1f}'
    label_x = xlabels[i]
    label_y = CPI_data[i] - 2
    text_obj = axs[1].text(label_x, label_y, label_text, ha='center', va='top', fontsize=14, color='black')
    text_obj.set_weight('bold')

# Define a function to specify the text description for the percentage difference of the CPI comparison
def comparison(a,b):
    per_diff = abs((a - b) / b) * 100
    if a > b:
        return f'Your computed CPI is greater than the general household benchmark by {per_diff:.1f}%'
    elif b > a:
        return f'Your computed CPI is less than the general household benchmark by {per_diff:.1f}%'
    else:
        return f'Your computed CPI is the same as the general household benchmark'

result = comparison(CPI_user,CPI_2023)

# Create the fig text box to include the text information into the chart
label_text = result
label_x = 0.6
label_y = 0.8
plt.figtext(label_x, label_y, label_text, ha='left', va='center', fontsize=16, fontfamily='Arial', fontweight='bold', color='black', in_layout=True, bbox=dict(facecolor='white', edgecolor='black', boxstyle='square'))

# Adjust the horizontal space padding between the two charts
plt.subplots_adjust(top=0.9)
plt.subplots_adjust(wspace=0.6)

# Plot the charts
plt.show()