import matplotlib.pyplot as plt
import pandas as pd
class PlotScore:
    # mlu -- 02-08-2018 -- maybe think about putting all this into a new clas 'Scoring'
    #
    def __init__(self, df, verbose):
        self.frame = df
        
    def plot_spatialGamDistr(inputFile, plotpath, nBin = 100, save = 0):
        """
        Method to analyze data created by SteppingAction in TestEm16 for collecting detailed information 
        on photons that enter certain volume(s).
            -- input:       file to read the data from. Dedicated frame created
            -- plotpath:    specify location for storage of plots
        """
        # Create local dataframe to store the Geant4 output
        #
        header = ['Name', 'Energy', 'x', 'y', 'z', 'px/p', 'py/p', 'pz/p']
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
        
        # mlu -- 03-08-2018 -- make plots rasterized to reduce file size (increasing statisitcs)
        #
        plt.figure( figsize = (12, 10) )
        plt.grid()
        plt.plot(scoreFrame.z.tolist(), scoreFrame.x.tolist(), 'b.', rasterized = True)
        plt.xlabel('z [m]')
        plt.ylabel('x [m]')
        plt.title('x-z Position at Entrance')
        if save: plt.savefig( plotpath + "gamPosXZ.pdf" )
        
        plt.figure( figsize = (12, 10) )
        plt.grid()
        plt.plot(scoreFrame.x.tolist(), scoreFrame.y.tolist(), 'b.', rasterized = True)
        plt.xlabel('x [m]')
        plt.ylabel('y [m]')
        plt.title('x-y Position at Entrance')
        if save: plt.savefig( plotpath + "gamPosXY.pdf" )

        return
