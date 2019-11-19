import matplotlib.pyplot as plt
from numpy import mean, std, array

from PlotSelectTools import Tracking 
from OpticsSelectTools import DataSelection

# Functions following from here should be put into another class, PlottingData 
#
def plot_defaultData( df, ax, plotpath, beam, size = 'all', Type = 'hit', nBin = 100, ticks = 10, verbose = 0, legCol = 2, save = 0):
    """
    Function to plot data from secondary events, taking into account different beam shapes and sizes. 
    In case of Type = hit allows to plot hits within a certain element. For Type == origin, it plots the origin of all elements or in a single element, if combined with selection in element
        -- dfGrp:       grouped DF object from selction before
        -- plotpath:    point to a directory for storing plots
        -- beam:        allows to select the beam shape. Available are pencil, gauss, flat and ring
        -- size:        choose beam sizes; gauss,flat and ring have to start with >0; defaults to 'all'
        -- Type:        choose which spectrum to plot - hits or origin
        -- nBin:        choose the binnig, defaults to 100
        -- ticks:       set the number of tickss on the xaxis (acts on binning)
        -- verbose:     switch on/off verbose output
        -- legCol:      specify number of columns in the legend box, defaults to 2
        -- save:        select whether or not the plots are dumped to pdf files
    
    RETURNS: nothing. Simple plottig tool
    """

    if Type == 'hit':
        ax.set_title("SR photons hitting beampipe")
        ax.hist( df[df.Material == b'Cu'].z_eu, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(beam), stacked = False)
        if save == 1:
            plt.savefig( plotpath + "SR_hits_beamshape.pdf", bbox_inches = 'tight', dpi = 150 )
            print ('saved plot as', plotpath, 'SR_hits_beamshape.pdf')

    elif Type == 'position':
        ax.set_title("Position of SR photons")
        ax.hist( df.z_eu, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(beam), stacked = False)
        if save == 1:
            plt.savefig( plotpath + "SR_position_beamshape.pdf", bbox_inches = 'tight', dpi = 150 )
            print ('saved plot as', plotpath, 'SR_position_beamshape.pdf')

    elif Type == 'origin':
        ax.set_title("Origin of SR photons")
        ax.hist( df[(df.Process == b'initStep') & (df.Creator==b'SynRad')].z_eu, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(beam), stacked = False) 
        if save == 1:
            plt.savefig( plotpath + "SR_origin_beamshape.pdf", bbox_inches = 'tight', dpi = 150 )
            print ('saved plot as', plotpath, 'SR_origin_beamshape.pdf')

    else:
        raise RuntimeError("Invalid selection of Type!")
    
    return

def plot_Energy(df, ax, plotpath, beam, size = 'all', Type = 'general', magnets = [], nBin = 100, ticks = 10, verbose = 0, legCol = 2, save = 0):
    """
    
    """

    from VisualSpecs import myColors as colors
    
    if Type == 'general':
        ax.hist( df[df.Process == b'initStep'].Egamma*1e6, bins = nBin, histtype = 'step', lw = 2.5, label = str(beam) )
        # title = 'photon energy distribution - ' + str(Type)
    
    elif Type == 'hit':
        
        ax.hist( df[ (df.Creator == b'SynRad') & (df.Material == b'Cu') ].Egamma*1e6, bins = nBin, histtype = 'step', lw = 2.5, label = str(beam) )
    
    else:
        if magnets == []: raise RuntimeError('*** List of magnets empty ...')
        incr = 0
        for magn in magnets:
            ax.hist( df[(df.OrigVol == magn) & (df.Process==b'initStep')].Egamma*1e6, bins = nBin, histtype = 'step', lw = 2.5, label = str(magn), color = colors[incr])
            incr += 1
        # title = 'photon energy distribution - ' + str(Type)

    if (save == 1):
        plt.savefig(plotpath + "SR_energy_spectrum" + str(Type) + ".pdf", bbox_inches = 'tight', dpi = 50 )
        print ('saved plot as', plotpath, 'SR_energy_spectrum' + str(Type) + '.pdf')
    
    return

def plotSrcHits(df, ax, beam, elements, nBin = 100, ticks = 5, save = 0, verbose = 0):
    """
    Method to select certain elements as sources and plot hits caused BY THESE elements.
    Requires full element names, no groups implemented yet.
        -- df:      dataframe to do the selection on
        -- name:    list of names, has to be passed as list, even for single element
        -- nBin:    set number of bins/binning level
        -- ticks:   set the number of ticks on the xaxis (acts on binning)
        -- save:    choose to whether or not save the plot
        -- verbose: switch on/off or set level of verbosity

    RETURNS: the plot
    """

    # plt.figure( figsize = (15,10) )
    # ax = plt.subplot(111)
    # plt.title("Hits from Element(s)")
    # plt.rc('grid', linestyle = '--', color = 'gray')
    
    # check, if elements is not empty
    #
    if elements == []:
        raise RuntimeError("Elements is empty --> no elements to plot!")
        
    # do the actual selection, based on passed elements
    #
    for elem in elements:
        
        if verbose: print('Looking into current element', elem)
        
        selection = df[df.OrigVol == elem]
        if verbose > 1: print( selection )

        ax.hist( selection[ (selection.Material == b'Cu') & (selection.Creator == b'SynRad') ].z_eu, bins = nBin, histtype = 'step', lw = 2.5, fill = False, label = str(elem) )
        
        # if verbose > 1: print (hits.Track)
    
    # plt.locator_params(axis = 'x', nbins = ticks)    
    # plt.grid()
    
    # plt.legend()
    # ax.legend(loc = 'lower center', bbox_to_anchor = (0.5, -0.2), ncol = 6)
    
    # plt.ylabel('photons/bin')
    # plt.xlabel('z [m]')

    return 

def plotPrimTrack( df, plotpath, axis = 'all' ):
    """
    Method to plot the path of primary particles after Geant tracking
        -- df:          dataframe holding primary data
        -- axis:        choose between both or only one transverse coordinate
        -- plotpath:    specify location to dump pdf plots

    RETURNS: nothing. Simple plottig tool
    """
    x_eu = df.x_eu.tolist()
    y_eu = df.y_eu.tolist()
    z_eu = df.z_eu.tolist()

    plt.figure( figsize = (12,10) )
    plt.title('primary particle track')
    plt.grid()
    if axis == 'all':
        plt.plot(z_eu, x_eu, 'r.', label = 'horizontal')
        plt.plot(z_eu, y_eu, 'b.', label = 'vertical')
    elif axis == 'horizontal':
        plt.plot(z_eu, x_eu, 'r.', label = 'horizontal')
    elif axis == 'vertical':
        plt.plot(z_eu, y_eu, 'b.', label = 'vertical')
    plt.xlabel('z [m]')
    plt.ylabel('trnsv. pos. [m]')
    plt.legend()

    return

def plot_colEff(df, plotpath, ):
    """
    Method to count the hits +-2m from IP and plot this as fct. of the collimator settings.
        -- df:          dataframe holding collimation data
        -- plotpath:    specify location for saving plots

    RETURNS: nothing. Simple plottig tool
    """
    
    # first check for right data
    #
    aperList = df.CollDim.unique()
    if aperList == []: raise RuntimeError("No apertures found!")
    else:
        print (" -*-*-*-*-*-*-*-*-*-*-*-*- \n", "List of apertures: ", aperList)

    return

from itertools import cycle
from VisualSpecs import align_yaxis, myColors
def Plot_Bend_Cones(df, ScaleXY, aper = 0, zrange = [], xrange = [], lines = 'both', verbose = 0):
    """
    Function to plot the tangential lines representing SR fans coming from bending magnets in an accelerator
        -- df: dataframe holding the information
        -- ScaleXY: scale factor transverse dimensions for aperture plot
        -- aper: switch aperture plot on/off
        -- zrange: select a certain range in z to plot for (especially for large machines) aka zmin, zmax
        -- xrange: select certain range in x for plotting 
        -- lines: specify which part of the SR fan to plot (entry, exit, both)
        -- verbose: verbosity level
    RETURN: figure object
    """

    # init the plot
    #
    fig = plt.figure( figsize = (20,10) ); ax = fig.add_subplot(111)
    if aper: twin = ax.twinx()

    # check for existance of Euclidean coordinates, slice frame if zmin, zmax given
    #
    if {'x_EU', 'y_EU', 'z_EU'}.issubset( df.columns ) == 0: raise KeyError('x,y,z_EU not found: EU coordinates missing?')
    if zrange != []: 
        print('selection zmin =', zrange[0], 'zmax =', zrange[1], 'm')
        df = df[ (df.z_EU > zrange[0]) & (df.z_EU < zrange[1]) & (df.x_EU > xrange[0]) & (df.x_EU < xrange[1]) ]
        df = df.reset_index()
        ax.set_xlim( zrange[0] - 10, zrange[1] + 10 )

    # plot the reference path
    #
    ax.plot( df.z_EU, df.x_EU*ScaleXY, color = myColors[11], ls = '--', lw = 3.)

    # store first vectors for intial iteration
    #
    tang = [array([0,0,1])]
    VEU = [array([0,0,0])]

    for i in range(df.index.min() + 1, df.index.max() + 1 ):

        dirCS = array( [df.loc[i,'PX'], df.loc[i,'PY'], df.loc[i,'PS']] )
        veu = array([df.loc[i,'x_EU'], df.loc[i,'y_EU'], df.loc[i,'z_EU']])
        tan = df.loc[i,'W'] @ dirCS
        
        VEU.append( veu )
        tang.append( tan ) 

        if 'BEND' in df.loc[i, 'KEYWORD']: 
            if verbose: print('found bend', df.loc[i, 'NAME'], 'at integer', i)

            # 2nd step: plot single elements
            #
            x1 = df.at[i, 'z_EU']; x2 = df.at[i-1, 'z_EU']
            y1 = df.at[i, 'x_EU']*ScaleXY; y2 = df.at[i-1, 'x_EU']*ScaleXY

            ax.plot( [x1,x2], [y1,y2], ls = '-', lw = 5.5) 

            if aper:
                ap1 = df.at[i, 'APER']*ScaleXY; ap2 = df.at[i-1, 'APER']*ScaleXY
                ax.plot( [x1,x2], [y1+ap1,y2+ap2], [x1, x2], [y1-ap1,y2-ap2], ls = '-', lw = 2.5, color = myColors[11])

            ax.text((x1+x2)/2, (y1 + y2)/2, df.loc[i,'NAME'], fontsize = 18 )
            
            # 3rd step: determine the tangent on the bend (entry/exit)
            #
            start = VEU[i-1] + tang[i-1]
            end = veu + tan
            
            len_s = 1; len_e = 1
            if abs(end[2]) < abs(veu[2]):
                len_s = abs(VEU[i-1][2]/(start[2] - VEU[i-1][2]))
                len_e = abs(veu[2]/(end[2] - veu[2]))
                
            start = VEU[i-1] + len_s*tang[i-1]
            end = veu + len_e*tan
            
            # 4th step: add tangents as lines to the plot 
            #
            Exit = line([veu[2], end[2]], [veu[0]*ScaleXY, end[0]*ScaleXY], lw = 2.5, ls = '-', color = 'green') 
            Start = line([VEU[i-1][2], start[2]], [VEU[i-1][0]*ScaleXY, start[0]*ScaleXY], lw = 2.5, ls = '-', color = 'red')
            
            if lines == 'entry': ax.add_line(Start)
            elif lines == 'exit': ax.add_line(Exit)
            elif lines == 'both': ax.add_line(Start); ax.add_line(Exit)
            else: raise KeyError('Select which lines to plot.')

            if verbose:
                print(i,df.loc[i-1, 'NAME'],'line from (', VEU[i-1][0], VEU[i-1][2], ') to (', start[0], start[2], ') \n',
                i,df.loc[i, 'NAME'],'line from (', veu[0], veu[2], ') to (', end[0], end[2], ') \n --------------------------- ')


    ax.set_xlabel('Z [m]'); ax.set_ylabel('X [m]')
    if xrange != []: ax.set_ylim( xrange[0], xrange[1] )

    if aper:
        twin.plot( df[df.rel_S > -100].rel_S, df[df.rel_S > -100].APER*ScaleXY, color = myColors[11], lw = 2.5 )
        twin.plot( df[df.rel_S > -100].rel_S, -df[df.rel_S > -100].APER*ScaleXY, color = myColors[11], lw = 2.5 )
        twin.set_ylabel('aperture [m]')                                               
        
        if xrange != []: twin.set_ylim( xrange[0], xrange[1] )
        align_yaxis(ax, 0, twin, 0)

    plt.title('synchrotron radiation fans (dipoles)')
    plt.tight_layout()  
        
    return fig
