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
from Input import DataSelection

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

def plot_diffApers(df, plotpath, selection = 'SR', Type = 'hit', aperture = 'all', verbose = 0, zlim = [], nBin = 100, ticks = 10, legCol = 2, save = 0):
            
    """
    This is a function to plot selected collimation data and gives the option to select only certain or all dimensions. Dimensions refer to the collimator opening.
        -- df:          dataframe that holds data to plot 
                        ==> ATTENTION:  df requires a name given to it: in case of collimation, name must contain 'col', 
                                        else not.
        -- Type:        specify which data to be plotted: 'hits' or 'origin'; defaults to 'hits'
        -- aperture:    defaults to 'all' but allows selecting only certain apertures
        -- verbose:     additional output
        -- zlim:        allows tp plot only certain z range, defaults to empty list
        -- nBin:        specify number of bins; defaults to 100
        -- ticks:       refine the tick frequenc if necessary
        -- legCol:      specify number of columns in the legend box, defaults to 2
        -- save:        choose whether or not the plots are dumped as pdf
        
    returns: nothing. Simple plottig tool
    """
    # invoke aper_select from DataSelection
    #
    selection = DataSelection(df, verbose)
    grouped = selection.aper_select(aperture, verbose)
    
    # ~ # create a list of available apertures from the frame
    # ~ #
    # ~ aperList = df.CollDim.unique()
    # ~ if verbose: print (" -*-*-*-*-*-*-*-*-*-*-*-*- \n", "List of apertures: ", aperList)
    
    # ~ # based on chose in 'selection', slice out SR data from overall frame df
    # ~ # pass name from df to sliced df
    # ~ #
    # ~ if selection == 'SR':
        # ~ df_sliced = df[(df.Creator == 'SynRad') & (df.charge == 0)]
        # ~ df_sliced.name = df.name
    # ~ else:
        # ~ raise RuntimeError('Other selections not yet implemented!')
    
    # ~ # check the df name, if collimation data, groupby apertures
    # ~ #
    # ~ if re.findall('col', df_sliced.name):
        # ~ print ("found collimator frame - groupby 'CollDim' \n", "-----------------------------")
        
        # ~ if aperture == 'all':
            # ~ # add the aperture option here?
            # ~ print ('selected all apertures!')
            
            # ~ grouped = df_sliced.groupby(['CollDim', 'optics', 'BeamShape'])   #['CollDim','optics','BeamShape','BeamSize']

        # ~ else:
            # ~ DF = pd.DataFrame()
            # ~ for i in aperture:
                # ~ print ('aperture selected:', i)
                # ~ if i in aperList:
                    # ~ tmp = df_sliced[df_sliced.CollDim == i]
                    # ~ DF = DF.append(tmp)
    # ~ #                 print (tmp.head())
                # ~ else:
                    # ~ raise ValueError('Selected aperture', i, 'not in the list. Available are:', aperList)
                
            # ~ grouped = DF.groupby(['CollDim', 'optics', 'BeamShape']) # ,'optics','BeamShape','BeamSize'


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
                
        if verbose: print ( "current group:", name )
        elif verbose > 1: print ( "parent frame:", grouped )

        tracking = Tracking(frame, verbose)
        Z_pos, Z_org, Z_hit = tracking.collectInfo(verbose = verbose)
        
        count = sum(1 for x in Z_hit if (x > -2) & (x < 2) )
        
        print ("*** TEST --> counting hits:", count)

                    
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
    

    plt.locator_params(axis = 'x', nbins = ticks)

    plt.ylabel( "photons/bin" )
    plt.xlabel( "z [m]" )

    plt.legend()
    ax.legend( loc = 'lower center', bbox_to_anchor = (0.5, -0.25), ncol = legCol )
    
    if (Type == 'hit' and save == 1):
        plt.savefig(plotpath + 'SR_hits_aper.pdf', bbox_inches = 'tight')
        print ("saved plot as", plotpath, "SR_hits_aper.pdf")
    elif (Type == 'position' and save == 1):
        plt.savefig(plotpath + 'SR_position_aper.pdf', bbox_inches = 'tight')
        print ("saved plot as", plotpath, "SR_position_aper.pdf")
    elif(Type == 'origin' and save == 1):
        plt.savefig(plotpath + 'SR_origin_aper.pdf', bbox_inches = 'tight')
        print ("saved plot as", plotpath, "SR_origin_aper.pdf")
    
    
    

def plot_diffBeamShape(df, plotpath, beamTypes, beamSizes, zlim = [], beam = 'all', size = 'all', elements = [], Type = 'hit', nBin = 100, ticks = 10, verbose = 0, legCol = 2, save = 0):
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
        -- ticks:       set the number of tickss on the xaxis (acts on binning)
        -- verbose:     switch on/off verbose output
        -- legCol:      specify number of columns in the legend box, defaults to 2
        -- save:        select whether or not the plots are dumped to pdf files
    
    returns: nothing. Simple plottig tool
    """
    
    # check for collimation and use switch for groupby further below
    #
    if re.findall('col', df.name):
        collimation = 1
        print ("Found collimator frame - groupby 'CollDim' \n", "-----------------------------")
    else:
        collimation = 0
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
    else:
        print (" *** Warning: No elements selected, defaults to all.")
    
    # check result of selection above
    #   
    if verbose > 1: print ("Sliced data frame: \n", "----------------------------- \n", df_sliced)
    
    # case 1
    #
    if beam == 'all' and size == 'all':
              
        print ('selected all beam types and sizes!')
        
        if collimation: grouped = df_sliced.groupby(['CollDim','optics','BeamShape','BeamSize'])
        else: grouped = df_sliced.groupby(['optics','BeamShape','BeamSize']) 
        
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
        
        if collimation: grouped = DF.groupby(['CollDim','optics','BeamSize'])
        else: grouped = DF.groupby(['optics','BeamSize'])
    
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
        if collimation: grouped = DF.groupby(['CollDim','optics','BeamShape','BeamSize'])
        else: grouped = DF.groupby(['optics','BeamShape','BeamSize'])
    
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
        
        if collimation: grouped = DF.groupby(['CollDim','optics','BeamShape']) #,'BeamSize'])
        else: grouped = DF.groupby(['optics','BeamShape']) #,'BeamSize'])
    
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
        
        #~ if verbose:
            #~ print ( "current group:", name )
        #~ elif verbose > 1:
            #~ print ( "parent frame:", grouped )
            
        # invoke new function from Input.py -- initiate tracking object from class
        # use collectInfo to select z data
        #
        tracking = Tracking(frame, verbose)
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
    
    plt.locator_params(axis = 'x', nbins = ticks)

    plt.ylabel("photons/bin")
    plt.xlabel("z [m]")

    plt.legend()
    ax.legend(loc = 'lower center', bbox_to_anchor = (0.5, -0.2), ncol = legCol)
    
    if (Type == 'hit' and save == 1):
        plt.savefig(plotpath + 'SR_hits_beamshape.pdf', bbox_inches = 'tight')
        print ("saved plot as", plotpath, "SR_hits_beamshape.pdf")
    elif (Type == 'position' and save == 1):
        plt.savefig(plotpath + 'SR_position_beamshape.pdf', bbox_inches = 'tight')
        print ("saved plot as", plotpath, "SR_position_beamshape.pdf")
    elif(Type == 'origin' and save == 1):
        plt.savefig(plotpath + 'SR_origin_beamshape.pdf', bbox_inches = 'tight')
        print ("saved plot as", plotpath, "SR_origin_beamshape.pdf")




def plotSrcHits(df, plotpath, elements, zlim = [], nBin = 100, ticks = 5, save = 0, verbose = 0):
    """
    Method to select certain elements as sources and plot hits caused BY THESE elements.
    Requires full element names, no groups implemented yet.
        -- df:      dataframe to do the selection on
        -- name:    list of names, has to be passed as list, even for single element
        -- nBin:    set number of bins/binning level
        -- ticks:   set the number of tickss on the xaxis (acts on binning)
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
    
    plt.locator_params(axis = 'x', nbins = ticks)    
    plt.grid()
    
    plt.legend()
    ax.legend(loc = 'lower center', bbox_to_anchor = (0.5, -0.15), ncol = 4)
    
    plt.ylabel('photons/bin')
    plt.xlabel('z [m]')
    
    if save == 1: 
        print ("Saving figure as ", plotpath, "SR_hitsFrmElmt.pdf")
        plt.savefig(plotpath + "SR_hitsFrmElmt.pdf", bbox_inches = 'tight')



def plot_colEff(df, plotpath, ):
    """
    Method to count the hits +-2m from IP and plot this as fct. of the collimator settings.
        -- df:          dataframe holding collimation data
        -- plotpath:    specify location for saving plots
    """
    
    # first check for right data
    #
    aperList = df.CollDim.unique()
    if aperList == []: raise RuntimeError("No apertures found!")
    else:
        print (" -*-*-*-*-*-*-*-*-*-*-*-*- \n", "List of apertures: ", aperList)
    
def plot_spatialGamDistr(inputFile, plotpath, nBin = 100, save = 0):
    """
    Method to analyze data created by SteppingAction in TestEm16 for collecting detailed information 
    on photons that enter certain volume(s).
        -- input:       file to read the data from. Dedicated frame created
        -- plotpath:    specify location for storage of plots
    """
    # Create local dataframe to store the Geant4 output
    #
    header = ['Energy', 'x', 'y', 'z', 'px/p', 'py/p', 'pz/p']
    scoreFrame = pd.read_table(inputFile, sep = '\t', header = None, names = header)
    
    # count number of entries
    #
    totalGam = scoreFrame.Energy.count()
    print (" ========================================= \n", " total number of entries: ", totalGam, " photons.\n", " ========================================= ")
    
    # plot the energy distribution
    #
    plt.figure( figsize = (12,10) )
    plt.hist(scoreFrame.Energy.tolist(), nBin)
    plt.yscale('log')
    plt.grid()
    plt.xlabel('Energy [keV]')
    plt.ylabel('photons/bin')
    plt.title('Energy Distribution')
    
    # save the plots if desired
    #
    if save: plt.savefig( plotpath + "energyDistr.pdf" )
    
    # plot the spatial information
    #
    plt.figure( figsize = (12, 10) )
    plt.grid()
    plt.hist(scoreFrame.x.tolist(), nBin)
    plt.xlabel('x [m]')
    plt.ylabel('photons/bin')
    plt.title('Horizontal Position at Entrance')
    if save: plt.savefig( plotpath + "gamHor.pdf" )
        
    plt.figure( figsize = (12, 10) )
    plt.grid()
    plt.hist(scoreFrame.y.tolist(), nBin)
    plt.xlabel('y [m]')
    plt.ylabel('photons/bin')
    plt.title('Vertical Position at Entrance')
    if save: plt.savefig( plotpath + "gamVer.pdf" )

    plt.figure( figsize = (12, 10) )
    plt.grid()
    plt.hist(scoreFrame.z.tolist(), nBin)
    plt.xlabel('z [m]')
    plt.ylabel('photons/bin')
    plt.title('Longitudinal Position at Entrance')
    if save: plt.savefig( plotpath + "gamLon.pdf" )
    
    
    
