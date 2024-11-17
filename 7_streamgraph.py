import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('final_output.csv')
df = df.drop(df.columns[-1], axis=1)  # Drop the last column ('PaxLastyr')

df['MonthNum'] = pd.to_datetime(df['Month'], format='%b').dt.month
df['TimeIndex'] = (df['Year'] - df['Year'].min()) * 12 + df['MonthNum']

grouped = df.groupby(['Year', 'MonthNum'])

x = np.arange(len(df['TimeIndex'].unique()))
y_positive = []  # To store positive (larger) values
y_negative = []  # To store negative (smaller) values

for _, group in grouped:
    pax_values = group['Pax'].values
    if len(pax_values) == 2:  # If there are two values for the same Year-Month
        pax_larger = max(pax_values)
        pax_smaller = min(pax_values)
        
        y_positive.append(pax_larger)
        y_negative.append(-pax_smaller)  # Plot the smaller value on the negative side
    else:
        y_positive.append(pax_values[0])
        y_negative.append(0)  # No smaller value, so append 0 for negative side

def moving_average(y, window_size=3):
    return np.convolve(y, np.ones(window_size) / window_size, mode='same')

window_size = 3  # Set a smaller window size to capture more of the variations (ridges)
y_positive_smoothed = moving_average(y_positive, window_size)
y_negative_smoothed = moving_average(y_negative, window_size)

y_positive_smoothed[:2] = y_positive[:2]
y_positive_smoothed[-2:] = y_positive[-2:]

y_negative_smoothed[:2] = y_negative[:2]
y_negative_smoothed[-2:] = y_negative[-2:]

fig, ax = plt.subplots(figsize=(10, 7))

# Plot the streamgraph: positive side (domestic)
positive_plot = ax.stackplot(x, y_positive_smoothed, baseline="zero", color="#2B8CBE", alpha=0.7)
# Plot the mirrored streamgraph: negative side (international)
negative_plot = ax.stackplot(x, y_negative_smoothed, baseline="zero", color="#FF6347", alpha=0.7)

ax.axhline(0, color="black", ls="--")

years = np.unique(df['Year'])

year_ticks = years[years >= 2007]
xticks = []
for year in year_ticks:
    january_time_index = (year - df['Year'].min()) * 12 + 1  # January is Month 1
    if january_time_index in df['TimeIndex'].values:
        xticks.append(january_time_index-3)
ax.set_xticks(xticks)

ax.set_xticklabels([str(year) for year in year_ticks])

yticks = np.arange(-150000, 300001, 50000)  # Positive and negative ticks
ax.set_yticks(yticks)

yticklabels = [f'{abs(i)//1000}k' if i != 0 else '0' for i in yticks]
ax.set_yticklabels(yticklabels)

ax.set_ylim(-50000, 300000)

ax.set_title("VTZ Airport Passengers: Domestic vs. International", fontsize=16)
ax.set_xlabel("Year", fontsize=12)

ax.legend([positive_plot[0], negative_plot[0]], ['dom. #pax', 'int. #pax'], loc="upper left", fontsize=12)

plt.tight_layout()
plt.show()
