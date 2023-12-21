#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2023-12-20 21:56:29 trottar"
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
        
energy_settings = ['Q5p5W3p02right_highe','Q5p5W3p02left_highe','Q5p5W3p02center_highe', \
                   'Q4p4W2p74right_highe','Q4p4W2p74left_highe','Q4p4W2p74center_highe', \
                   'Q3p0W3p14right_highe','Q3p0W3p14left_highe','Q3p0W3p14center_highe', \
                   'Q3p0W2p32right_highe','Q3p0W2p32left_highe','Q3p0W2p32center_highe', \
                   'Q2p1W2p95right_highe','Q2p1W2p95left_highe','Q2p1W2p95center_highe']
    
# Assuming 'efficiency_data' is a DataFrame with a column named 'Run_Number'
efficiency_dict = {}
for i,setting in enumerate(energy_settings):
    efficiency_dict[setting] = efficiency_data[efficiency_data['Run_Number'].isin(run_numbers_dict[setting])]

    print("{}: {}".format(setting,efficiency_dict[setting]['Run_Number']))

################################################################################################################################################

# Define the linear fit function
def linear_fit(x, m, b):
    return m * x + b

# Error weighted fit of data
def fit_data(plt, x_name, y_name):

    color = ['blue','red','purple','orange','pink','yellow']

    x_lst = []
    y_lst = []
    yerr_lst = []
    
    for i,setting in enumerate(energy_settings):
        print("Plotting {}: {} vs {}...".format(setting, x_name, y_name))

        # Make x data
        efficiency_xdata = efficiency_dict[setting][x_name].copy()
        
        # Concatenate x data from different sources
        x_data = efficiency_xdata
        x_lst.append(x_data)

        # Make y data
        efficiency_ydata = efficiency_dict[setting][y_name].copy()

        # Concatenate y data from different sources
        y_data = efficiency_ydata
        y_lst.append(y_data)

        if "Hodo" not in y_name:
            
            y_error_name = y_name+"_ERROR"

            # Make y error
            efficiency_yerror = efficiency_dict[setting][y_error_name].copy()
            yerr_lst.append(efficiency_yerror)

            # Concatenate y error from different sources
            y_error = efficiency_yerror
            y_error = y_error + 1e-10 # Prevent divide by zero
            yerr_lst.append(y_error)

            plt.scatter(x_data, y_data,color=color[int(i/3)],zorder=4,label='10p6')
            plt.errorbar(x_data, y_data, yerr=y_error, label=None,color='black',linestyle='None',zorder=3)
        else:
            plt.scatter(x_data, y_data,color='blue',zorder=4,label='10p6')
    
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
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_3/4_Trigger_Rate", "SHMS_Pion_ALL_TRACK_EFF")
plt.ylabel('SHMS_Pion_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_3/4_Trigger_Rate", "SHMS_Aero_ALL_Pion_Eff")
plt.ylabel('SHMS_Aero_ALL_Pion_Eff', fontsize=12)
plt.xlabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_3/4_Trigger_Rate", "SHMS_Hodo_3_of_4_EFF")
plt.ylabel('SHMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

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
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "SHMS_Pion_ALL_TRACK_EFF")
plt.ylabel('SHMS_Pion_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('SHMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "SHMS_Aero_ALL_Pion_Eff")
plt.ylabel('SHMS_Aero_ALL_Pion_Eff', fontsize=12)
plt.xlabel('SHMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "SHMS_Hodo_3_of_4_EFF")
plt.ylabel('SHMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('SHMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

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
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "HMS_Elec_ALL_TRACK_EFF")
plt.ylabel('HMS_Elec_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "HMS_Cer_ALL_Elec_Eff")
plt.ylabel('HMS_Cer_ALL_Elec_Eff', fontsize=12)
plt.xlabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "HMS_Hodo_3_of_4_EFF")
plt.ylabel('HMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

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
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_Hodoscope_S1X_Rate", "HMS_Elec_ALL_TRACK_EFF")
plt.ylabel('HMS_Elec_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('HMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_Hodoscope_S1X_Rate", "HMS_Cer_ALL_Elec_Eff")
plt.ylabel('HMS_Cer_ALL_Elec_Eff', fontsize=12)
plt.xlabel('HMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_Hodoscope_S1X_Rate", "HMS_Hodo_3_of_4_EFF")
plt.ylabel('HMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('HMS S1X HODO Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

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
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_dict_4p9["COIN_Trigger_Rate"],efficiency_dict_4p9["COIN_CPULT"],color='purple',zorder=4,label='4p9')
plt.scatter(efficiency_dict_6p2["COIN_Trigger_Rate"],efficiency_dict_6p2["COIN_CPULT"],color='orange',zorder=4,label='6p2')
plt.scatter(efficiency_dict_8p2["COIN_Trigger_Rate"],efficiency_dict_8p2["COIN_CPULT"],color='pink',zorder=4,label='8p2')

plt.ylabel('COIN CPULT', fontsize=12)
plt.xlabel('COIN Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(223)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
plt.xlabel('COIN Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
plt.xlabel('COIN Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

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
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('SHMS_Pion_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('SHMS_Aero_ALL_Pion_Eff', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('SHMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])   
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/SHMS_3-4_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('HMS_Elec_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('HMS_Cer_ALL_Elec_Eff', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('HMS_Hodo_3_of_4_EFF', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])   
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/HMS_EL-REAL_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('SHMS 3/4 Trigger Rate [kHz]', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('HMS EL-REAL Trigger Rate [kHz]', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

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
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "HMS_Cal_ALL_Elec_Eff")
plt.ylabel('HMS_Cal_ALL_Elec_Eff', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(223)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "HMS_Cer_ALL_Elec_Eff")
plt.ylabel('HMS_Cer_ALL_Elec_Eff', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

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
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "SHMS_Aero_ALL_Pion_Eff")
plt.ylabel('SHMS_Aero_ALL_Pion_Eff', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

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
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(122)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "SHMS_Pion_ALL_TRACK_EFF")
plt.ylabel('SHMS_Pion_ALL_TRACK_EFF', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/Track_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.ylabel('BOIL_Eff', fontsize=12)
plt.xlabel('Run Number', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(223)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "Non_Scaler_EDTM_Live_Time")
plt.ylabel('EDTM', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "BOIL_Eff")
plt.ylabel('Boiling Correction', fontsize=12)
plt.xlabel('Current', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_dict["Run_Number"])),int(max(efficiency_dict["Run_Number"]))), fontsize=12)

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/EDTM_%s_run.png' % (ROOTPrefix.replace("replay_","")))

#plt.show()
