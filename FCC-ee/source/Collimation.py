import uproot
from matplotlib import pyplot as plt
from os.path import isfile, isdir
from scipy.constants import elementary_charge as e
from Plot import matCodes
from Scatter import Scattering

class SRMasks:

    def __init__( self, Np, N_MC, tau_BSP, ntuples = [], plotpath = '/tmp/', verbose = 0 ):

        """
        Class to study effects of synchrotron radiation on mitigation elements, mainly masks and collimators.
        """

        self.ntuples = ntuples
        if len( self.ntuples ) == 0: raise Warning( "*** list of datafiles is empty!" )
        
        for ntuple in self.ntuples:
            if isfile( ntuple ): pass
            else: raise FileNotFoundError("Ntuple", ntuple, "doesn't exist!")

        if isdir( plotpath ): pass
        else: raise FileNotFoundError("plotpath", plotpath, "doesn't exist!")

        self.verbose = verbose
        self.plotpath = plotpath

        self.Np = Np
        self.N_MC = N_MC
        self.tau_BSP = tau_BSP

    # currently as private. Could also be made publicly available to create selected DFs
    #
    def __readData( self, select ):

        """
        Provide ntuple as DataFrame
            -- columns:     specify required data
            -- COL:         array for horizontal and vertical coll opening (COLH,COLV)
            -- optics:      optional key to distinguish different machine versions
        """

        for theTuple in self.ntuples:

            thefile = uproot.open( theTuple )
            df = thefile['seco_ntuple;1'].pandas.df( ['Creator', 'Material', 'Process', 'Name', 'Egamma', 'x_eu', 'y_eu', 'z_eu', 'trackLen'] )
            df['Name'] = [ name.decode("utf-8") for name in df.Name ]
            # df['OrigVol'] = [ origvol.decode("utf-8") for origvol in df.OrigVol ]

            if select == 'hit': condition = (df.Creator == 1) & (df.Material.isin(matCodes)) & (df.Material.shift(1) == 1)
            
            if select == 'scatter': 
                procs = [3,4]
                condition = ( df.Process.isin(procs)) & (df.Material.shift(1) == 1) & (df.Material.shift(-2) == 1) & (df.Name.shift(-2).str.contains("_v") )
                # condition = (df.Creator != 1) & (df.Material.isin(matCodes)) & (df.Material.shift(1) != 1) & (df.Material.shift(-1) == 1)

            df = df[ condition ]
            if df.empty: raise ValueError('Empty Dataframe!')

            mskQC1L1 = df[ ((df.Name == 'MASKQC1L1_2') | (df.Name == 'DRIFT_8630')) ]; mskQC1L1.name = 'MSK.QC1L1'
            mskQC2L1 = df[ ((df.Name == 'MASKQC2L1_2') | (df.Name == 'DRIFT_8624')) ]; mskQC2L1.name = 'MSK.QC2L1'
            mskQC1R1 = df[ ((df.Name == 'MASKQC1R1_2') | (df.Name == 'DRIFT_1')) ]; mskQC1R1.name = 'MSK.QC1R1' 
            mskQC2R1 = df[ ((df.Name == 'MASKQC2R1_2') | (df.Name == 'DRIFT_7')) ]; mskQC2R1.name = 'MSK.QC2R1'

            selection = [mskQC2L1, mskQC1L1, mskQC1R1, mskQC2R1]

            frac = self.Np/self.N_MC
            print( 'fraction of particles =', frac )

            for mask in selection: 
                count = mask.Egamma.count()
                P_SR = count*frac*mask.Egamma.mean()*1e9*e/(self.tau_BSP*1e-9)

                print( count, 'hits on', mask.name, 'with mean energy', mask.Egamma.mean()*1e6, 'keV \n resulting in P_SR', P_SR, 'W \n extrapolated on whole bunch:', count*frac, 'hits on', mask.name, '\n ------------------------------ \n')
                
            del df
        
        return selection


    def SRmasks( self, Type = 'transverse', xrange = [], nbin = 100, save = 0 ):

        selection = self.__readData('hit')
        
        plt.figure( figsize = (12,10) )
        if Type == 'transverse':                
            
            for mask in selection:
                plt.plot( mask.x_eu, mask.y_eu, marker = '.', ls = '', label = '%s' %mask.name )

            plt.xlabel('horizontal position [m]')
            plt.ylabel('vertical position [m]')
            plt.title('hits on the masks (transverse)')
            pltname = "mask_hitsTrnsv.pdf"

        if Type == 'longitudinal':                
            
            for mask in selection:
                print( 'Looking at', mask.name )
                plt.plot( mask.z_eu, mask.y_eu, marker = '.', ls = '', label = '%s' %mask.name )
            
            if xrange: plt.xlim( xrange[0], xrange[1] )

            plt.xlabel('longitudinal position [m]')
            plt.ylabel('vertical position [m]')
            plt.title('hits on the mask (longitudinal)')
            pltname = "mask_hitsLngt.pdf"

        if Type == 'hitsDistr':

            for mask in selection:
                plt.hist( mask.z_eu, bins = nbin, histtype = 'step', lw = 2, label = '%s' %mask.name )
                print( mask.z_eu.count(), 'hits on', mask.name )
                
        # for mask in selection:
        #     plt.hist( mask[mask.Egamma != 0].Egamma*1e6, bins = 100, histtype = 'step' )
            pltname = "mask_hitsAlongZ.pdf"

        if Type == 'energy':
            
            # mark a 100 keV
            plt.axvline(x = 100, lw = 2.5, ls = '--', color = 'red')

            for mask in selection:
                plt.hist( mask.Egamma*1e6, bins = nbin, histtype = 'step', lw = 2, label = '%s' %mask.name )
                plt.yscale('log')
                plt.title('energy of photons striking the mask')
                plt.xlabel('E$_\\gamma$ [keV]'); plt.ylabel('photons/bin')

            pltname = "mask_hitsEnergy.pdf"
        
        plt.legend()
        
        if save == 1:
            plt.savefig( self.plotpath + pltname, bbox_inches = 'tight', dpi = 75 )
            print ( 'saved plot as', self.plotpath, pltname )

        if self.verbose: print( 'processed data, deleting DF ...' )
        del selection
        
        return 0


    def FwdScatter( self, save = 0, xlim = [] ):
        
        selection = self.__readData('scatter')
        if self.verbose: 
            for mask in selection:
                print( 'Constructed DF', mask.head() )
        for mask in selection:
            
            Scattering().scatterGlobal( df = mask, xlim = xlim )

        return 0

    
    def efficiency( self, extdf, logscale, save, xlim = [], Type = 'collEff' ):
        """
        Number of photons at masks location as function of collimator closure
        Method to count the hits +-2m from IP and plot this as fct. of the collimator settings.
            -- extdf: DF containing the number of photons at the masks for different scenario
        """
        
        if Type == 'collEff':
            from Plot import plotColEff
        
            plotColEff( extdf, logscale, save, self.verbose, plotpath = self.plotpath )
        
        else:

            from scipy.constants import speed_of_light as c 
            selection = self.__readData('hit')

            # set up one figure to hold all plots (compare diff masks directly)
            #
            fig, ax = plt.subplots( figsize = (16, 9))
            newax = ax.twiny()
            fig.subplots_adjust( bottom = 0.1 )

            newax.set_frame_on(True)
            newax.patch.set_visible(False)
            newax.xaxis.set_ticks_position('bottom')
            newax.xaxis.set_label_position('bottom')
            newax.spines['bottom'].set_position(('outward', 80))

            # iterate through masks
            #
            for mask in selection:
                ax.hist( mask.trackLen, bins = 100, histtype = 'step', lw = 2.5, fill = False, label = mask.name )
                newax.hist( mask.trackLen/c*1e9, bins = 100, histtype = 'step', lw = 2.5, fill = False )

            ax.set_xlabel('track length [m]')
            ax.set_ylabel('$\\gamma\'s$/bin')
            newax.set_xlabel('arrival time [ns]')
            
            if xlim:
                ax.set_xlim( xlim[0], xlim[1] )
                newax.set_xlim( xlim[0]/c*1e9, xlim[1]/c*1e9 )
                
            if logscale: 
                ax.set_yscale('log')
                newax.set_yscale('log')
            
            fig.legend( loc = "upper right", bbox_to_anchor = (1,1), bbox_transform = ax.transAxes )
        
            



        