import matplotlib.pyplot as plt
from numpy import mean, std

from PlotSelectTools import Tracking 
from OpticsSelectTools import DataSelection

# Functions following from here should be put into another class, PlottingData 
#
def plot_diffApers(df, plotpath, selection = 'SR', Type = 'hit', aperture = 'all', verbose = 0, zlim = [], nBin = 100, ticks = 10, legCol = 2, save = 0):
            
    """
    This is a function to plot selected collimation data and gives the option to select only certain or all dimensions. Dimensions refer to the collimator opening.
        -- df:       dataframe that holds data to plot ==> ATTENTION:  df requires a name given to it: in case of collimation, name must contain 'col', 
        -- Type:        specify which data to be plotted: 'hits' or 'origin'; defaults to 'hits'
        -- aperture:    defaults to 'all' but allows selecting only certain apertures
        -- verbose:     additional output
        -- zlim:        allows tp plot only certain z range, defaults to empty list
        -- nBin:        specify number of bins; defaults to 100
        -- ticks:       refine the tick frequenc if necessary
        -- legCol:      specify number of columns in the legend box, defaults to 2
        -- save:        choose whether or not the plots are dumped as pdf
        
    RETURNS: nothing. Simple plottig tool
    """
    # prepare data selection
    #
    dataSel = Tracking( verbose )
    
    # settings for the plot
    #
    plt.figure( figsize = (15,10) )
    ax = plt.subplot(111)
    plt.rc('grid', linestyle = "--", color = 'grey')
    plt.grid()
    if zlim: plt.xlim( zlim[0], zlim[1] )         # allows to set the xlim

    for aper, subframe in df:
    
        if verbose:
            print( "current group:", aper )
        elif verbose > 1:
            print( "parent frame:", subframe )

        Z_pos, Z_org, Z_hit, E_org, E_hit = dataSel.collectInfo( subframe )
        
        count = sum( 1 for x in Z_hit if (x > -2) & (x < 2) )
        print ("Sum of hits in L*:", count)

        # plot resulting data
        #
        if Type == 'hit':
            plt.title("SR photons hitting beampipe")
            plt.hist(Z_hit, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(name), stacked = False) 
        elif Type == 'position':
            plt.title("Position of SR photons")
            plt.hist(Z_pos, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(name), stacked = False) 
        elif Type == 'origin':
            plt.title("Origin of SR photons")
            plt.hist(Z_org, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(name), stacked = False) 
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
    
    return

def plot_defaultData(dfGrp, plotpath, zlim = [], beam = 'all', size = 'all', Type = 'hit', nBin = 100, ticks = 10, verbose = 0, legCol = 2, save = 0):
    """
    Function to plot data from secondary events, taking into account different beam shapes and sizes. 
    In case of Type = hit allows to plot hits within a certain element. For Type == origin, it plots the origin of all elements or in a single element, if combined with selection in element
        -- dfGrp:       grouped DF object from selction before
        -- plotpath:    point to a directory for storing plots
        -- zlim:		array to put zmin and zmax; allows to plot only certain region; default empty 
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
    # prepare data selection
    dataSel = Tracking( verbose )

    # settings for the plot
    #
    plt.figure(figsize = (15,10))
    ax = plt.subplot(111)
    plt.rc('grid', linestyle = "--", color = 'grey')
    plt.grid()
    if zlim: plt.xlim(zlim[0], zlim[1])         # allows to set the xlim

    for name, subframe in dfGrp:
    
        if verbose:
            print ( "current group:", name )
        elif verbose > 1:
            print ( "parent frame:", dfGrp )
            
        # invoke new function from Input.py -- initiate tracking object from class
        # use collectInfo to select z data
        #
        Z_pos, Z_org, Z_hit, E_org, E_hit = dataSel.collectInfo( subframe )
        
        # plot resulting data
        #
        if Type == 'hit':
            plt.title("SR photons hitting beampipe")
            plt.hist(Z_hit, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(name), stacked = False)
        elif Type == 'position':
            plt.title("Position of SR photons")
            plt.hist(Z_pos, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(name), stacked = False)
        elif Type == 'origin':
            plt.title("Origin of SR photons")
            plt.hist(Z_org, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(name), stacked = False) 
        else:
            raise RuntimeError("Invalid selection of Type!")
    
    plt.locator_params(axis = 'x', nbins = ticks)
    plt.ylabel("photons/bin")
    plt.xlabel("z [m]")

    plt.legend()
    ax.legend(loc = 'upper center', bbox_to_anchor = (0.5, -0.1), ncol = legCol)
    
    if (Type == 'hit' and save == 1):
        plt.savefig(plotpath + "SR_hits_beamshape.pdf", bbox_inches = 'tight', dpi = 150 )
        print ('saved plot as', plotpath, 'SR_hits_beamshape.pdf')
    elif (Type == 'position' and save == 1):
        plt.savefig(plotpath + "SR_position_beamshape.pdf", bbox_inches = 'tight', dpi = 150 )
        print ('saved plot as', plotpath, 'SR_position_beamshape.pdf')
    elif(Type == 'origin' and save == 1):
        plt.savefig(plotpath + "SR_origin_beamshape.pdf", bbox_inches = 'tight', dpi = 150 )
        print ('saved plot as', plotpath, 'SR_origin_beamshape.pdf')
    
    return

def plot_Energy(dfGrp, plotpath, beam = 'all', size = 'all', Type = 'spectrum', nBin = 100, ticks = 10, verbose = 0, legCol = 2, save = 0):
    """
    
    """

    # check for existence of the data
    #
    # prepare data selection
    dataSel = Tracking( verbose )

    # settings for the plot
    #
    plt.figure(figsize = (15,10))
    ax = plt.subplot(111)
    plt.rc('grid', linestyle = "--", color = 'grey')
    plt.grid()
    
    for name, subframe in dfGrp:
    
        if verbose:
            print ( "current group:", name )
        elif verbose > 1:
            print ( "parent frame:", dfGrp )
            
        # invoke new function from Input.py -- initiate tracking object from class
        # use collectInfo to select z data
        #
        Z_pos, Z_org, Z_hit, E_org, E_hit = dataSel.collectInfo( subframe )
        E_mean = mean(E_org); E_std = std(E_org)
    
        # plot resulting data
        #
        if Type == 'spectrum':
            plt.title("SR photons hitting beampipe")
            plt.hist(E_org, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(name), stacked = False)
            plt.yscale( 'log' )
        elif Type == 'distribution':
            print('Number of entries (E_org) =', len(E_org), 'in', name, '\n'
                'Mean energy =', E_mean, 'keV \n'
                'std deviation =', E_std, '\n'
                ' ---------------------------------- ' )
            plt.title('photon energy distribution')
            plt.hist(E_org, bins = nBin, histtype = 'step', normed = True, fill = False, linewidth = 1.5, label = str(name), stacked = False)
        else:
            raise RuntimeError("Invalid selection of Type!")

    plt.locator_params(axis = 'x', nbins = ticks)
    plt.xlabel( 'Energy [keV]' )
    plt.ylabel( 'photons/bin' )
    plt.title( 'Energy distribution' )
    plt.axvline( x = 100, lw = 2, ls = '--', color = 'red' )
    plt.legend()
    ax.legend(loc = 'upper center', bbox_to_anchor = (0.5, -0.1), ncol = legCol)

    if (Type == 'spectrum' and save == 1):
        plt.savefig(plotpath + "SR_energy_spectrum.pdf", bbox_inches = 'tight', dpi = 150 )
        print ('saved plot as', plotpath, 'SR_energy_spectrum.pdf')
    else: pass

    return

def plotSrcHits(df, plotpath, elements, zlim = [],  nBin = 100, ticks = 5, save = 0, verbose = 0):
    """
    Method to select certain elements as sources and plot hits caused BY THESE elements.
    Requires full element names, no groups implemented yet.
        -- df:      dataframe to do the selection on
        -- name:    list of names, has to be passed as list, even for single element
        -- nBin:    set number of bins/binning level
        -- ticks:   set the number of ticks on the xaxis (acts on binning)
        -- save:    choose to whether or not save the plot
        -- verbose: switch on/off or set level of verbosity

    RETURNS: nothing. Simple plottig tool
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
    
        plt.hist(zpos, bins = nBin, histtype = 'step', linewidth = 2, fill = False, label = str(elem))
        
        if verbose > 1: print (hits.Track)
    
    plt.locator_params(axis = 'x', nbins = ticks)    
    plt.grid()
    
    plt.legend()
    ax.legend(loc = 'lower center', bbox_to_anchor = (0.5, -0.2), ncol = 6)
    
    plt.ylabel('photons/bin')
    plt.xlabel('z [m]')
    
    if save == 1: 
        print ("Saving figure as ", plotpath, "SR_hitsFrmElmt.pdf")
        plt.savefig(plotpath + "SR_hitsFrmElmt.pdf", bbox_inches = 'tight')

    return

def plotPrimTrack( df, plotpath, axis = 'all' ):
    """
    Method to plot the ppath of primary particles after Geant tracking
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
from VisualSpecs import align_yaxis
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
    ax.plot( df.z_EU, df.x_EU*ScaleXY, color = colors[11], ls = '--', lw = 3.)

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
                ax.plot( [x1,x2], [y1+ap1,y2+ap2], [x1, x2], [y1-ap1,y2-ap2], ls = '-', lw = 2.5, color = colors[11])

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
        twin.plot( df[df.rel_S > -100].rel_S, df[df.rel_S > -100].APER*ScaleXY, color = colors[11], lw = 2.5 )
        twin.plot( df[df.rel_S > -100].rel_S, -df[df.rel_S > -100].APER*ScaleXY, color = colors[11], lw = 2.5 )
        twin.set_ylabel('aperture [m]')                                               
        
        if xrange != []: twin.set_ylim( xrange[0], xrange[1] )
        align_yaxis(ax, 0, twin, 0)

    plt.title('synchrotron radiation fans (dipoles)')
    plt.tight_layout()  
        
    return fig
