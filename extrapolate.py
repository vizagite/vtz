import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from scipy.optimize import OptimizeWarning
import warnings

df = pd.read_csv('final_output.csv')

print(df.head())

df = df.loc[df.groupby(['Year', 'Month'])['Pax'].idxmax()]

df['Month_Num'] = pd.to_datetime(df['Month'] + df['Year'].astype(str), format='%b%Y')

# Filter out data after February 2020 - covid lockdowns outliers (for fitting only)
df_fit = df[(df['Year'] < 2020) | ((df['Year'] == 2020) & (df['Month_Num'] <= '2020-02-01'))]

start_date = pd.to_datetime('1981-01-01')
df['Time_Index'] = (df['Month_Num'] - start_date) / pd.Timedelta(days=30.4375)  # Approx 30.4375 days per month
df_fit.loc[:, 'Time_Index'] = (df_fit['Month_Num'] - start_date) / pd.Timedelta(days=30.4375)

# Prepare the data for regression models (Time_Index as the independent variable)
X = df_fit['Time_Index'].values  # Independent variable (continuous time index)
y = df_fit['Pax'].values  # Dependent variable (Pax)

def exponential_decay(t, a, b):
    return a * np.exp(b * t)

params_exp, _ = curve_fit(exponential_decay, X, y, p0=(max(y), -0.01))  # Initial guess: a=max(y), b=-0.01
y_pred_exp = exponential_decay(X, *params_exp)

y_pred_exp = np.round(y_pred_exp).astype(int)

def linear_fit(t, a, b):
    return a * t + b

params_lin, _ = curve_fit(linear_fit, X, y, p0=(1, max(y)))  # Initial guess: slope=1, intercept=max(y))
y_pred_lin = linear_fit(X, *params_lin)

current_time = (pd.to_datetime('today') - start_date) / pd.Timedelta(days=30.4375)  # Get current time index
time_range = np.arange(0, current_time + 1, 1)  # Time range from 0 (1981 Jan) to the current time index

extrapolated_data = []
extrapolated_times = []  # Store the time indices for extrapolated data

for time in time_range:
    predicted_pax_exp = exponential_decay(time, *params_exp)  # Exponential model prediction
    predicted_pax_exp = np.round(predicted_pax_exp).astype(int)  # Round the prediction to integer
    
    if predicted_pax_exp < 0:
        break
    
    predicted_pax_lin = linear_fit(time, *params_lin)  # Linear model prediction
    predicted_pax_lin = np.round(predicted_pax_lin).astype(int)  # Round the prediction to integer
    
    if predicted_pax_lin < 0:
        predicted_pax_lin = None  # Do not plot or store this linear prediction
    
    if predicted_pax_lin is not None and predicted_pax_lin > 400000:
        break
    
    time_diff = pd.Timedelta(days=time * 30.4375)  # Convert the time index back to days
    month_date = start_date + time_diff
    current_year = month_date.year
    current_month = month_date.month
    
    extrapolated_data.append([current_year, month_date.strftime('%b'), predicted_pax_exp, predicted_pax_lin])
    extrapolated_times.append(time)  # Store the time index


future_time = time_range[-1] + 1  # Start from the last time point in the range
while True:
    predicted_pax_lin = linear_fit(future_time, *params_lin)  # Linear model prediction
    predicted_pax_lin = np.round(predicted_pax_lin).astype(int)  # Round the prediction to integer
    
    if predicted_pax_lin >= 500000:
        break
    
    time_diff = pd.Timedelta(days=future_time * 30.4375)  # Convert the time index back to days
    month_date = start_date + time_diff
    current_year = month_date.year
    current_month = month_date.month
    
    extrapolated_data.append([current_year, month_date.strftime('%b'), None, predicted_pax_lin])  # None for exponential
    extrapolated_times.append(future_time)  # Store the time index
    future_time += 1  # Increment to the next time point

extrapolated_df = pd.DataFrame(extrapolated_data, columns=['Year', 'Month', 'Pax_Extrapolated_Exp', 'Pax_Extrapolated_Lin'])

print(extrapolated_df)

original_times_aligned = [start_date + pd.Timedelta(days=t * 30.4375) for t in df['Time_Index'].values]

plt.figure(figsize=(10, 6))

plt.scatter(original_times_aligned, df['Pax'], color='blue', label='Original Data')

plt.plot(original_times_aligned[:len(df_fit)], y_pred_exp, color='red', label='Exponential Decay Fit')

plt.plot(original_times_aligned[:len(df_fit)], y_pred_lin, color='green', label='Linear Fit')

extrapolated_time = [start_date + pd.Timedelta(days=t * 30.4375) for t in extrapolated_times]

plt.scatter(extrapolated_time, extrapolated_df['Pax_Extrapolated_Exp'], color='orange', label='Extrapolated Exp. Data', marker='o', s=10, linewidths=0.01)

mask_lin = extrapolated_df['Pax_Extrapolated_Lin'].notna()
plt.scatter(np.array(extrapolated_time)[mask_lin], np.array(extrapolated_df['Pax_Extrapolated_Lin'])[mask_lin], 
            color='purple', label='Extrapolated Lin. Data', marker='o', s=20, linewidths=0.5)

xticks = pd.date_range(start='1981-01-01', end='2042-01-01', freq='5AS')  # Generate ticks for every 5 years
plt.xticks(xticks, labels=xticks.year)

plt.xlabel('Year')
plt.ylabel('Pax')
plt.title('Exponential and Linear Decay Fitting and Extrapolation')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()
# extrapolated_df.to_csv('extrapolated_output.csv', index=False)
