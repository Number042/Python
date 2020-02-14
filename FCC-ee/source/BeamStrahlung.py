from numpy import average, mean
from os import walk
from re import split

class BeamStrahlung():

    ## walk through directory and select relevant files
    ##
    def selectFiles( path, name ):
        fileList = []
        print('Searching path', path, '...')
        for (dirpath, dirnames, filenames) in walk( str(path) ):
            for filename in filenames:
                if filename.startswith( str(name) ): print('appening', filename, 'to fileList'); fileList.append(filename)    
        
        return fileList

    ## read the mean photon energy and number of photons per MP from output files
    ##
    def readData( dataFiles, verbose = 1 ):
        """
        Reads the mean photon energy (inital and final) and the photon number/macro particle (initial and final)
        """
        E_mean = []; n_gam = []; beam = 'dummy'; 

        for file in dataFiles:
            E_tmp = []; n_tmp = []
            with open(file, 'r+') as inputFile:
                if verbose: print('opened file', file)
                    
                for line in inputFile:
                    
                    if 'beam1' in line: 
                        beam = 'b1'
                        print('found b1')

                    elif 'beam2' in line: beam = 'b2'

                    if beam == 'b1': 
                        print('current beam =', beam)
                        if verbose: print(line)

                        if 'average photon energy' in line:
                            strings = split('\s|:|\n', line)            
                            E = float(strings[9])
                            E_tmp.append(E)
                            
                        if 'number of phot. per tracked macropart' in line:
                            strings = split('\s|:', line)
                            n = float(strings[10])
                            n_tmp.append(n)

                if E_tmp != []:
                    print('appending E_tmp.mean =', mean(E_tmp), '\n n_tmp.mean =', mean(n_tmp))
                    E_mean.append( mean(E_tmp) )
                if n_tmp != []: n_gam.append( mean(n_tmp) )
        return E_mean, n_gam

    def CalcBSPower( n_gam, E_mean ):
        
        E_gam_tot = average(n_gam)*params['Np']*average(E_mean)
        P_SRBS = E_gam_tot*elementary_charge/(tau_BSP*1e-9)
        print(E_gam_tot, 'GeV')
        print(P_SRBS*1e6, 'kW/beam and IP')
        
        return P_SRBS

    def RunGP(cells):
        
        for i in cells:
            print('running z =', i, '...')
            ## set cell size
            call( ['sed', '-i', 's/n_z\=[0-9]\+/n_z\=%s/g' %str(i), 'acc.dat'] )
            ## run the program
            call( ['./guinea', 'FCCee', 'FCCee_BS', 'testOut_nz%s' %str(i)] )
            ## rename files 
            call( ['cp', 'photon.dat', 'photon_nz%s.dat' %str(i)])
            if i == max(cells): print('... done.')
            else: print('... next run.')