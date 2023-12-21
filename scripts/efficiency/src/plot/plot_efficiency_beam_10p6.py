#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2023-12-20 21:02:53 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from csv import DictReader
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys, os

################################################################################################################################################
'''
User Inputs
'''
ROOTPrefix = sys.argv[1]
runType = sys.argv[2]
timestmp = sys.argv[3]

################################################################################################################################################
'''
ltsep package import and pathing definitions
'''

# Import package for cuts
import ltsep as lt 

p=lt.SetPath(os.path.realpath(__file__))

# Add this to all files for more dynamic pathing
USER=p.getPath("USER") # Grab user info for file finding
HOST=p.getPath("HOST")
REPLAYPATH=p.getPath("REPLAYPATH")
UTILPATH=p.getPath("UTILPATH")
ANATYPE=p.getPath("ANATYPE")
SCRIPTPATH=p.getPath("SCRIPTPATH")

################################################################################################################################################

inp_f = UTILPATH+"/scripts/efficiency/OUTPUTS/%s_%s_efficiency_data_%s.csv"  % (ROOTPrefix.replace("replay_",""),runType,timestmp)

# Converts csv data to dataframe
try:
    efficiency_data = pd.read_csv(inp_f)
except IOError:
    print("Error: %s does not appear to exist." % inp_f)
print(efficiency_data.keys())

# Including dummy
#efficiency_data = efficiency_data[(efficiency_data['Run_Number'] >= 4865)  & (efficiency_data['Run_Number'] <= 5334)]

# Initialize an empty dictionary to store run numbers
run_numbers_dict = {}

# Loop through all files in the specified directory
for filename in os.listdir(REPLAYPATH + '/UTIL_BATCH/InputRunLists/KaonLT_2018_2019/'):
    # Construct the full file path
    file_path = os.path.join(REPLAYPATH + '/UTIL_BATCH/InputRunLists/KaonLT_2018_2019/', filename)

    # Check if the path is a file (not a directory)
    if os.path.isfile(file_path):
        # Open each file and read run numbers, ignoring non-numeric lines
        with open(file_path, 'r') as file:
            # Assuming each line in the file contains a single Run_Number
            run_numbers = [int(line.strip()) for line in file if line.strip().isdigit()]

        # Use the filename as the key and store run numbers in the dictionary
        run_numbers_dict[filename] = run_numbers

print(run_numbers_dict)
        
# Update 'your_file.txt' with the actual file path
with open(REPLAYPATH+'/UTIL_BATCH/InputRunLists/KaonLT_2018_2019/Prod_Autumn18', 'r') as file:
    # Assuming each line in the file contains a single Run_Number
    run_numbers = [int(line.strip()) for line in file]

energy_settings = ['Q5p5W3p02right_highe','Q5p5W3p02left_highe','Q5p5W3p02center_highe', \
                   'Q4p4W2p74right_highe','Q4p4W2p74left_highe','Q4p4W2p74center_highe', \
                   'Q3p0W3p14right_highe','Q3p0W3p14left_highe','Q3p0W3p14center_highe', \
                   'Q3p0W2p32right_highe','Q3p0W2p32left_highe','Q3p0W2p32center_highe', \
                   'Q2p1W2p95right_highe','Q2p1W2p95left_highe','Q2p1W2p95center_highe']
    
# Assuming 'efficiency_data' is a DataFrame with a column named 'Run_Number'
efficiency_data = {}
for setting in energy_settings:
    efficiency_data[setting] = efficiency_data[efficiency_data['Run_Number'].isin(run_numbers)]

################################################################################################################################################

# Define the linear fit function
def linear_fit(x, m, b):
    return m * x + b

# Error weighted fit of data
def fit_data(plt, x_name, y_name):

    color = ['blue','red','purple','orange','pink']

    x_lst = []
    y_lst = []
    yerr_lst = []
    
    for setting in energy_settings:    
        print("Plotting {}: {} vs {}...".format(setting, x_name, y_name))

        y_error_name = y_name+"_ERROR"

        # Make x data
        efficiency_xdata = efficiency_data[setting][x_name].copy()
        
        # Concatenate x data from different sources
        x_data = efficiency_xdata
        x_lst.append(x_data)

        # Make y data
        efficiency_ydata = efficiency_data[setting][y_name].copy()

        # Concatenate y data from different sources
        y_data = efficiency_ydata
        y_lst.append(y_data)

        if "hodo" not in y_name:
            # Make y error
            efficiency_yerror = efficiency_data[setting][y_error_name].copy()
            yerr_lst.append(efficiency_yerror)

            # Concatenate y error from different sources
            y_error = efficiency_yerror
            y_error = y_error + 1e-10 # Prevent divide by zero
            yerr_lst.append(y_error)

            plt.scatter(x_data, y_data,color='blue',zorder=4,label='10p6')
            plt.errorbar(x_data, y_data, yerr=y_error, label=None,color='black',linestyle='None',zorder=3)
        else:
            plt.scatter(x_data, y_data,color='blue',zorder=4,label='10p6')

    x_data = pd.concat(x_lst, ignore_index=True)
    y_data = pd.concat(y_lst, ignore_indey=True)
    y_error = pd.concat(yerr_lst, ignore_indey=True)
            
    if "hodo" not in y_name:
        # Perform the error-weighted linear fit
        params, covariance = curve_fit(linear_fit, x_data, y_data, sigma=y_error, absolute_sigma=True)

        # Extract the slope and intercept from the fit
        slope = params[0]
        intercept = params[1]

        # Calculate the standard deviations of the parameters
        slope_error = np.sqrt(covariance[0, 0])
        intercept_error = np.sqrt(covariance[1, 1])

        # Calculate the fitted values and residuals
        y_fit = linear_fit(x_data, slope, intercept)
        residuals = y_data - y_fit

        # Calculate the chi-square value
        chi_square = np.sum((residuals / y_error)**2)

        # Generate x values for the error band
        x_fit = np.linspace(min(x_data), max(x_data), 100)

        # Calculate y values for the error band
        y_fit = linear_fit(x_fit, slope, intercept)

        # Calculate upper and lower bounds for the error band
        y_upper = linear_fit(x_fit, slope + slope_error, intercept + intercept_error)
        y_lower = linear_fit(x_fit, slope - slope_error, intercept - intercept_error)

        # Plot the data and the fitted line
        plt.plot(x_fit, y_fit, label='m={0:.2e}±{1:.2e}\nb={2:.2e}±{3:.2e}\nchisq={4:.2e}'.format(slope, slope_error, intercept, intercept_error, chi_square), color='limegreen', linewidth=2, zorder=6)
        plt.fill_between(x_fit, y_lower, y_upper, color='lightgreen', alpha=0.4,zorder=5)
    
    # Annotate the plot with the slope and intercept
    plt.legend(loc="lower right", markerscale=0.7, scatterpoints=1, fontsize=10)

################################################################################################################################################

plt.figure(figsize=(12,8))

plt.subplot(221)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_3/4_Trigger_Rate", "Non_Scaler_EDTM_Live_Time")
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_3/4_Trigger_Rate", "SHMS_Pion_ALL_TRACK_EFF")
plt.ylabel('SHMS_Pion_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_3/4_Trigger_Rate", "SHMS_Aero_ALL_Pion_Eff")
plt.ylabel('SHMS_Aero_ALL_Pion_Eff', fontsize=12)
plt.xlabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_3/4_Trigger_Rate", "SHMS_Hodo_3_of_4_EFF")
plt.ylabel('SHMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])   
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/SHMS_3-4_%s.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "Non_Scaler_EDTM_Live_Time")
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('SHMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "SHMS_Pion_ALL_TRACK_EFF")
plt.ylabel('SHMS_Pion_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('SHMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "SHMS_Aero_ALL_Pion_Eff")
plt.ylabel('SHMS_Aero_ALL_Pion_Eff', fontsize=12)
plt.xlabel('SHMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "SHMS_Hodo_3_of_4_EFF")
plt.ylabel('SHMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('SHMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/SHMS_S1X_%s.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "Non_Scaler_EDTM_Live_Time")
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "HMS_Elec_ALL_TRACK_EFF")
plt.ylabel('HMS_Elec_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "HMS_Cer_ALL_Elec_Eff")
plt.ylabel('HMS_Cer_ALL_Elec_Eff', fontsize=12)
plt.xlabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "HMS_Hodo_3_of_4_EFF")
plt.ylabel('HMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])   
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/HMS_EL-REAL_%s.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_Hodoscope_S1X_Rate", "Non_Scaler_EDTM_Live_Time")
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('HMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_Hodoscope_S1X_Rate", "HMS_Elec_ALL_TRACK_EFF")
plt.ylabel('HMS_Elec_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('HMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_Hodoscope_S1X_Rate", "HMS_Cer_ALL_Elec_Eff")
plt.ylabel('HMS_Cer_ALL_Elec_Eff', fontsize=12)
plt.xlabel('HMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_Hodoscope_S1X_Rate", "HMS_Hodo_3_of_4_EFF")
plt.ylabel('HMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('HMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/HMS_S1X_%s.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))
'''
plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('COIN Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["COIN_Trigger_Rate"],efficiency_data_4p9["COIN_CPULT"],color='purple',zorder=4,label='4p9')
plt.scatter(efficiency_data_6p2["COIN_Trigger_Rate"],efficiency_data_6p2["COIN_CPULT"],color='orange',zorder=4,label='6p2')
plt.scatter(efficiency_data_8p2["COIN_Trigger_Rate"],efficiency_data_8p2["COIN_CPULT"],color='pink',zorder=4,label='8p2')

plt.ylabel('COIN CPULT', fontsize=12)
plt.xlabel('COIN Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(223)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
plt.xlabel('COIN Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
plt.xlabel('COIN Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/COIN_%s.png' % (ROOTPrefix.replace("replay_","")))
'''

plt.figure(figsize=(12,8))

plt.subplot(221)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('SHMS_Pion_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('SHMS_Aero_ALL_Pion_Eff', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('SHMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])   
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/SHMS_3-4_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('HMS_Elec_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('HMS_Cer_ALL_Elec_Eff', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('HMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])   
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/HMS_EL-REAL_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/COIN_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "HMS_Hodo_3_of_4_EFF")
plt.ylabel('HMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "HMS_Cal_ALL_Elec_Eff")
plt.ylabel('HMS_Cal_ALL_Elec_Eff', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(223)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "HMS_Cer_ALL_Elec_Eff")
plt.ylabel('HMS_Cer_ALL_Elec_Eff', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/HMSDet_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "SHMS_Hodo_3_of_4_EFF")
plt.ylabel('SHMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "SHMS_Aero_ALL_Pion_Eff")
plt.ylabel('SHMS_Aero_ALL_Pion_Eff', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/SHMSDet_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(121)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "HMS_Elec_ALL_TRACK_EFF")
plt.ylabel('HMS_Elec_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(122)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "SHMS_Pion_ALL_TRACK_EFF")
plt.ylabel('SHMS_Pion_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/Track_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('BOIL_Eff', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(223)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "Non_Scaler_EDTM_Live_Time")
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "BOIL_Eff")
plt.ylabel('Boiling Correction', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/EDTM_%s_run.png' % (ROOTPrefix.replace("replay_","")))

#plt.show()
