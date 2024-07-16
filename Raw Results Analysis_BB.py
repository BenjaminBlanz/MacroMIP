#!/usr/bin/env python
# coding: utf-8

# code from Nike modified by Benjamin

#%% In[2]:

print('loading libs')

from scipy.io import loadmat
import numpy as np
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import os

#%%

# show the plots?
showPlots = False

#%% function to find the shape of a nested list as python is defficient
def shape(listOfLists):
    shape = []
    b = listOfLists
    while type(b) == list:
        shape.append(len(b))
        b = b[0]
    return shape

#%% sector aggregation function
def aggregateSectorNace62ToNace1(inArray):
    shape = list(inArray.shape)
    sectorDim = shape.index(len(sectors_nace_62))
    shape[sectorDim] = len(sectors_nace_1)
    aggArray = np.ones(shape)
    for t in range(len(time_steps)):
        for c in range(len(country_codes)):
            for s in range(len(sectors_nace_1)):
                matched_sector_idcs = [sectors_nace_62.index(sector) for sector in sectors_nace_62 if sector.startswith(sectors_nace_1[s])]
                if len(shape)==4:
                    for e in range(len(experiments)):
                        aggArray[t,e,c,s] = sum(inArray[t,e,c,matched_sector_idcs])
                else:
                    aggArray[t,c,s] = sum(inArray[t,c,matched_sector_idcs])
    return aggArray

#%% data description function
def describeData(data):
    for key in list(data.keys()):
        print(key)
        if(type(data[key]) != np.ndarray):
            print("   Is not a data array, ignoring.")
        else:
            x = data[key]
            print("   Is an array with shape: " + str(x.shape))
            dimensions = ''
            for j in range(0,(len(list(x.shape)))):
                if key[-5:] == "_mean" and j==1 and x.shape[j]==1:
                    dimensions = dimensions + "experiment mean" + ', '
                else:
                    dimensions = dimensions + list(dimensionLabels.keys())[dimensionLabelsLengths.index(x.shape[j])] + ', '
            dimensions = dimensions[:-2]
            print("   dimensions: " + dimensions)

#%% area of circle wedge
# use if you want the change in the piechart wedge radi to reflect the area change of the wedges
# decided against this as with linear radius scaling, we can add concentric circles behind the pie for scales

# def areaOfWedges(pieData, radius):
#     angles = 360 * pieData / sum(pieData)
#     areas = np.pi * radius**2 * angles/360
#     return areas, angles

# def radiusOfWedgeWithArea(area,angle):
#     return np.sqrt((area*360)/(np.pi * angle))

# def radiusOfRelChange(pieData, baseAreas, baseRadius, angles):
#     relChangedAreas = baseAreas * pieData
#     return radiusOfWedgeWithArea(relChangedAreas, angles)


# baseAreas, baseAngles = areaOfWedges(piedata,base_radius)
# relAdjArea = baseAreas[s] * (1+ scenarios_dif_rel[scenario_index][sector_thing][time_index,country_index,s]*10)
# relAdjRadius = np.sqrt((relAdjArea*360)/(np.pi * baseAngles[s]))

#%% Constants data labels
# List of country codes
country_codes = ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'FI', 'FR', 'HR',
                 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK']
country_codes_3 = ['AUT', 'BEL', 'BGR', 'CYP', 'CZE', 'DEU', 'DNK', 'EST', 'GRC', 'ESP', 'FIN', 'FRA', 'HRV',
                 'HUN', 'IRL', 'ITA', 'LTU', 'LUX', 'LVA', 'NLD', 'POL', 'PRT', 'ROU', 'SWE', 'SVN', 'SVK']
regions=['AT11', 'AT12', 'AT13', 'AT21', 'AT22', 'AT31', 'AT32', 'AT33', 'AT34', 'BE10', 'BE21', 'BE22', 'BE23',
         'BE24', 'BE25', 'BE31', 'BE32', 'BE33', 'BE34', 'BE35', 'BG31', 'BG32', 'BG33', 'BG34', 'BG41', 'BG42',
         'CY00', 'CZ01', 'CZ02', 'CZ03', 'CZ04', 'CZ05', 'CZ06', 'CZ07', 'CZ08', 'DE11', 'DE12', 'DE13', 'DE14',
         'DE21', 'DE22', 'DE23', 'DE24', 'DE25', 'DE26', 'DE27', 'DE30', 'DE40', 'DE50', 'DE60', 'DE71', 'DE72',
         'DE73', 'DE80', 'DE91', 'DE92', 'DE93', 'DE94', 'DEA1', 'DEA2', 'DEA3', 'DEA4', 'DEA5', 'DEB1', 'DEB2',
         'DEB3', 'DEC0', 'DED2', 'DED4', 'DED5', 'DEE0', 'DEF0', 'DEG0', 'DK01', 'DK02', 'DK03', 'DK04', 'DK05',
         'EE00', 'EL30', 'EL41', 'EL42', 'EL43', 'EL51', 'EL52', 'EL53', 'EL54', 'EL61', 'EL62', 'EL63', 'EL64',
         'EL65', 'ES11', 'ES12', 'ES13', 'ES21', 'ES22', 'ES23', 'ES24', 'ES30', 'ES41', 'ES42', 'ES43', 'ES51',
         'ES52', 'ES53', 'ES61', 'ES62', 'ES63', 'ES64', 'ES70', 'FI1B', 'FI1C', 'FI1D', 'FI19', 'FI20', 'FR10',
         'FRB0', 'FRC1', 'FRC2', 'FRD1', 'FRD2', 'FRE1', 'FRE2', 'FRF1', 'FRF2', 'FRF3', 'FRG0', 'FRH0', 'FRI1',
         'FRI2', 'FRI3', 'FRJ1', 'FRJ2', 'FRK1', 'FRK2', 'FRL0', 'FRM0', 'FRY1', 'FRY2', 'FRY3', 'FRY4', 'HR03',
         'HU11', 'HU12', 'HU21', 'HU22', 'HU23', 'HU31', 'HU32', 'HU33', 'IE04', 'IE05', 'IE06', 'ITC1', 'ITC2',
         'ITC3', 'ITC4', 'ITF1', 'ITF2', 'ITF3', 'ITF4', 'ITF5', 'ITF6', 'ITG1', 'ITG2', 'ITH1', 'ITH2', 'ITH3',
         'ITH4', 'ITH5', 'ITI1', 'ITI2', 'ITI3', 'ITI4', 'LT01', 'LT02', 'LU00', 'LV00', 'NL11', 'NL12', 'NL13',
         'NL21', 'NL22', 'NL23', 'NL31', 'NL32', 'NL33', 'NL34', 'NL41', 'NL42', 'PL21', 'PL22', 'PL41', 'PL42',
         'PL43', 'PL51', 'PL52', 'PL61', 'PL62', 'PL63', 'PL71', 'PL72', 'PL81', 'PL82', 'PL84', 'PL91', 'PL92',
         'PT11', 'PT15', 'PT16', 'PT17', 'PT18', 'PT20', 'PT30', 'RO11', 'RO12', 'RO21', 'RO22', 'RO31', 'RO32',
         'RO41', 'RO42', 'SE11', 'SE12', 'SE21', 'SE22', 'SE23', 'SE31', 'SE32', 'SE33', 'SI03', 'SI04', 'SK01',
         'SK02', 'SK03', 'SK04'];
danube_countries = ['DE', 'AT', 'CZ', 'HU', 'SK', 'SI', 'RO', 'BG', 'HR']
# List of NUTS-2 codes for the specified countries and German regions
danube_nuts_2 = [
    # Germany
    'DE11', 'DE13', 'DE14', 'DE21', 'DE22', 'DE23', 'DE24', 'DE25', 'DE26', 'DE27',
    # Austria
    'AT11', 'AT12', 'AT13', 'AT21', 'AT22', 'AT31', 'AT32', 'AT33', 'AT34',
    # Czechia
    'CZ01', 'CZ02', 'CZ03', 'CZ04', 'CZ05', 'CZ06', 'CZ07', 'CZ08',
    # Hungary
    'HU11', 'HU12', 'HU21', 'HU22', 'HU23', 'HU31', 'HU32', 'HU33',
    # Slovenia
    'SI03', 'SI04',
    # Croatia
    'HR03', #'HR04',
    # Romania
    'RO11', 'RO12', 'RO21', 'RO22', 'RO31', 'RO32', 'RO41', 'RO42',
    # Bulgaria
    'BG31', 'BG32', 'BG33', 'BG34', 'BG41', 'BG42'
]
sectors_nace_62 = ['A01', 'A02', 'A03', 'B', 'C10-C12', 'C13-C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', 'C22', 'C23',
           'C24', 'C25', 'C26', 'C27', 'C28', 'C29', 'C30', 'C31_C32', 'C33', 'D', 'E36', 'E37-E39', 'F', 'G45',
           'G46', 'G47', 'H49', 'H50', 'H51', 'H52', 'H53', 'I', 'J58', 'J59_J60', 'J61', 'J62_J63', 'K64', 'K65',
           'K66', 'L', 'M69_M70', 'M71', 'M72', 'M73', 'M74_M75', 'N77', 'N78', 'N79', 'N80-N82', 'O', 'P',
           'Q86', 'Q87_Q88', 'R90-R92', 'R93', 'S94', 'S95', 'S96']
sectors_nace_1 = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S']
key_sectors = ['A01', 'H50', 'H51', 'H52', 'H53', 'K64', 'K65']

time_steps = [f"Q{i}" for i in range(0,13)]

experiments = [f"E{i}" for i in range(0,18)]

dimensionLabels = {"countries":country_codes,"sectors_nace_62":sectors_nace_62,"sectors_nace_1":sectors_nace_1,"time":time_steps,"experiments":experiments}
dimensionLabelsLengths =  [len(dimensionLabels[i]) for i in dimensionLabels.keys()]

sectors_nace_1_colors =  cm.tab20.colors
sectors_nace_62_colors =  cm.tab20(np.linspace(0, 1, len(sectors_nace_62)))

#%% load data
print('loading data')
# `data` is a dictionary with variable names as keys and loaded matrices as values
base = loadmat('Baseline.mat')
shock_eq = loadmat('Earthquake_Q1.mat')
shock_f = loadmat('Flood_Q1.mat')
shock_eq_f = loadmat('Earthquake_Q1_Flood_Q5.mat')
shock_f_eq = loadmat('Flood_Q1_Earthquake_Q5.mat')


scenarios = [shock_f, shock_eq, shock_f_eq, shock_eq_f]
scenarios_names = ["flood", "earthquake", "compound flood earthquake", "compound earthquake flood"]
scenarios_colors = ["deepskyblue", "indianred","deepskyblue", "indianred"]
scenarios_linest = ["-","-","--","--"]

#%% load and prepare map shape
print('loading map')

sns.set(style="whitegrid", palette="pastel", color_codes=True)
sns.mpl.rc("figure", figsize=(10,6))
world = gpd.read_file("ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")
europe = world#world[world['CONTINENT']=='Europe']
europe.insert(len(europe.columns), 'INSET_FIG_X', europe['LABEL_X'])
europe.insert(len(europe.columns), 'INSET_FIG_Y', europe['LABEL_Y'])

europe.loc[europe['ADM0_A3']=='LUX','INSET_FIG_X'] = 2
europe.loc[europe['ADM0_A3']=='LUX','INSET_FIG_Y'] = 54

europe.loc[europe['ADM0_A3']=='NLD','INSET_FIG_X'] = 5.8
europe.loc[europe['ADM0_A3']=='NLD','INSET_FIG_Y'] = 53

europe.loc[europe['ADM0_A3']=='BEL','INSET_FIG_X'] = 2.4
europe.loc[europe['ADM0_A3']=='BEL','INSET_FIG_Y'] = 56

europe.loc[europe['ADM0_A3']=='HRV','INSET_FIG_X'] = 16.9
europe.loc[europe['ADM0_A3']=='HRV','INSET_FIG_Y'] = 44.4

europe.loc[europe['ADM0_A3']=='AUT','INSET_FIG_X'] = 12
europe.loc[europe['ADM0_A3']=='AUT','INSET_FIG_Y'] = 47.5

europe.loc[europe['ADM0_A3']=='ITA','INSET_FIG_X'] = 12
europe.loc[europe['ADM0_A3']=='ITA','INSET_FIG_Y'] = 43.3

europe.loc[europe['ADM0_A3']=='LVA','INSET_FIG_X'] = 21
europe.loc[europe['ADM0_A3']=='LVA','INSET_FIG_Y'] = 58.2

europe.loc[europe['ADM0_A3']=='LUX','INSET_FIG_X'] = 0.2
europe.loc[europe['ADM0_A3']=='LUX','INSET_FIG_Y'] = 52.5

europe.loc[europe['ADM0_A3']=='HUN','INSET_FIG_X'] = 19.45
europe.loc[europe['ADM0_A3']=='HUN','INSET_FIG_Y'] = 47.2

europe.loc[europe['ADM0_A3']=='ROU','INSET_FIG_X'] = 24.2
europe.loc[europe['ADM0_A3']=='ROU','INSET_FIG_Y'] = 46.1

europe.loc[europe['ADM0_A3']=='BGR','INSET_FIG_X'] = 25.5
europe.loc[europe['ADM0_A3']=='BGR','INSET_FIG_Y'] = 42.5

europe.loc[europe['ADM0_A3']=='SVN','INSET_FIG_X'] = 5
europe.loc[europe['ADM0_A3']=='SVN','INSET_FIG_Y'] = 40

europe.loc[europe['ADM0_A3']=='SVK','INSET_FIG_X'] = 26
europe.loc[europe['ADM0_A3']=='SVK','INSET_FIG_Y'] = 50.5

#%% iterate over entries of data and print out shape
# print('Basic shape of Data')
# describeData(base)

#%% calculate means, differences to baseline, aggregate sectors
print('calculating means and aggregating sectors')
thingsWeCareAbout =  ['capital_consumption', 'capital_loss', 'compensation_employees', 'euribor',
                      'government_debt', 'government_deficit', 'nominal_capitalformation', 'nominal_exports',
                      'nominal_fixed_capitalformation', 'nominal_fixed_capitalformation_dwellings',
                      'nominal_gdp', 'nominal_government_consumption', 'nominal_gva',
                      'nominal_household_consumption', 'nominal_imports', 'nominal_output', 'nominal_sector_gva',
                      'nominal_sector_output', 'operating_surplus', 'real_capitalformation', 'real_exports',
                      'real_fixed_capitalformation', 'real_fixed_capitalformation_dwellings', 'real_gdp',
                      'real_government_consumption', 'real_gva', 'real_household_consumption', 'real_imports',
                      'real_output', 'real_sector_gva', 'real_sector_output', 'sector_capital_consumption',
                      'sector_capital_loss', 'sector_operating_surplus', 'taxes_production', 'unemployment_rate',
                      'wages']

scenarios_rel =  []
scenarios_dif =  []
scenarios_dif_rel =  []
for j in range(len(thingsWeCareAbout)):
    base[thingsWeCareAbout[j]+"_mean"] = base[thingsWeCareAbout[j]].mean(axis=1)
    for s in range(len(scenarios)):
        scenarios[s][thingsWeCareAbout[j]+"_mean"] = scenarios[s][thingsWeCareAbout[j]].mean(axis=1)
thingsWeCareAbout = thingsWeCareAbout + [s + "_mean" for s in thingsWeCareAbout]
for j in range(len(thingsWeCareAbout)):
    if 'sector' in thingsWeCareAbout[j]:
        base[thingsWeCareAbout[j]+"_nace1"] = aggregateSectorNace62ToNace1(base[thingsWeCareAbout[j]])
        thingsWeCareAbout.append(thingsWeCareAbout[j]+"_nace1")
    for s in range(len(scenarios)):
        if 'sector' in thingsWeCareAbout[j]:
            scenarios[s][thingsWeCareAbout[j]+"_nace1"] = aggregateSectorNace62ToNace1(scenarios[s][thingsWeCareAbout[j]])
for s in range(len(scenarios)):
    scenarios_rel.append(dict())
    scenarios_dif.append(dict())
    scenarios_dif_rel.append(dict())
    for j in range(len(thingsWeCareAbout)):
        scenarios_rel[s][thingsWeCareAbout[j]] = scenarios[s][thingsWeCareAbout[j]]/base[thingsWeCareAbout[j]]
        scenarios_dif[s][thingsWeCareAbout[j]] = scenarios[s][thingsWeCareAbout[j]]-base[thingsWeCareAbout[j]]
        scenarios_dif_rel[s][thingsWeCareAbout[j]] = (scenarios[s][thingsWeCareAbout[j]]-base[thingsWeCareAbout[j]])/base[thingsWeCareAbout[j]]


#%% grid plots
print('plotting time series')
figdir = 'figures/timeseries'

thing = 'real_output_mean'
plotType = 'dif_rel'

num_countries = len(country_codes)

# Creating a figure and a grid of subplots
nrows=6
ncols=5
subfig_size = [5, 6]

fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(subfig_size[0]*ncols,subfig_size[1]*nrows ))  # Adjust nrows and ncols if needed
fig.suptitle(thing + ' as ' + plotType)
fig.subplots_adjust(hspace=0.5, wspace=0.5)

max_val = 0
min_val = 0
for s in range(len(scenarios)):
    max_val = max(max_val,np.max(scenarios_dif_rel[s][thing]))
    min_val = min(min_val,np.min(scenarios_dif_rel[s][thing]))

# Plotting data for each country in its own subplot
row = 0
col = 0
for index, code in enumerate(country_codes):
    if(col==ncols):
        row+=1
        col=0
    ax = axes[row, col]  # Determine the position of the subplot
    if(plotType=='abs'):
        ax.plot(base[thing][:,index], label='Baseline')
    for s in range(len(scenarios)):
        if plotType == 'abs':
            ax.plot(scenarios[s][thing][:,index], label=scenarios_names[s],
                    color=scenarios_colors[s],linestyle=scenarios_linest[s])
        if plotType == 'dif_rel':
            ax.plot(scenarios_dif_rel[s][thing][:,index], label=scenarios_names[s],
                    color=scenarios_colors[s],linestyle=scenarios_linest[s])
            ax.set_ylim(min_val,max_val)
    ax.set_title(f'{code}')
    ax.set_xlabel('Time Step')
    ax.set_ylabel(thing)
    col+=1
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc='lower right')
# Hide unused subplots
for index in range(num_countries, nrows*ncols):  # Adjust the range if the grid size is changed
    if(col==ncols):
        row+=1
        col=0
    axes[row, col].axis('off')
    col+=1

# Adjust layout
plt.tight_layout()

# Show the plot
if showPlots: plt.show()


if not os.path.exists(figdir):
    os.makedirs(figdir)
fig.savefig(figdir+'/timeseries_' + thing + '_as_' + plotType + '.png')
fig.savefig(figdir+'/timeseries_' + thing + '_as_' + plotType + '.pdf')

plt.close()

#%% spatial plot
print('plotting maps')
basefigdir = 'figures/maps'

nrows=3
ncols=10
subfig_size = [5, 5]

max_val = max(abs(min_val),abs(max_val))
min_val = -max_val

scenariosToPlot = [0,1,2,3]

for scenario_index in scenariosToPlot:
    timestep = 'Q4'

    if plotType == 'abs':
        thing_df = pd.DataFrame({'time': np.repeat(time_steps, len(country_codes)), 'country': country_codes_3 * len(time_steps) , thing:base[thing].flatten()})
    if plotType == 'dif_rel':
        thing_df = pd.DataFrame({'time': np.repeat(time_steps, len(country_codes)), 'country': country_codes_3 * len(time_steps) , thing:scenarios_dif_rel[scenario_index][thing].flatten()})


    # initialize the figure
    nrows=3
    ncols=6
    fig, axes = plt.subplots(nrows, ncols, figsize=(subfig_size[0]*ncols,subfig_size[1]*nrows ))
    fig.suptitle(thing + ' in ' + scenarios_names[scenario_index] + ' scenario as ' + plotType)
    row = 0
    col = 0
    for index, timestep in enumerate(time_steps):

        thing_df_1 = thing_df[thing_df['time']==timestep]

        mergedData = europe.merge(thing_df_1, how='left', left_on='ADM0_A3', right_on='country')

        # determine subfigure
        if(col==ncols):
            row+=1
            col=0
        if row>=nrows or col>=ncols:
            break
        if ncols > 1:
            ax = axes[row, col]
        else:
            ax = axes[row]
        col+=1
        # define colors
        if plotType == 'abs':
            cmap = cm.Reds
            min_val, max_val = min(thing_df[thing]), max(thing_df[thing])
        if plotType == 'dif_rel':
            cmap = cm.seismic_r
        norm = mcolors.Normalize(vmin=min_val, vmax=max_val)

        # create the plot
        mergedData.plot(column=thing, cmap=cmap, norm=norm,
                        edgecolor='black', linewidth=0.2,ax=ax)

        # custom axis
        ax.set_xlim(-15, 35)
        ax.set_ylim(32, 72)
        ax.axis('off')

        # define range and values for the legend
        value_ranges = np.arange(min_val,max_val,(max_val-min_val)/10).tolist()
        labels = ['%.2f' % elem for elem in value_ranges]

        # parameters of the legend
        rectangle_width = 2
        rectangle_height = 1.5
        legend_x = 30
        legend_y_start = 55
        legend_y_step = 1.5

        # create the legend
        for i in range(len(labels)):
           value = (value_ranges[i]-min_val)/(max_val-min_val) # Normalize the value to [0, 1]
           color = cmap(value)
           ax.add_patch(plt.Rectangle((legend_x, legend_y_start - i * legend_y_step), rectangle_width, rectangle_height,
                                      color=color, ec='black', lw=0.6))
           ax.text(legend_x + 2.5, legend_y_start - i * legend_y_step + 0.7, labels[i],
                 fontsize=12, va='center')

        # title
        ax.title.set_text(timestep)
    # Hide unused subplots
    for index in range(len(time_steps), nrows*ncols):  # Adjust the range if the grid size is changed
        if(col==ncols):
            row+=1
            col=0
        axes[row, col].axis('off')
        col+=1

    # display the plot
    plt.tight_layout()
    if showPlots: plt.show()

    figdir = basefigdir
    if not os.path.exists(figdir):
        os.makedirs(figdir)
    fig.savefig('figures/map-'+ thing + '_in_' + scenarios_names[scenario_index] + '_scenario_as_' + plotType + '.png')
    fig.savefig('figures/map-'+ thing + '_in_' + scenarios_names[scenario_index] + '_scenario_as_' + plotType + '.pdf')

    plt.close(fig)

#%% pie chart config
plotType = 'dif_rel'
sector_thing = 'real_sector_output_mean_nace1'
country_index = 22
scenario_index = 1
base_radius = 1
rel_change_scaling = 5
nrows=3
ncols=6
subfig_size=[3,3]

wedgeprops={"edgecolor":"k","linewidth":0.5}

if base[sector_thing].shape[2]==len(sectors_nace_1):
    sector_colors= sectors_nace_1_colors
    sector_names = sectors_nace_1
else:
    sector_colors= sectors_nace_62_colors
    sector_names = sectors_nace_62

#%% function pie charts real output per sector

def addRelChangePiePlot(piedata,ax):
    #circle scale lines
    ax.add_patch(plt.Circle((0,0), base_radius*(1-0.1*rel_change_scaling), linestyle='--', fill = False, edgecolor='gray', linewidth=1))
    ax.add_patch(plt.Circle((0,0), base_radius*(1-0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
    # ax.add_patch(plt.Circle((0,0), base_radius*(1-0.01*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
    ax.add_patch(plt.Circle((0,0), base_radius, linestyle='-', fill = False, edgecolor='k' ))
    # ax.add_patch(plt.Circle((0,0), base_radius*(1+0.01*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
    ax.add_patch(plt.Circle((0,0), base_radius*(1+0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
    # ax.add_patch(plt.Circle((0,0), base_radius*(1+0.1*rel_change_scaling), linestyle='--', fill = False, edgecolor='gray', linewidth=1))

    # the pie wedges
    for s in range(len(piedata)):
        wedges1, texts1 = ax.pie(piedata, radius=base_radius + rel_change_scaling* scenarios_dif_rel[scenario_index][sector_thing][time_index,country_index,s],
                                 colors=sector_colors, wedgeprops=wedgeprops, counterclock=False, startangle=-270)
        for wi in range(len(wedges1)):
            if wi != s:
                wedges1[wi].set_visible(False)

#%% pie charts
print('plotting pies')

basefigdir = 'figures/pies'

# initialize the figure
for country_index in range(len(country_codes)):
    for scenario_index in [0,1,2,3]:
        print(sector_thing + ' in ' + scenarios_names[scenario_index] + ' scenario as ' + plotType + ' for country ' + country_codes_3[country_index])
        fig, axes = plt.subplots(nrows, ncols, figsize=(subfig_size[0]*ncols,subfig_size[1]*nrows ))
        fig.suptitle(sector_thing + ' in ' + scenarios_names[scenario_index] + ' scenario as ' + plotType + ' for country ' + country_codes_3[country_index])
        row = 0
        col = 0
        for time_index, timestep in enumerate(time_steps):
            # determine subfigure
            if(col==ncols):
                row+=1
                col=0
            if row>=nrows or col>=ncols:
                break
            if ncols > 1:
                ax = axes[row, col]
            else:
                ax = axes[row]
            col+=1
            piedata = base[sector_thing][time_index,country_index,:]
            addRelChangePiePlot(piedata,ax)
            # title
            ax.title.set_text(timestep)
        # Hide unused subplots
        for time_index in range(len(time_steps), nrows*ncols-2):  # Adjust the range if the grid size is changed
            if(col==ncols):
                row+=1
                col=0
            axes[row, col].axis('off')
            col+=1

        # scale lines legend
        ax = axes[nrows-1,ncols-2]
        limits = 1+(0.09*rel_change_scaling)
        ax.set_xlim(-limits, limits)
        ax.set_ylim(-limits, limits)
        ax.axis('off')
        ax.add_patch(plt.Circle((0,0), (1-0.1*rel_change_scaling), linestyle='--', fill = False, edgecolor='gray', linewidth=1))
        ax.add_patch(plt.Circle((0,0), (1-0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
        ax.add_patch(plt.Circle((0,0), 1, linestyle='-', fill = False, edgecolor='k' ))
        ax.add_patch(plt.Circle((0,0), (1+0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
        ax.text(0,(1-0.1*rel_change_scaling),'-10%',fontsize=10,
                  backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
        ax.text(0,(1-0.05*rel_change_scaling),'-5%',fontsize=10,
                  backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
        ax.text(0,1,'reference',fontsize=10,
                  backgroundcolor='white',color='black',horizontalalignment='center',verticalalignment='center')
        ax.text(0,(1+0.05*rel_change_scaling),'+5%',fontsize=10,
                  backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
        # ax.text(0,(1+0.1*rel_change_scaling),'+10%',fontsize=10,
        #           backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')

        # sector color legends
        ax =  axes[nrows-1,ncols-1]
        wedges, texts = ax.pie(np.ones(len(piedata)),radius=base_radius, colors=sector_colors, labels=sector_names,
                                 wedgeprops=wedgeprops, counterclock=False, startangle=-270)
        ax.title.set_text('Sectors')

        # display the plot
        plt.tight_layout()
        if showPlots: plt.show()

        # save the plot
        figdir = basefigdir + '/' + scenarios_names[scenario_index]
        if not os.path.exists(figdir):
            os.makedirs(figdir)
        fig.savefig(figdir+'/pie-'+ sector_thing + '_in_' + scenarios_names[scenario_index] + '_scenario_as_' + plotType + ' for country ' + country_codes_3[country_index] + '.png')
        fig.savefig(figdir+'/pie-'+ sector_thing + '_in_' + scenarios_names[scenario_index] + '_scenario_as_' + plotType + ' for country ' + country_codes_3[country_index] + '.pdf')

        plt.close(fig)


#%% function pie charts real output per sector only rel diff

def addBrokenDonutPlot(piedata,ax):
    #circle scale lines
    ax.add_patch(plt.Circle((0,0), base_radius*(1-0.1*rel_change_scaling), linestyle='--', fill = False, edgecolor='gray', linewidth=1))
    ax.add_patch(plt.Circle((0,0), base_radius*(1-0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
    ax.add_patch(plt.Circle((0,0), base_radius, linestyle='-', fill = False, linewidth=0.1 ))
    ax.add_patch(plt.Circle((0,0), base_radius*(1+0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
    for s in range(len(piedata)):
        if scenarios_dif_rel[1][sector_thing][time_index,country_index,s] >= 0:
            wedges1, texts1 = ax.pie(piedata, radius=base_radius * (1 + rel_change_scaling * scenarios_dif_rel[scenario_index][sector_thing][time_index,country_index,s]),
                                     colors=sector_colors, wedgeprops=wedgeprops, counterclock=False, startangle=-270)
            wedges1[s].set_width(base_radius*(1-1/1 + rel_change_scaling * scenarios_dif_rel[scenario_index][sector_thing][time_index,country_index,s]))
        else:
            wedges1, texts1 = ax.pie(piedata, radius=base_radius,
                                     colors=sector_colors, wedgeprops=wedgeprops, counterclock=False, startangle=-270)
            wedges1[s].set_width(- base_radius * rel_change_scaling * scenarios_dif_rel[scenario_index][sector_thing][time_index,country_index,s])
        for wi in range(len(wedges1)):
            if wi != s:
                wedges1[wi].set_visible(False)

#%% broken donut charts real output per sector only rel diff
print('plotting broken donuts')

basefigdir = 'figures/brokendonuts'

max_val = 0
min_val = 0
for s in range(len(scenarios)):
    max_val = max(max_val,np.max(scenarios_dif_rel[s][thing]))
    min_val = min(min_val,np.min(scenarios_dif_rel[s][thing]))

# initialize the figure
for country_index in range(len(country_codes)):
    for scenario_index in [0,1,2,3]:
        print(sector_thing + ' in ' + scenarios_names[scenario_index] + ' scenario as ' + plotType + ' for country ' + country_codes_3[country_index])

        # initialize the figure
        nrows=3
        ncols=6
        fig, axes = plt.subplots(nrows, ncols, figsize=(subfig_size[0]*ncols,subfig_size[1]*nrows))
        fig.suptitle(sector_thing + ' in ' + scenarios_names[scenario_index] + ' scenario as ' + plotType + ' for country ' + country_codes_3[country_index])
        row = 0
        col = 0
        for time_index, timestep in enumerate(time_steps):
            # determine subfigure
            if(col==ncols):
                row+=1
                col=0
            if row>=nrows or col>=ncols:
                break
            if ncols > 1:
                ax = axes[row, col]
            else:
                ax = axes[row]
            col+=1
            piedata = base[sector_thing][time_index,country_index,:]
            addBrokenDonutPlot(piedata,ax)
            # title
            ax.title.set_text(timestep)
        # Hide unused subplots
        for time_index in range(len(time_steps), nrows*ncols-2):  # Adjust the range if the grid size is changed
            if(col==ncols):
                row+=1
                col=0
            axes[row, col].axis('off')
            col+=1

        # scale lines legend
        ax = axes[nrows-1,ncols-2]
        limits = 1+(0.09*rel_change_scaling)
        ax.set_xlim(-limits, limits)
        ax.set_ylim(-limits, limits)
        ax.axis('off')
        ax.add_patch(plt.Circle((0,0), (1-0.1*rel_change_scaling), linestyle='--', fill = False, edgecolor='gray', linewidth=1))
        ax.add_patch(plt.Circle((0,0), (1-0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
        ax.add_patch(plt.Circle((0,0), 1, linestyle='-', fill = False, edgecolor='k' ))
        ax.add_patch(plt.Circle((0,0), (1+0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
        ax.text(0,(1-0.1*rel_change_scaling),'-10%',fontsize=10,
                  backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
        ax.text(0,(1-0.05*rel_change_scaling),'-5%',fontsize=10,
                  backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
        ax.text(0,1,'reference',fontsize=10,
                  backgroundcolor='white',color='black',horizontalalignment='center',verticalalignment='center')
        ax.text(0,(1+0.05*rel_change_scaling),'+5%',fontsize=10,
                  backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')

        # sector color legends
        ax =  axes[nrows-1,ncols-1]
        wedges, texts = ax.pie(np.ones(len(piedata)), colors=sector_colors, labels=sector_names,
                                 wedgeprops=wedgeprops, counterclock=False, startangle=-270)
        ax.title.set_text('Sectors')

        # display the plot
        plt.tight_layout()
        if showPlots: plt.show()

        # save the plot
        figdir = basefigdir + '/' + scenarios_names[scenario_index]
        if not os.path.exists(figdir):
            os.makedirs(figdir)
        fig.savefig(figdir+'/brokendonut-'+ sector_thing + '_in_' + scenarios_names[scenario_index] + '_scenario_as_' + plotType + '_country_ ' + country_codes_3[country_index] + '.png')
        fig.savefig(figdir+'/brokendonut-'+ sector_thing + '_in_' + scenarios_names[scenario_index] + '_scenario_as_' + plotType + '_country_' + country_codes_3[country_index] + '.pdf')

        plt.close(fig)



#%% spatial pie plot
print('plotting maps with broken donuts')
basefigdir='figures/maps-brokendonut'
subfig_size = (15,15)
insetfig_size = min(subfig_size)*0.06
base_radius = 1

thing = 'real_output_mean'
sector_thing = 'real_sector_output_mean_nace1'
sns.set(style="whitegrid", palette="pastel", color_codes=True)

max_val = max(abs(min_val),abs(max_val))
min_val = -max_val

scenariosToPlot = [1]

for scenario_index in scenariosToPlot:
    print('running scenario '+scenarios_names[scenario_index])
    if plotType == 'abs':
        thing_df = pd.DataFrame({'time': np.repeat(time_steps, len(country_codes)), 'country': country_codes_3 * len(time_steps) , thing:base[thing].flatten()})
    if plotType == 'dif_rel':
        thing_df = pd.DataFrame({'time': np.repeat(time_steps, len(country_codes)), 'country': country_codes_3 * len(time_steps) , thing:scenarios_dif_rel[scenario_index][thing].flatten()})


    # initialize the figure
    nrows=3
    ncols=6
    fig, axes = plt.subplots(nrows, ncols, figsize=(subfig_size[0]*ncols,subfig_size[1]*nrows))
    fig.suptitle(thing + ' in ' + scenarios_names[scenario_index] + ' scenario as ' + plotType)
    row = 0
    col = 0
    for time_index, timestep in enumerate(time_steps):
        print(' time step ' + timestep)
        # determine subfigure
        if(col==ncols):
            row+=1
            col=0
        if row>=nrows or col>=ncols:
            break
        if ncols > 1:
            ax = axes[row, col]
        else:
            ax = axes[row]
        col+=1
        # define colors
        if plotType == 'abs':
            cmap = cm.Reds
            min_val, max_val = min(thing_df[thing]), max(thing_df[thing])
        if plotType == 'dif_rel':
            cmap = cm.seismic_r
        norm = mcolors.Normalize(vmin=min_val, vmax=max_val)

        # create the plot
        thing_df_1 = thing_df[thing_df['time']==timestep]
        mergedData = europe.merge(thing_df_1, how='left', left_on='ADM0_A3', right_on='country')
        mergedData.plot(column=thing, cmap=cmap, norm=norm,
                        edgecolor='black', linewidth=0.2,ax=ax)

        # custom axis
        ax.set_xlim(-15, 35)
        ax.set_ylim(32, 72)
        ax.axis('off')

        # arrow for BEL inset
        ax.add_patch(patches.FancyArrowPatch((europe['LABEL_X'][europe['ADM0_A3']=='BEL'].iloc[0],
                                                  europe['LABEL_Y'][europe['ADM0_A3']=='BEL'].iloc[0]),
                                                  (europe['INSET_FIG_X'][europe['ADM0_A3']=='BEL'].iloc[0],
                                                  europe['INSET_FIG_Y'][europe['ADM0_A3']=='BEL'].iloc[0]-1.9),
                                                  color='k', linewidth=0.2,connectionstyle="arc3,rad=-.3"))

        # arrow for LUX inset
        ax.add_patch(patches.FancyArrowPatch((europe['LABEL_X'][europe['ADM0_A3']=='LUX'].iloc[0],
                                                  europe['LABEL_Y'][europe['ADM0_A3']=='LUX'].iloc[0]),
                                                  (europe['INSET_FIG_X'][europe['ADM0_A3']=='LUX'].iloc[0]+1.3,
                                                  europe['INSET_FIG_Y'][europe['ADM0_A3']=='LUX'].iloc[0]-1.3),
                                                  color='k', linewidth=0.2,connectionstyle="arc3,rad=-.3"))

        # arrow for SVN inset
        ax.add_patch(patches.FancyArrowPatch((europe['LABEL_X'][europe['ADM0_A3']=='SVN'].iloc[0],
                                                  europe['LABEL_Y'][europe['ADM0_A3']=='SVN'].iloc[0]),
                                                  (europe['INSET_FIG_X'][europe['ADM0_A3']=='SVN'].iloc[0]+1.9,
                                                  europe['INSET_FIG_Y'][europe['ADM0_A3']=='SVN'].iloc[0]),
                                                  color='k', linewidth=0.2,connectionstyle="arc3,rad=-.6"))

        # arrow for SVK inset
        ax.add_patch(patches.FancyArrowPatch((europe['LABEL_X'][europe['ADM0_A3']=='SVK'].iloc[0]+2,
                                                  europe['LABEL_Y'][europe['ADM0_A3']=='SVK'].iloc[0]),
                                                  (europe['INSET_FIG_X'][europe['ADM0_A3']=='SVK'].iloc[0]-1.3,
                                                  europe['INSET_FIG_Y'][europe['ADM0_A3']=='SVK'].iloc[0]-1.3),
                                                  color='k', linewidth=0.2,connectionstyle="arc3,rad=.1"))
        # country inset plots
        for country_index in range(len(country_codes)):
            print('Making inset ' + country_codes_3[country_index])
            ax_sub = inset_axes(ax, width=insetfig_size, height=insetfig_size, loc=10,
                                bbox_to_anchor=(europe[europe['ADM0_A3']==country_codes_3[country_index]]['INSET_FIG_X'],
                                                europe[europe['ADM0_A3']==country_codes_3[country_index]]['INSET_FIG_Y']),
                                bbox_transform=ax.transData)
            piedata = base[sector_thing][time_index,country_index,:]
            addBrokenDonutPlot(piedata,ax_sub)

        # define range and values for the legend
        value_ranges = np.arange(min_val,max_val,(max_val-min_val)/10).tolist()
        labels = ['%.2f' % elem for elem in value_ranges]

        # parameters of the legend
        rectangle_width = 2
        rectangle_height = 1.5
        legend_x = 30
        legend_y_start = 55
        legend_y_step = 1.5

        # create the legend
        for i in range(len(labels)):
           value = (value_ranges[i]-min_val)/(max_val-min_val) # Normalize the value to [0, 1]
           color = cmap(value)
           ax.add_patch(plt.Rectangle((legend_x, legend_y_start - i * legend_y_step), rectangle_width, rectangle_height,
                                      color=color, ec='black', lw=0.6))
           ax.text(legend_x + 2.5, legend_y_start - i * legend_y_step + 0.7, labels[i],
                 fontsize=12, va='center')

        # title
        ax.title.set_text(timestep)

        # scale lines legend
        ax_sub = inset_axes(ax, width=insetfig_size*1.5, height=insetfig_size*1.5, loc=10,
                            bbox_to_anchor=(ax.get_xlim()[0]+3,ax.get_ylim()[1]-5),
                            bbox_transform=ax.transData)
        limits = 1+(0.09*rel_change_scaling)
        ax_sub.set_xlim(-limits, limits)
        ax_sub.set_ylim(-limits, limits)
        ax_sub.axis('off')
        ax_sub.add_patch(plt.Circle((0,0), (1-0.1*rel_change_scaling), linestyle='--', fill = False, edgecolor='gray', linewidth=1))
        ax_sub.add_patch(plt.Circle((0,0), (1-0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
        ax_sub.add_patch(plt.Circle((0,0), 1, linestyle='-', fill = False, edgecolor='k' ))
        ax_sub.add_patch(plt.Circle((0,0), (1+0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
        ax_sub.title.set_text('Relative Change')
        textkw = dict(facecolor='white',linewidth=0,pad=1)
        txt=ax_sub.text(0,(1-0.11*rel_change_scaling),'-10%',fontsize=10,
                  backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
        txt.set_bbox(textkw)
        txt=ax_sub.text(0,(1-0.05*rel_change_scaling),'-5%',fontsize=10,
                  backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
        txt.set_bbox(textkw)
        # ax_sub.text(0,1,'reference',fontsize=10,
        #           backgroundcolor='white',color='black',horizontalalignment='center',verticalalignment='center')
        txt=ax_sub.text(0,(1+0.05*rel_change_scaling),'+5%',fontsize=10,
                  backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
        txt.set_bbox(textkw)

        # sector color legends
        ax_sub = inset_axes(ax, width=insetfig_size*1.5, height=insetfig_size*1.5, loc=10,
                            bbox_to_anchor=(ax.get_xlim()[0]+10,ax.get_ylim()[1]-5),
                            bbox_transform=ax.transData)
        wedges, texts = ax_sub.pie(np.ones(len(piedata)), colors=sector_colors, labels=sector_names,
                                 wedgeprops=wedgeprops, counterclock=False, startangle=-270)
        ax_sub.title.set_text('Sectors')

        # save just the subplot
        figdir = basefigdir + '/' + scenarios_names[scenario_index]
        if not os.path.exists(figdir):
            os.makedirs(figdir)
        fig.savefig(figdir+'/map-brokendonut-'+ sector_thing + '_in_' + scenarios_names[scenario_index] + '_scenario_as_' + plotType + '_time_step_ ' + timestep + '.png',
                    bbox_inches=ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).expanded(1, 1))
        fig.savefig(figdir+'/map-brokendonut-'+ sector_thing + '_in_' + scenarios_names[scenario_index] + '_scenario_as_' + plotType + '_time_step_ ' + timestep + '.pdf',
                    bbox_inches=ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).expanded(1, 1))

    # Hide unused subplots
    for time_index in range(len(time_steps), nrows*ncols):  # Adjust the range if the grid size is changed
        if(col==ncols):
            row+=1
            col=0
        axes[row, col].axis('off')
        col+=1

    # display the plot
    plt.tight_layout()
    if showPlots: plt.show()

    # save just the whole figure
    figdir = basefigdir
    if not os.path.exists(figdir):
        os.makedirs(figdir)
    fig.savefig(figdir+'/map-brokendonut-'+ sector_thing + '_in_' + scenarios_names[scenario_index] + '_scenario_as_' + plotType + '.png')
    fig.savefig(figdir+'/map-brokendonut-'+ sector_thing + '_in_' + scenarios_names[scenario_index] + '_scenario_as_' + plotType + '.pdf')

    plt.close(fig)

#%% test

# subfig_width =  15
# subfig_height =  15
# insetfig_size = min(subfig_width,subfig_height)*0.06
# base_radius = 1

# fig, axes = plt.subplots(1, 1, figsize=(subfig_width, subfig_height))
# fig.suptitle(thing + ' in ' + scenarios_names[scenario_index] + ' scenario as ' + plotType)
# row = 1
# col = 1
# time_index, timestep = 5, 'Q5'
# thing_df_1 = thing_df[thing_df['time']==timestep]

# # determine subfigure
# ax = axes

# # create the plot
# thing_df_1 = thing_df[thing_df['time']==timestep]
# mergedData = europe.merge(thing_df_1, how='left', left_on='ADM0_A3', right_on='country')
# mergedData.plot(column=thing, cmap=cmap, norm=norm,
#                 edgecolor='black', linewidth=0.2,ax=ax)

# # custom axis
# ax.set_xlim(-15, 35)
# ax.set_ylim(32, 72)
# ax.axis('off')




# # arrow for BEL inset
# ax.add_patch(patches.FancyArrowPatch((europe['LABEL_X'][europe['ADM0_A3']=='BEL'].iloc[0],
#                                           europe['LABEL_Y'][europe['ADM0_A3']=='BEL'].iloc[0]),
#                                           (europe['INSET_FIG_X'][europe['ADM0_A3']=='BEL'].iloc[0],
#                                           europe['INSET_FIG_Y'][europe['ADM0_A3']=='BEL'].iloc[0]-1.9),
#                                           color='k', linewidth=0.2,connectionstyle="arc3,rad=-.3"))

# # arrow for LUX inset
# ax.add_patch(patches.FancyArrowPatch((europe['LABEL_X'][europe['ADM0_A3']=='LUX'].iloc[0],
#                                           europe['LABEL_Y'][europe['ADM0_A3']=='LUX'].iloc[0]),
#                                           (europe['INSET_FIG_X'][europe['ADM0_A3']=='LUX'].iloc[0]+1.3,
#                                           europe['INSET_FIG_Y'][europe['ADM0_A3']=='LUX'].iloc[0]-1.3),
#                                           color='k', linewidth=0.2,connectionstyle="arc3,rad=-.3"))

# # arrow for SVN inset
# ax.add_patch(patches.FancyArrowPatch((europe['LABEL_X'][europe['ADM0_A3']=='SVN'].iloc[0],
#                                           europe['LABEL_Y'][europe['ADM0_A3']=='SVN'].iloc[0]),
#                                           (europe['INSET_FIG_X'][europe['ADM0_A3']=='SVN'].iloc[0]+1.9,
#                                           europe['INSET_FIG_Y'][europe['ADM0_A3']=='SVN'].iloc[0]),
#                                           color='k', linewidth=0.2,connectionstyle="arc3,rad=-.6"))

# # arrow for SVK inset
# ax.add_patch(patches.FancyArrowPatch((europe['LABEL_X'][europe['ADM0_A3']=='SVK'].iloc[0]+2,
#                                           europe['LABEL_Y'][europe['ADM0_A3']=='SVK'].iloc[0]),
#                                           (europe['INSET_FIG_X'][europe['ADM0_A3']=='SVK'].iloc[0]-1.3,
#                                           europe['INSET_FIG_Y'][europe['ADM0_A3']=='SVK'].iloc[0]-1.3),
#                                           color='k', linewidth=0.2,connectionstyle="arc3,rad=.1"))

# # country inset plots
# for country_index in range(len(country_codes)):
#     print('Making inset ' + country_codes_3[country_index])
#     ax_sub = inset_axes(ax, width=insetfig_size, height=insetfig_size, loc=10,
#                         bbox_to_anchor=(europe[europe['ADM0_A3']==country_codes_3[country_index]]['INSET_FIG_X'],
#                                         europe[europe['ADM0_A3']==country_codes_3[country_index]]['INSET_FIG_Y']),
#                         bbox_transform=ax.transData)
#     piedata = base[sector_thing][time_index,country_index,:]
#     addBrokenDonutPlot(piedata,ax_sub)
#     # addRelChangePiePlot(piedata,ax_sub)
#     # limits = 1+(0.09*rel_change_scaling)
#     # ax_sub.set_xlim(-limits, limits)
#     # ax_sub.set_ylim(-limits, limits)
#     # ax_sub.axis('off')
#     # ax_sub.add_patch(plt.Circle((0,0), base_radius*(1+0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))

# # define range and values for the legend
# value_ranges = np.arange(min_val,max_val,(max_val-min_val)/10).tolist()
# labels = ['%.2f' % elem for elem in value_ranges]

# # parameters of the legend
# rectangle_width = 2
# rectangle_height = 1.5
# legend_x = 30
# legend_y_start = 55
# legend_y_step = 1.5

# # create the legend
# for i in range(len(labels)):
#    value = (value_ranges[i]-min_val)/(max_val-min_val) # Normalize the value to [0, 1]
#    color = cmap(value)
#    ax.add_patch(plt.Rectangle((legend_x, legend_y_start - i * legend_y_step), rectangle_width, rectangle_height,
#                               color=color, ec='black', lw=0.6))
#    ax.text(legend_x + 2.5, legend_y_start - i * legend_y_step + 0.7, labels[i],
#          fontsize=12, va='center')

# # title
# ax.title.set_text(timestep)

# # scale lines legend
# ax_sub = inset_axes(ax, width=insetfig_size*1.5, height=insetfig_size*1.5, loc=10,
#                     bbox_to_anchor=(ax.get_xlim()[0]+3,ax.get_ylim()[1]-5),
#                     bbox_transform=ax.transData)
# limits = 1+(0.09*rel_change_scaling)
# ax_sub.set_xlim(-limits, limits)
# ax_sub.set_ylim(-limits, limits)
# ax_sub.axis('off')
# ax_sub.add_patch(plt.Circle((0,0), (1-0.1*rel_change_scaling), linestyle='--', fill = False, edgecolor='gray', linewidth=1))
# ax_sub.add_patch(plt.Circle((0,0), (1-0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
# ax_sub.add_patch(plt.Circle((0,0), 1, linestyle='-', fill = False, edgecolor='k' ))
# ax_sub.add_patch(plt.Circle((0,0), (1+0.05*rel_change_scaling), linestyle=':', fill = False, edgecolor='gray', linewidth=1))
# ax_sub.title.set_text('Relative Change')
# textkw = dict(facecolor='white',linewidth=0,pad=1)
# txt=ax_sub.text(0,(1-0.11*rel_change_scaling),'-10%',fontsize=10,
#           backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
# txt.set_bbox(textkw)
# txt=ax_sub.text(0,(1-0.05*rel_change_scaling),'-5%',fontsize=10,
#           backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
# txt.set_bbox(textkw)
# # ax_sub.text(0,1,'reference',fontsize=10,
# #           backgroundcolor='white',color='black',horizontalalignment='center',verticalalignment='center')
# txt=ax_sub.text(0,(1+0.05*rel_change_scaling),'+5%',fontsize=10,
#           backgroundcolor='white',color='gray',horizontalalignment='center',verticalalignment='center')
# txt.set_bbox(textkw)

# # sector color legends
# ax_sub = inset_axes(ax, width=insetfig_size*1.5, height=insetfig_size*1.5, loc=10,
#                     bbox_to_anchor=(ax.get_xlim()[0]+10,ax.get_ylim()[1]-5),
#                     bbox_transform=ax.transData)
# wedges, texts = ax_sub.pie(np.ones(len(piedata)), colors=sector_colors, labels=sector_names,
#                          wedgeprops=wedgeprops, counterclock=False, startangle=-270)
# ax_sub.title.set_text('Sectors')
