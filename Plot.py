import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt 
import matplotlib.ticker as ticker
import numpy as np
import collections as clt
import sys
import os
import difflib as dl  
import re
import timeit

from Input import Tracking 

# --------------------------- RC PARAMS STYLE SECTION -------------------------------------
mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['axes.labelsize'] = 15
mpl.rcParams['axes.titlesize'] = 20
mpl.rcParams['figure.figsize'] = 15., 10.    # figure size in inches

mpl.rcParams['legend.fontsize'] = 16
# --------------------------- ----------------------- -------------------------------------

# Functions following from here should be put into another class, PlottingData 
#
def plot_defaultData():
    pass

def plot_diffApers(df, aperList, plotpath, selection = 'SR', Type = 'hit', aperture = 'all', verbose = 0, nBin = 100, save = 0):
            
    """
    This is a function to plot selected collimation data.
        -- frame is chosen as df 
            ==> ATTENTION:  df requires a name given to it: in case of collimation, name must contain 'col', 
                            else not.
        -- Type: specify which data to be plotted: 'hits' or 'origin'; defaults to 'hits'
        -- save: choose whether or not the plots are dumped as pdf
        -- verbose: additional output
        -- nBin: specify number of bins; defaults to 100
        -- aperture: allows to choose only certain dimensions; defaults to 'all'
    """
   
    event_last = 999999999
    track_last = 999999999
    
    # based on chose in 'selection', slice out SR data from overall frame df
    # pass name from df to sliced df
    #
    if selection == 'SR':
        df_sliced = df[(df.Creator == 'SynRad') & (df.charge == 0)]
        df_sliced.name = df.name
    else:
        raise RuntimeError('Other selections not yet implemented!')
    
    # check the df name, if collimation data, groupby apertures
    #
    if re.findall('col', df_sliced.name):
        print ("found collimator frame - groupby 'CollDim' \n", "-----------------------------")
        
        if aperture == 'all':
            # add the aperture option here?
            print ('selected all apertures!')
            grouped = df.groupby('CollDim')

        else:
            DF = pd.DataFrame()
            for i in aperture:
                print ('aperture selected:', i)
                if i in aperList:
                    tmp = df_sliced[df_sliced.CollDim == i]
                    DF = DF.append(tmp)
    #                 print (tmp.head())
                else:
                    raise ValueError('Selected aperture', i, 'not in the list.')
                
            grouped = DF.groupby('CollDim')


        plt.figure(figsize = (15,10))
        plt.rc('grid', linestyle = "--", color = 'grey')
        plt.grid()

        for name, frame in grouped:
            if verbose:
                print (name)
                
            Z_org = []; Z_hit = []; E_org = []; E_hit = []

            for row in frame.index:
                event = frame.get_value(row,'Event')
                track = frame.get_value(row,'Track')
                z_eu  = frame.get_value(row,'z_eu')
                mat   = frame.get_value(row,'Material')
                energ = frame.get_value(row,'ptot')
                if(event_last != event or track_last != track):
                    event_last = event
                    track_last = track
                    Z_org.append(z_eu)
                    E_org.append(energ*10**6)
                elif(mat == 'Cu'): # 'Fe'
                    Z_hit.append(z_eu)
                    E_hit.append(energ)
                    
            if Type == 'hit':
                plt.title("SR photons hitting beampipe")
                plt.hist(Z_hit, bins = nBin, range = (-300, 100), histtype = 'step', fill = False, linewidth = 1.5, label = str(name))
#                 frame[frame.Material == 'Cu'].hist(column = 'z_eu', bins = nBin, label = name)
                plt.xlabel("z [m]")
                plt.ylabel("photons/bin")
                plt.legend()
                if(save == 1):
                    plt.savefig(plotpath + 'SR_hits_coll.pdf', bbox_inches='tight')
                    print ("saved plot as", plotpath,"SR_hits_coll.pdf")
                
            elif Type == 'origin':
                plt.title("Origin of SR photons")
                plt.hist(Z_org, bins = nBin, range = (-550, 0), histtype = 'step', fill = False, linewidth = 1.5,
                         label = 'dummy', stacked = False)
                plt.xlabel("z [m]")
                plt.ylabel("photons/bin")
                plt.legend()
                if(save == 1):
                    plt.savefig(plotpath + 'SR_origin_coll.pdf', bbox_inches='tight')
                    print ("saved plot as", plotpath,"SR_origin_coll.pdf")
    
    # if no collimation data selected the sliced frame is used without groupby
    #
    else:
        print ("no collimator frame - no groupby operation \n -----------------------------")
        print (df_sliced.name)
        
        Z_org = []; Z_hit = []; E_org = []; E_hit = []
        
        plt.figure(figsize = (15,10))
        plt.rc('grid', linestyle = "--", color = 'grey')
        plt.grid()
        
        for row in df_sliced.index:
            event = df.get_value(row,'Event')
            track = df.get_value(row,'Track')
            z_eu  = df.get_value(row,'z_eu')
            mat   = df.get_value(row,'Material')
            energ = df.get_value(row,'ptot')
    #         print (row, event, event_last, track, track_last)
            if(event_last != event or track_last != track):
                event_last = event
                track_last = track
                Z_org.append(z_eu)
                E_org.append(energ*10**6)
            elif(mat == 'Cu'): # 'Fe'
                Z_hit.append(z_eu)
                E_hit.append(energ)
            
        if Type == 'hit':
            plt.title("SR photons hitting beampipe")
            plt.hist(Z_hit, bins = nBin, range = (-300, 100), histtype = 'step', fill = False, linewidth = 1.5, label = str(df.name))
            plt.xlabel("z [m]")
            plt.ylabel("photons/bin")
            plt.legend()
            if(save == 1):
                plt.savefig(plotpath + 'SR_hits_def.pdf', bbox_inches='tight')
                print ("saved plot as", plotpath,"SR_hits_def.pdf")
                
        elif Type == 'origin':
            plt.title("Origin of SR photons")
            plt.hist(Z_org, bins = nBin, range = (-550, 0), histtype = 'step', fill = False, linewidth = 1.5, label = str(df.name), stacked = False)
            plt.xlabel("z [m]")
            plt.ylabel("photons/bin")
            plt.legend()
            if(save == 1):
                plt.savefig(plotpath + 'SR_origin_def.pdf', bbox_inches='tight')
                print ("saved plot as", plotpath,"SR_origin_def.pdf")


def plot_diffBeamShape(df, plotpath, beamTypes, beamSizes, zlim = [], beam = 'all', size = 'all', elements = [], Type = 'hit', nBin = 100, ticks = 5, verbose = 0, save = 0):
    """
    Function to plot data from secondary events, taking into account different beam shapes and sizes. 
    In case of Type = hit allows to plot hits within a certain element. For Type == origin, it plots the origin of all elements or in a single element, if combined with selection in element
        -- df:          pass data frame to fct. 
        -- plotpath:    point to a directory for storing plots
        -- beamTypes:
        -- beamSizes:
        -- zlim:		array to put zmin and zmax; allows to plot only certain region; default empty 
        -- beam:        allows to select the beam shape. Available are pencil, gauss, flat and ring
        -- size:        choose beam sizes; gauss,flat and ring have to start with >0; defaults to 'all'
        -- element:     choose single element to plot results for
        -- Type:        choose which spectrum to plot - hits or origin
        -- nBin:        choose the binnig, defaults to 100
        -- verbose:     switch on/off verbose output
        -- save:        select whether or not the plots are dumped to pdf files
    
    returns: nothing. Simple plottig tool
    """
    
    if re.findall('col', df.name):
        print ("Found collimator frame - groupby 'CollDim' \n", "-----------------------------")
    else:
        print ("Found no collimator frame - analysing default data \n", "-----------------------------")
        if verbose: print ("beam types:", beamTypes, '\n' "beam sizes:", beamSizes)
    
    # do the slicing based on Creator and charge to secure synchrotron radiation -- mlu 11-21-2017 now hardcoded!
    #
    df_sliced = df[(df.Creator == 'SynRad') & (df.charge == 0)]
    df_sliced.name = df.name
    
    # additional option to select certain element(s), hsa to be able to accept a list
    #
    if elements:
        df_sliced = df_sliced[df_sliced.element.isin(elements)] # slices the df based on selected elements 
    
    # check result of selection above
    #   
    if verbose > 1: print ("Sliced data frame: \n", "----------------------------- \n", df_sliced)
    
    # case 1
    #
    if beam == 'all' and size == 'all':
              
        print ('selected all beam types and sizes!')
        grouped = df_sliced.groupby(['optics','BeamShape','BeamSize']) 
        
    # case 2
    #
    elif beam == 'all' and size != 'all':
        DF = pd.DataFrame()
        
        for j in size:
            print ("All beam types of size", j, "selected")
                
            if j in beamSizes:
                tmp = df_sliced[df_sliced.BeamSize == j] 
                DF = DF.append(tmp)
                if verbose: print (tmp.head())
            else:
                raise ValueError("Selected beam size", j, "not in the list of available beam sizes:", beamSizes)
        
        grouped = DF.groupby(['optics','BeamSize'])
    
    # case 3    
    #
    elif beam != 'all' and size != 'all':
        
        DF = pd.DataFrame()
        framelist = []
        for i in beam:
            for j in size:
                print ("Type", i, "selected, with size", j, "sigma")
                    
                if i in beamTypes and j in beamSizes:
                    tmp = df_sliced[(df_sliced.BeamShape == i) & (df_sliced.BeamSize == j)]
                    framelist.append(tmp)
                    if verbose > 1: print (tmp)
                elif i not in beamTypes:
                    raise ValueError("Selected beam type", i, "not in the list of available beams:", beamTypes)
                elif j not in beamSizes:
                    raise ValueError("Selected beam size", j, "not in the list of available beam sizes:", beamSizes)
        
        DF = DF.append(framelist)
        grouped = DF.groupby(['optics','BeamShape','BeamSize'])
    
    # case 4
    #
    elif beam != 'all' and size == 'all':
        
        DF = pd.DataFrame()
        for i in beam:
            print ("Type", i, "selected with all sizes.")
            if i in beamTypes:
                tmp = df_sliced[df_sliced.BeamShape == i] 
                DF = DF.append(tmp)
                #if verbose: print (tmp.head())
            else:
                raise ValueError("Selected beam type", i, "not in the list of available beams:", beamTypes)
        
        if verbose: print (DF)
        grouped = DF.groupby(['optics','BeamShape','BeamSize'])
    
    else:
        raise RuntimeError("Invalid selection of choice(s)!")
    
    # settings for the plot
    #
    plt.figure(figsize = (15,10))
    ax = plt.subplot(111)
    plt.rc('grid', linestyle = "--", color = 'grey')
    plt.grid()
    
    # allows to set the xlim
    #
    if zlim: plt.xlim(zlim[0], zlim[1])

    for name, frame in grouped:
        
        if verbose:
            print ("current group:", name)
        
        # invoke new function from Input.py -- initiate tracking object from class
        # use collectInfo to select z data
        #
        tracking = Tracking(frame)
        Z_pos, Z_org, Z_hit = tracking.collectInfo(verbose = verbose)
         
        # plot resulting data
        #
        if Type == 'hit':
            plt.title("SR photons hitting beampipe")
            plt.hist(Z_hit, bins = nBin, histtype = 'step', fill = False, linewidth = 1.5, label = str(name), stacked = False)  # range = (-300, 100),
               
        elif Type == 'position':
            plt.title("Position of SR photons")
            plt.hist(Z_pos, bins = nBin, histtype = 'step', fill = False, linewidth = 1.5, label = str(name), stacked = False) #, range = (-550, 0)
            
        elif Type == 'origin':
            plt.title("Origin of SR photons")
            plt.hist(Z_org, bins = nBin, histtype = 'step', fill = False, linewidth = 1.5, label = str(name), stacked = False) #, range = (-550, 0)
        else:
            raise RuntimeError("Invalid selection of Type!")
    
    #ax.xaxis.set_major_locator(ticker.MultipleLocator(ticks))

    plt.ylabel("photons/bin")
    plt.xlabel("z [m]")

    plt.legend()
    ax.legend(loc = 'lower center', bbox_to_anchor = (0.5, -0.15), ncol = 4)
    
    if (Type == 'hit' and save == 1):
        plt.savefig(plotpath + 'SR_hits_beamshape.pdf', bbox_inches = 'tight')
        print ("saved plot as", plotpath, "SR_hits_beamshape.pdf")
    elif (Type == 'position' and save == 1):
        plt.savefig(plotpath + 'SR_position_beamshape.pdf', bbox_inches = 'tight')
        print ("saved plot as", plotpath, "SR_position_beamshape.pdf")
    elif(Type == 'origin' and save == 1):
        plt.savefig(plotpath + 'SR_origin_beamshape.pdf', bbox_inches = 'tight')
        print ("saved plot as", plotpath, "SR_origin_beamshape.pdf")


def plotSrcHits(df, plotpath, elements, zlim = [], nBin = 100, save = 0, verbose = 0):
    """
    Method to select certain elements as sources and plot hits caused by these elements.
    Requires full element names, no groups implemented yet.
        -- df:      dataframe to do the selection on
        -- name:    list of names, has to be passed as list, even for single element
        -- nBin:    set number of bins/binning level
        -- save:    choose to whether or not save the plot
        -- verbose: switch on/off or set level of verbosity
    """
    
    plt.figure(figsize = (15,10))
    ax = plt.subplot(111)
    plt.title("Hits from Element(s)")
    plt.rc('grid', linestyle = '--', color = 'gray')
    
    # allows to set the z range as option
    #
    if zlim: plt.xlim(zlim[0], zlim[1])
    
    # check, if elements is not empty
    #
    if elements == []:
        raise RuntimeError("Elements is empty --> no elements to plot!")
        
    # do the actual selection, based on passed elements
    #
    for elem in elements:
        selection = df[df.OrigVol == elem]
    
        hits = selection[selection.Material == 'Cu']
        zpos = hits.z_eu.tolist()
    
        plt.hist(zpos, bins = nBin, histtype = 'step', fill = False, label = str(elem))
        
        if verbose > 1: print (hits.Track)
        
    plt.grid(); plt.legend()
    ax.legend(loc = 'lower center', bbox_to_anchor = (0.5, -0.25), ncol = 4)
    plt.ylabel('photons/bin')
    plt.xlabel('z [m]')
    
    if save == 1: 
        print ("Saving figure as ", plotpath, "SR_hitsFrmElmt.pdf")
        plt.savefig(plotpath + "SR_hitsFrmElmt.pdf", bbox_inches = 'tight')
