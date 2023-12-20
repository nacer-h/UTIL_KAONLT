#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2023-12-19 23:26:18 trottar"
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
efficiency_data_4p9 = efficiency_data[(efficiency_data['Run_Number'] >= 6885)  & (efficiency_data['Run_Number'] <= 7045)]

################################################################################################################################################

# Define the linear fit function
def linear_fit(x, m, b):
    return m * x + b

# Error weighted fit of data
def fit_data(plt, x_name, y_name):

    print("Plotting {} vs {}...".format(x_name, y_name))
    
    y_error_name = y_name+"_ERROR"
    
    # Make x data
    efficiency_xdata_4p9 = efficiency_data_4p9[x_name].copy()

    # Concatenate x data from different sources
    x_data = efficiency_xdata_4p9

    # Concatenate y data from different sources
    y_data = efficiency_ydata_4p9

    # Concatenate y error from different sources
    y_error = efficiency_error_4p9
    y_error = y_error + 1e-10 # Prevent divide by zero
    
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
    plt.errorbar(x_data, y_data, yerr=y_error, label=None,color='black',linestyle='None',zorder=3)
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
plt.scatter(efficiency_data_4p9["SHMS_3/4_Trigger_Rate"],efficiency_data_4p9["Non_Scaler_EDTM_Live_Time"],color='blue',zorder=4,label='4p9')

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_3/4_Trigger_Rate", "SHMS_Pion_ALL_TRACK_EFF")
plt.scatter(efficiency_data_4p9["SHMS_3/4_Trigger_Rate"],efficiency_data_4p9["SHMS_Pion_ALL_TRACK_EFF"],color='blue',zorder=4,label='4p9')

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_3/4_Trigger_Rate", "SHMS_Aero_ALL_Pion_Eff")
plt.scatter(efficiency_data_4p9["SHMS_3/4_Trigger_Rate"],efficiency_data_4p9["SHMS_Aero_ALL_Pion_Eff"],color='blue',zorder=4,label='4p9')

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
#fit_data(plt, "SHMS_3/4_Trigger_Rate", "SHMS_Hodo_3_of_4_EFF")
plt.scatter(efficiency_data_4p9["SHMS_3/4_Trigger_Rate"],efficiency_data_4p9["SHMS_Hodo_3_of_4_EFF"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])   
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/SHMS_3-4_%s.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "Non_Scaler_EDTM_Live_Time")
plt.scatter(efficiency_data_4p9["SHMS_Hodoscope_S1X_Rate"],efficiency_data_4p9["Non_Scaler_EDTM_Live_Time"],color='blue',zorder=4,label='4p9')

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "SHMS_Pion_ALL_TRACK_EFF")
plt.scatter(efficiency_data_4p9["SHMS_Hodoscope_S1X_Rate"],efficiency_data_4p9["SHMS_Pion_ALL_TRACK_EFF"],color='blue',zorder=4,label='4p9')

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "SHMS_Aero_ALL_Pion_Eff")
plt.scatter(efficiency_data_4p9["SHMS_Hodoscope_S1X_Rate"],efficiency_data_4p9["SHMS_Aero_ALL_Pion_Eff"],color='blue',zorder=4,label='4p9')

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
#fit_data(plt, "SHMS_Hodoscope_S1X_Rate", "SHMS_Hodo_3_of_4_EFF")
plt.scatter(efficiency_data_4p9["SHMS_Hodoscope_S1X_Rate"],efficiency_data_4p9["SHMS_Hodo_3_of_4_EFF"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/SHMS_S1X_%s.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "Non_Scaler_EDTM_Live_Time")
plt.scatter(efficiency_data_4p9["HMS_EL-REAL_Trigger_Rate"],efficiency_data_4p9["Non_Scaler_EDTM_Live_Time"],color='blue',zorder=4,label='4p9')

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "HMS_Elec_ALL_TRACK_EFF")
plt.scatter(efficiency_data_4p9["HMS_EL-REAL_Trigger_Rate"],efficiency_data_4p9["HMS_Elec_ALL_TRACK_EFF"],color='blue',zorder=4,label='4p9')

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "HMS_Cer_ALL_Elec_Eff")
plt.scatter(efficiency_data_4p9["HMS_EL-REAL_Trigger_Rate"],efficiency_data_4p9["HMS_Cer_ALL_Elec_Eff"],color='blue',zorder=4,label='4p9')

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
#fit_data(plt, "HMS_EL-REAL_Trigger_Rate", "HMS_Hodo_3_of_4_EFF")
plt.scatter(efficiency_data_4p9["HMS_EL-REAL_Trigger_Rate"],efficiency_data_4p9["HMS_Hodo_3_of_4_EFF"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])   
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/HMS_EL-REAL_%s.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_Hodoscope_S1X_Rate", "Non_Scaler_EDTM_Live_Time")
plt.scatter(efficiency_data_4p9["HMS_Hodoscope_S1X_Rate"],efficiency_data_4p9["Non_Scaler_EDTM_Live_Time"],color='blue',zorder=4,label='4p9')

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_Hodoscope_S1X_Rate", "HMS_Elec_ALL_TRACK_EFF")
plt.scatter(efficiency_data_4p9["HMS_Hodoscope_S1X_Rate"],efficiency_data_4p9["HMS_Elec_ALL_TRACK_EFF"],color='blue',zorder=4,label='4p9')

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "HMS_Hodoscope_S1X_Rate", "HMS_Cer_ALL_Elec_Eff")
plt.scatter(efficiency_data_4p9["HMS_Hodoscope_S1X_Rate"],efficiency_data_4p9["HMS_Cer_ALL_Elec_Eff"],color='blue',zorder=4,label='4p9')

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
#fit_data(plt, "HMS_Hodoscope_S1X_Rate", "HMS_Hodo_3_of_4_EFF")
plt.scatter(efficiency_data_4p9["HMS_Hodoscope_S1X_Rate"],efficiency_data_4p9["HMS_Hodo_3_of_4_EFF"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/HMS_S1X_%s.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))
'''
plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["COIN_Trigger_Rate"],efficiency_data_4p9["Non_Scaler_EDTM_Live_Time"],color='blue',zorder=4,label='4p9')

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["COIN_Trigger_Rate"],efficiency_data_4p9["COIN_CPULT"],color='blue',zorder=4,label='4p9')

plt.ylabel('COIN CPULT', fontsize=12)
plt.xlabel('COIN Trigger Rate [kHz]', fontsize=12)
#plt.title('%s-%s' % (int(min(efficiency_data["Run_Number"])),int(max(efficiency_data["Run_Number"]))), fontsize=12)

plt.subplot(223)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["COIN_Trigger_Rate"],efficiency_data_4p9["SHMS_3/4_Trigger_Rate"],color='blue',zorder=4,label='4p9')

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["COIN_Trigger_Rate"],efficiency_data_4p9["HMS_EL-REAL_Trigger_Rate"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/COIN_%s.png' % (ROOTPrefix.replace("replay_","")))
'''

plt.figure(figsize=(12,8))

plt.subplot(221)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["Non_Scaler_EDTM_Live_Time"],color='blue',zorder=4,label='4p9')

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["SHMS_Pion_ALL_TRACK_EFF"],color='blue',zorder=4,label='4p9')

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["SHMS_Aero_ALL_Pion_Eff"],color='blue',zorder=4,label='4p9')

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["SHMS_Hodo_3_of_4_EFF"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])   
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/SHMS_3-4_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["Non_Scaler_EDTM_Live_Time"],color='blue',zorder=4,label='4p9')

plt.subplot(222)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["HMS_Elec_ALL_TRACK_EFF"],color='blue',zorder=4,label='4p9')

plt.subplot(223)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["HMS_Cer_ALL_Elec_Eff"],color='blue',zorder=4,label='4p9')

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["HMS_Hodo_3_of_4_EFF"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])   
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/HMS_EL-REAL_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)    
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["Non_Scaler_EDTM_Live_Time"],color='blue',zorder=4,label='4p9')

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["COIN_CPULT"],color='blue',zorder=4,label='4p9')

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["HMS_EL-REAL_Trigger_Rate"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/COIN_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
#fit_data(plt, "BCM1_Beam_Cut_Current", "HMS_Hodo_3_of_4_EFF")
plt.scatter(efficiency_data_4p9["BCM1_Beam_Cut_Current"],efficiency_data_4p9["HMS_Hodo_3_of_4_EFF"],color='blue',zorder=4,label='4p9')

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "HMS_Cal_ALL_Elec_Eff")
plt.scatter(efficiency_data_4p9["BCM1_Beam_Cut_Current"],efficiency_data_4p9["HMS_Cal_ALL_Elec_Eff"],color='blue',zorder=4,label='4p9')

plt.subplot(223)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "HMS_Cer_ALL_Elec_Eff")
plt.scatter(efficiency_data_4p9["BCM1_Beam_Cut_Current"],efficiency_data_4p9["HMS_Cer_ALL_Elec_Eff"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/HMSDet_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
#fit_data(plt, "BCM1_Beam_Cut_Current", "SHMS_Hodo_3_of_4_EFF")
plt.scatter(efficiency_data_4p9["BCM1_Beam_Cut_Current"],efficiency_data_4p9["SHMS_Hodo_3_of_4_EFF"],color='blue',zorder=4,label='4p9')

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "SHMS_Aero_ALL_Pion_Eff")
plt.scatter(efficiency_data_4p9["BCM1_Beam_Cut_Current"],efficiency_data_4p9["SHMS_Aero_ALL_Pion_Eff"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/SHMSDet_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(121)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "HMS_Elec_ALL_TRACK_EFF")
plt.scatter(efficiency_data_4p9["BCM1_Beam_Cut_Current"],efficiency_data_4p9["HMS_Elec_ALL_TRACK_EFF"],color='blue',zorder=4,label='4p9')

plt.subplot(122)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "SHMS_Pion_ALL_TRACK_EFF")
plt.scatter(efficiency_data_4p9["BCM1_Beam_Cut_Current"],efficiency_data_4p9["SHMS_Pion_ALL_TRACK_EFF"],color='blue',zorder=4,label='4p9')

plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/Track_%s_run.png' % (ROOTPrefix.replace("replay_","")))

plt.figure(figsize=(12,8))

plt.subplot(221)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["Non_Scaler_EDTM_Live_Time"],color='blue',zorder=4,label='4p9')

plt.subplot(222)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
plt.scatter(efficiency_data_4p9["Run_Number"],efficiency_data_4p9["BOIL_Eff"],color='blue',zorder=4,label='4p9')

plt.subplot(223)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "Non_Scaler_EDTM_Live_Time")
plt.scatter(efficiency_data_4p9["BCM1_Beam_Cut_Current"],efficiency_data_4p9["Non_Scaler_EDTM_Live_Time"],color='blue',zorder=4,label='4p9')

plt.subplot(224)
plt.grid(zorder=1)
#plt.xlim(0,100)
#plt.ylim(0.9,1.1)
fit_data(plt, "BCM1_Beam_Cut_Current", "BOIL_Eff")
plt.scatter(efficiency_data_4p9["BCM1_Beam_Cut_Current"],efficiency_data_4p9["BOIL_Eff"],color='blue',zorder=4,label='4p9')
plt.tight_layout(rect=[0,0.03,1,0.95])
plt.savefig(UTILPATH+'/scripts/efficiency/OUTPUTS/plots/EDTM_%s_run.png' % (ROOTPrefix.replace("replay_","")))

#plt.show()