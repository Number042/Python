import matplotlib.pyplot as plt
from numpy import mean, std, array

from PlotSelectTools import Tracking 
from OpticsSelectTools import DataSelection

matCodes = [2,3,4,5]

# verbose output for materials in the analysis
#
def printMats(materials):

    # material codes: "Vacuum" 1, Cu" 2, "W" 3, "Gold" 4, "Be" 5
    #
    print('checking materials present in the set:')
    for code in materials:
        if code == 2: print('found copper')
        if code == 3: print('found tungsten')
        if code == 4: print('found gold')
        if code == 5: print('found beryllium')

# Functions following from here should be put into another class, PlottingData 
#
def plot_defaultData( df, ax, plotpath, beam, collSet, size = 'all', Type = 'hit', nBin = 100, ticks = 10, verbose = 0, legCol = 2, save = 0):
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

    if verbose > 1: printMats( df.Material.unique() )

    theLabel = str( beam + '_' + size + '_' + collSet )

    if Type == 'hit':    
        ax.set_title("SR photons hitting beampipe")
        selection = df[ (df.Creator == 1) & (df.Material.isin(matCodes)) & (df.Material.shift(1) == 1) ]
        print(' --- # of entries:', selection.z_eu.count() )        

        # ax.hist( df[df.Material == 2].z_eu, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(beam), stacked = False)
        ax.hist( selection.z_eu, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = theLabel, stacked = False)

    elif Type == 'position':
        ax.set_title("Position of SR photons")
        print(' --- # of entries:', df.z_eu.count() )        
        ax.hist( df.z_eu, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = theLabel, stacked = False)

    elif Type == 'origin':
        ax.set_title("Origin of SR photons")
        selection = df[(df.Process == 0) & (df.Creator == 1 )]
        print(' --- # of entries:', selection.z_eu.count() )        
        
        ax.hist( selection.z_eu, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = theLabel, stacked = False) 
    
    else:
        raise RuntimeError("Invalid selection of Type!")
    
    ax.axvspan(-10, 10, alpha = 0.15, color = 'lightsteelblue') 
    del df

    return

def plot_Energy(df, ax, plotpath, beam, collSet, size = 'all', nBin = 100, xlim = [], Type = 'general', magnets = [], ticks = 10, verbose = 0, legCol = 2, save = 0):
    """
    
    """

    from VisualSpecs import myColors as colors
    from numpy import select
    
    if Type == 'general':
        ax.hist( df[df.Process == 0].Egamma*1e6, bins = nBin, histtype = 'step', lw = 2.5, label = str( beam + '_' + collSet ) )
        # title = 'photon energy distribution - ' + str(Type)
    
    elif Type == 'hit':
        if verbose > 1: printMats( df.Material.unique() )
        ax.hist( df[ (df.Creator == 1) & (df.Material.isin(matCodes)) & (df.Material.shift(1) == 1) ].Egamma*1e6, bins = nBin, histtype = 'step', lw = 2.5, label = str( beam + '_' + collSet ) )

    elif Type == 'bendVsQuad':
        df['Keyword'] = select([df.OrigVol.str.contains('B'), df.OrigVol.str.contains('QC'), df.OrigVol.str.contains('SOL')], ['BEND','QUAD','SOLENOID'], default = 'other')
        df = df[df.Process == 0]

        for key in ['BEND','QUAD']:
            ax.hist( df[ df.Keyword == key ].Egamma*1e6, bins = nBin, histtype = 'step', lw = 2.5, label = str(key) )
    
    elif Type == 'Solenoid':
        
        if magnets == []:
            df['Keyword'] = select( [df.OrigVol.str.contains('B'), df.OrigVol.str.contains('QC'), df.OrigVol.str.contains('SOL')], ['BEND','QUAD','SOLENOID'], default = 'other' )
            df = df[(df.Process == 0) & (df.Keyword == 'SOLENOID') ]

            ax.hist(df.Egamma*1e6, bins = nBin, histtype = 'step', lw = 2.5, label = str('solenoid'))
        else:
            incr = 0
            for magn in magnets:
                ax.hist( df[(df.OrigVol == magn) & (df.Process == 0)].Egamma*1e6, bins = nBin, histtype = 'step', lw = 2.5, label = str(magn), color = colors[incr])
                incr += 1
    else:
        if magnets == []: raise RuntimeError('*** List of magnets empty ...')
        incr = 0
        for magn in magnets:
            ax.hist( df[(df.OrigVol == magn) & (df.Process == 0)].Egamma*1e6, bins = nBin, histtype = 'step', lw = 2.5, label = str(magn), color = colors[incr])
            incr += 1
        # title = 'photon energy distribution - ' + str(Type)
    if xlim:
        ax.set_xlim( xlim[0], xlim[1] )
    
    del df
    return

def plotSrcHits(df, ax, beam, collSet, elements, nBin = 100, ticks = 5, save = 0, verbose = 0):
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

        ax.hist( selection[ (selection.Material.isin(matCodes)) & (selection.Creator == 1) & (selection.Material.shift(1) == 1) ].z_eu, bins = nBin, histtype = 'step', lw = 2.5, fill = False, label = str(elem) )

        # if verbose > 1: print (hits.Track)
    
    ax.axvspan(-10, 10, alpha = 0.15, color = 'lightsteelblue')     
    del df
    
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

def plotColEff( grp, ax, logscale, save, verbose, plotpath = '/tmp/' ):
    """
    Method to visualize data on collimation efficiency stored in an external DF
        -- df: data source
        -- logscale: choose whether or not a log scale is applied to enhance details
        -- save: choose whether or not to save the plot

    RETURNS: nothing. Simple plottig tool
    """
        
    color = 'tab:blue'

    newax = ax.twiny()

    newax.set_frame_on(True)
    newax.patch.set_visible(False)
    newax.xaxis.set_ticks_position('bottom')
    newax.xaxis.set_label_position('bottom')
    newax.spines['bottom'].set_position(('outward', 80))

    ax.plot( grp['setting'], grp['rateQC2L'], 'r--', label = 'MSK.QC2L1' )
    newax.plot( grp['sigma'], grp['rateQC1L'], 'b--', label = 'MSK.QC1L1' )
    newax.plot( grp['sigma'], grp['rateCntrChm'], 'g--', label = 'central Chamber')

    ax.set_xlabel('half opening [mm]', color = color )
    ax.set_ylabel('$\\gamma\'s$/bunch')
    
    ax.tick_params(axis = 'x', colors = color )
    newax.set_xlabel('half opening [$\\sigma$]', color = color )
    newax.tick_params(axis = 'x', colors = color )
    
    if logscale:
        ax.set_yscale('log')
        newax.set_yscale('log')
        
def PlotBendCones(df, ScaleXY, aper = 0, zrange = [], xrange = [], tangents = 'both', verbose = 0):
    """
    Function to plot the tangential lines representing SR fans coming from bending magnets in an accelerator
        -- df: dataframe holding the information
        -- ScaleXY: scale factor transverse dimensions for aperture plot
        -- aper: switch aperture plot on/off
        -- zrange: select a certain range in z to plot for (especially for large machines) aka zmin, zmax
        -- xrange: select certain range in x for plotting 
        -- tangents: specify which part of the SR fan to plot (entry, exit, both), defaults to none
        -- verbose: verbosity level
    RETURN: figure object
    """
    from itertools import cycle
    from VisualSpecs import align_yaxis, myColors
    import matplotlib.lines as lines

    # init the plot
    #
    fig = plt.figure( figsize = (20,10) ); ax = fig.add_subplot(111)
    if aper: twin = ax.twinx()

    # check for existance of Euclidean coordinates, slice frame if zmin, zmax given
    #
    if {'x_EU', 'y_EU', 'z_EU'}.issubset( df.columns ) == 0: raise KeyError('x,y,z_EU not found: EU coordinates missing?')
    if zrange != []: 
        if zrange[0] < 0 and zrange[1] > 0: raise Warning(" *** no overlapping zrange: better choose either <= 0 or >= 0" )
        print('selection zmin =', zrange[0], 'zmax =', zrange[1], 'm')
        df = df[ (df.z_EU > zrange[0]) & (df.z_EU < zrange[1]) & (df.x_EU > xrange[0]) & (df.x_EU < xrange[1]) ]
        df = df.reset_index()
        ax.set_xlim( zrange[0] - 10, zrange[1] + 10 )

    # plot the reference path
    #
    ax.plot( df.z_EU, df.x_EU*ScaleXY, color = myColors[10], ls = '--', lw = 3.)

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
                ax.plot( [x1,x2], [y1+ap1,y2+ap2], [x1, x2], [y1-ap1,y2-ap2], ls = '-', lw = 2.5, color = myColors[10])

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
            Exit = lines.Line2D([veu[2], end[2]], [veu[0]*ScaleXY, end[0]*ScaleXY], lw = 2.5, ls = '-', color = 'green') 
            Start = lines.Line2D([VEU[i-1][2], start[2]], [VEU[i-1][0]*ScaleXY, start[0]*ScaleXY], lw = 2.5, ls = '-', color = 'red')
            
            if tangents == 'entry': ax.add_line(Start)
            elif tangents == 'exit': ax.add_line(Exit)
            elif tangents == 'both': ax.add_line(Start); ax.add_line(Exit)
            else: pass 

            if verbose:
                print(i,df.loc[i-1, 'NAME'],'line from (', VEU[i-1][0], VEU[i-1][2], ') to (', start[0], start[2], ') \n',
                i,df.loc[i, 'NAME'],'line from (', veu[0], veu[2], ') to (', end[0], end[2], ') \n --------------------------- ')


    ax.set_xlabel('Z [m]'); ax.set_ylabel('X [m]')
    if xrange != []: ax.set_ylim( xrange[0], xrange[1] )

    if aper:
        twin.plot( df[df.rel_S > -100].rel_S, df[df.rel_S > -100].APER*ScaleXY, color = myColors[10], lw = 2.5 )
        twin.plot( df[df.rel_S > -100].rel_S, -df[df.rel_S > -100].APER*ScaleXY, color = myColors[10], lw = 2.5 )
        twin.set_ylabel('aperture [m]')                                               
        
        if xrange != []: twin.set_ylim( xrange[0], xrange[1] )
        align_yaxis(ax, 0, twin, 0)

    plt.title('synchrotron radiation fans (dipoles)')
    plt.tight_layout()  
        
    return fig