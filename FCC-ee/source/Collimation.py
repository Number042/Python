import uproot
from matplotlib import pyplot as plt
from os.path import isfile, isdir
from Plot import matCodes

class SRMasks:

    def __init__( self, ntuples, plotpath = '/tmp/', verbose = 0 ):

        """
        Class to study effects of synchrotron radiation on mitigation elements, mainly masks and collimators.
        """

        self.ntuples = ntuples
        if len( self.ntuples ) == 0: raise RuntimeError( "*** list of datafiles is empty!" )
        
        for ntuple in self.ntuples:
            if isfile( ntuple ): pass
            else: raise FileNotFoundError("Ntuple", ntuple, "doesn't exist!")

        if isdir( plotpath ): pass
        else: raise FileNotFoundError("plotpath", plotpath, "doesn't exist!")
        self.verbose = verbose
        self.plotpath = plotpath

    # currently as private. Could also be made publicly available to create selected DFs
    #
    def __readData( self, ntuple ):

        """
        Provide ntuple as DataFrame
            -- columns:     specify required data
            -- COL:         array for horizontal and vertical coll opening (COLH,COLV)
            -- optics:      optional key to distinguish different machine versions
        """

        thefile = uproot.open( ntuple )
        df = thefile['seco_ntuple;1'].pandas.df( ['Creator', 'Material', 'Name', 'Egamma', 'x_eu', 'y_eu', 'z_eu'] )
        
        
        hits = df[ (df.Creator == 1) & (df.Material.isin(matCodes)) & (df.Material.shift(1) == 1) ]
        
        return hits


    def SRmasks( self, Type = 'transverse', nbin = 100 ):

        selection = []
        for tuple in self.ntuples:

            df = self.__readData( tuple )
        
            mskQC1L1 = df[ ((df.Name == b'MASKQC1L1_2') | (df.Name == b'DRIFT_8632')) ]; mskQC1L1.name = 'MASKQC1L1'
            mskQC2L1 = df[ ((df.Name == b'MASKQC2L1_2') | (df.Name == b'DRIFT_8626')) ]; mskQC2L1.name = 'MASKQC2L1'
            mskQC1R1 = df[ ((df.Name == b'MASKQC1R1_2') | (df.Name == b'DRIFT_1')) ]; mskQC1R1.name = 'MASKQC1R1' 
            mskQC2R1 = df[ ((df.Name == b'MASKQC2R1_2') | (df.Name == b'DRIFT_7')) ]; mskQC2R1.name = 'MASKQC2R1'

            selection = [mskQC2L1, mskQC1L1, mskQC1R1, mskQC2R1]
            del df

        plt.figure()
        if Type == 'transverse':                
            
            for mask in selection:
                print( 'Looking at', mask.name )
                print( mask.Egamma.count(), 'hits on', mask.name, 'with mean energy', mask.Egamma.mean()*1e6, 'keV')
            #     print( grp.Egamma.mean() )
                plt.plot( mask.x_eu, mask.y_eu, marker = '.', ls = '', label = '%s' %mask.name)
        
        if Type == 'hitsDistr':

            for mask in selection:
                plt.hist( mask.z_eu, bins = nbin, histtype = 'step', lw = 2 )
        
        # for mask in selection:
        #     plt.hist( mask[mask.Egamma != 0].Egamma*1e6, bins = 100, histtype = 'step' )
            plt.legend()

        return 0