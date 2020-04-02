import matplotlib.pyplot as plt
import VisualSpecs
class Processes:
    """
    Class to do the analysis regarding photon interaction with matter. This is meant to investigate what
    happens with the synchrotron radiation that impacts on the beam pipe wall. 
    """
    
    def __init__( self, df, plotpath, save = 0, verbose = 0 ):
        self.df = df
        self.save = save
        self.verbose = verbose
        self.plotpath = plotpath

    def prepData( self, cols = ['x_eu', 'y_eu', 'z_eu', 'ptot', 'mass', 'charge', 'ProcName', 'Material', 'Creator'] ):
        
        """
        Function to read general twiss files.
            -- relS:    choose if another column with relative S position is added (IP in the center)
            -- verbose: choose verbosity level
        """

        # clean the frame to increase efficiency
        #
        self.df = self.df[cols]
        if self.verbose:
            print( "Processes:", self.df.ProcName.unique(), '\n Creators:', self.df.Creator.unique() )

        #return self.df


    def showerDistr( self, process = 'all', figSize = [15,10] ):
        
        """
        Method to plot a distribution of all processes taking place along the G4 tracklength
            -- process: selection of single processes possible
        """
        
        graph = plt.figure( figsize = (figSize[0], figSize[1]) )
        plt.title('EM showers - photon interaction with matter')
        plt.xlabel('z [m]'); plt.ylabel('entries/bin')

        crtrs = self.df[(self.df.charge == -1) & (self.df.ProcName == 'initStep') ].groupby(['Creator'])
        
        for crtr, subframe in crtrs:
            org = subframe.z_eu.tolist()
            plt.hist(org, bins = 200, stacked = False, histtype = 'step', lw = 2.5, fill = False, label = '%s' %crtr)
                
        plt.legend(); plt.grid()
        
        if self.save: 
            print ("Saving figure as ", self.plotpath, "particlesEMShowerHit.pdf")
            plt.savefig( self.plotpath + "particlesEMShowerHit.pdf", bbox_inches = 'tight', dpi = 50)

        return graph

    def showerEnerg( self, process = 'all', figsize = [15,10], xlim = []):

        graph = plt.figure( figsize = ( figsize[0], figsize[1]) )
        plt.yscale('log'); plt.grid()
        plt.title('EM showers - energy distribution')
        plt.xlabel('E [GeV]'); plt.ylabel('entries/bin')
        
        crtrs = self.df[(self.df.charge == -1) & (self.df.ProcName == 'initStep') ].groupby(['Creator'])

        for crtr, subframe in crtrs:
            enrg = subframe.ptot.tolist()
            plt.hist(enrg, bins = 200, stacked = False, histtype = 'step', lw = 2.5, fill = False, label = '%s' %crtr)
        
        plt.legend() 
        if xlim != []: plt.xlim(0,2e-3)
        
        if self.save:  
            print ("Saving figure as ", self.plotpath, "particlesEMShowerEnrg.pdf")
            plt.savefig( self.plotpath + "particlesEMShowerEnrg.pdf", bbox_inches = 'tight', dpi = 50)
        
        if self.verbose: print('heaviest particle mass:', self.df.mass.max())

        return graph


    
