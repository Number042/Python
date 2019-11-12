import pandas as pd 
from numpy import nan, float64, pi
from os import walk, listdir, path 
from re import findall, split

class DataReader:
    
    """
    Data-wrapper class to read in tfs or G4 output
        -- project: a name for the current project
        -- path: takes a single or list of path(s) to search for files
    """
    
    def __init__( self, filepath, verbose = 0 ):
        self.filepath = filepath        
        self.verbose = verbose

    def getBeam_and_Aper_Info(self, file):
        
        # input to check for beam characteristics and aperture information
        pattern = 'pencil|gauss\d{2}|gauss\d{1}|ring\d{2}|ring\d{1}|flat\d{2}|flat\d{1}'
        types = 'pencil|gauss|ring|flat'
        beamSize = '\d{2}|\d{1}'
        aperSize = r'\D(\d{4})\D'
        
        beaminfo = findall(pattern, file)
        aper = findall(aperSize, file)
        
        if beaminfo:
            print ("    * beam found: ", beaminfo[0])
            tmp_df = pd.read_table( file, sep = r'\s+', keep_default_na = False )

            bemsh = findall(types, beaminfo[0])
            if bemsh:
                self.beamList.append(bemsh[0])
                tmp_df['BeamShape'] = bemsh[0]

            bemsi = findall(beamSize, beaminfo[0])
            if bemsi:
                self.beamSizes.append(int(bemsi[0]))
                tmp_df['BeamSize'] = int(bemsi[0])

        else:
            print ("    * beam shape: none, set to pencil")
            tmp_df = pd.read_table(file, sep = r'\s+')
            self.beamList.append('pencil')
            tmp_df['BeamShape'] = 'pencil'
            self.beamSizes.append(0)
            tmp_df['BeamSize'] = 0
        
        if aper != []:
            self.aperList.append(int(aper[0]))
            print ("    ==> found aperture:", aper[0])
            tmp_df['CollDim'] = int(aper[0])
        else:
            print ("    * no aperture specified")
            tmp_df['CollDim'] = 0

        # some verbose output and returning the temporary data frame
        #
        if tmp_df.empty: print ("WARNING: tmp_df is empty!")
        return tmp_df
    
    
    def get_beamShapes(self, verbose = 0):
        
    
        # collect all beam shapes; use | as 'or' in regex for distinct types
        #
        directory = self.filepath

        pattern = 'pencil|gauss\d{2}|gauss\d{1}|ring\d{2}|ring\d{1}|flat\d{2}|flat\d{1}'
        types = 'pencil|gauss|ring|flat'
        size = '\d{2}|\d{1}'
        
        beamList = []; beamSizes = []
        dataFiles = []
        for i in directory:
            
            for root, dirs, files in walk(i, topdown = True):
                
                # exclude all hidden files and directories
                #
                files = [f for f in files if not f[0] == '.']
                dirs[:] = [d for d in dirs if not d[0] == '.']
                for element in files:
                    dataFiles.append(element)
            if self.verbose:
                print ("get_beamShapes: read in files", dataFiles)
            
            # write out beam types
            #
            for element in dataFiles:
                
                beaminfo = findall(pattern, element)
                if beaminfo:
                    print ("    * beam found: ", beaminfo[0])
                    bemsh = findall(types, beaminfo[0])
                    if bemsh:
                        beamList.append(bemsh[0])
                    bemsi = findall(size, beaminfo[0])
                    if bemsi:
                        beamSizes.append(int(bemsi[0]))
                else:
                    beamList.append('pencil'); beamSizes.append(0)
                
            return beamList, beamSizes

    def buildFrame( self, parentDir, files, incr, optics, datType, read ):
        
        DatFrame = pd.DataFrame()
        
        primDataFiles = [path.join(parentDir, file) for file in files if findall(read, file) and not findall(datType, file)] # -- mlu 11-21-2017 -- '_prim_ntuple.out'
        if self.verbose: print ("list of files: \n", primDataFiles)
        
        self.aperList = []; self.beamList = []; self.beamSizes = []
        for file in primDataFiles:

            if self.verbose: print ("   --> appending file:", file, "...")
            tmp_df = self.getBeam_and_Aper_Info(file)

            print( "counter j = ", incr, "writing optic: ", optics[incr], " to tmp_df ..." )
            tmp_df['optics'] = optics[incr]
            
            DatFrame = DatFrame.append(tmp_df)
            incr += 1
            
        if DatFrame.empty: print (" *** WARNING *** DatFrame empty!")
        else: print ("returning DatFrame ... ")
        
        return DatFrame

    
    def readG4out(self, optics = 'fcc_ee', read = 'primaries', datType = 'default', verbose = 0):
        """
        Method to read in the G4 output
            -- optics:  string to preselect which machine to search for
            -- read:    option to choose whether primary or secondary data should be read; defaults to primaries
            -- datType: switch between default and collimation 
            
        RETURN: a data frame
        """
        
        print ("files are in:", self.filepath) 
        print (" *********************************************** ")
        GlobDatFrame = pd.DataFrame()
        frameList = []
        opticsList = []

        for pth in self.filepath:
            j = 0
            for root, dirs, files in walk(pth, topdown = True):
                
                # exclude all hidden files and directories which have nothing to do with accelerators
                #
                dirs[:] = [d for d in dirs if not d[0] == '.' and optics in d and listdir(pth + d)]
                files = [f for f in files if not f[0] == '.' and optics in f]

                if self.verbose: print ( " subdirectories exist for following optics: \n", dirs, "\n -----------------------------")
                    
                print (" accessing directory:", root, "...")
                if dirs != []:
                    k = 0
                    for d in dirs:
                        print('subdir', d, 'contains files ... ')
                        opticsList.append(str(dirs[k]))
                        k += 1
                        if self.verbose > 1: 
                            print ("optics read from subdir:")
                            for optic in opticsList: print(" -- ", optic)
                else:
                    print ("    ==> no subdirectories.")        

                # check if the opticsList is empty before filling by files --> useful for working on temporary!
                # 
                if files != []:
                    print ("    ==> found data. \n")
                    if self.verbose > 1: print (files)
                    if opticsList == []:
                        print ("Try now to read optics type from file names ... \n")
                        
                    for f in files:
                            
                        if self.verbose > 1: print ( "current file: ", f )
                            
                        # distinction in data tpe: default vs. collimation
                        #
                        if datType == 'default':
                                
                            if read == 'primaries' and  'prim' in f:
                                if not findall('_coll', f): 
                                    optic = split('_b1',f)  #optic = split('_b1_prim',f) 
                                    opticsList.append(str(optic[0])) 
                            elif read == 'secondaries' and 'seco' in f:
                                if not findall('_coll_', f):
                                    optic = f.split('_b1') #optic = f.split('_b1_seco')
                                    opticsList.append(str(optic[0]))
                                    
                        elif datType == 'collimation':
                             
                            if read == 'primaries' and  'prim' in f:
                                if findall('_coll_', f):
                                    optic = split('_b\d{1}_\d{4}_', f) 
                                    opticsList.append(str(optic[0])) 
                            elif read == 'secondaries' and 'seco' in f:
                                if findall('_coll_', f):
                                    optic = split('_b\d{1}_\d{4}_', f)
                                    opticsList.append(str(optic[0]))
                                    
                    if opticsList == []: 
                        print("*** WARNING *** opticsList empty --> optics specification for \n",
                              f, 
                              "\n failed!")
                    
                    elif opticsList != [] and verbose > 1: 
                        print ("optics read from files:")
                        for optic in opticsList:
                            print (" -- ", optic)
                        
                else: raise RuntimeError( "no files found -- given directory seems empty!" )

                # collect data based on certain parameters
                #
                if datType == 'default' and read == 'primaries':
                    name = 'def_primaries'
                    frameList.append( self.buildFrame( root, files, j, opticsList, datType = '_coll', read = '_prim_'  ) )
                
                elif datType == 'default' and read == 'secondaries':
                    name = 'def_secondaries'
                    frameList.append( self.buildFrame( root, files, j, opticsList, datType = '_coll', read = '_seco_') )

                # not yest used (mlu -- 2019 - 11 - 05); needs modification in buildFrame (or drop it?)
                # maybe possible to read coll aperture from twiss?
                #
                # elif datType == 'collimation' and read == 'primaries':
                #     name = 'col_primaries'
                #     frameList.append( self.buildFrame( root, files, j, opticsList, datType = '_coll', read = '_prim_') )                    
                # #     primDataFiles = [path.join(root, file) for file in files if findall('_prim_', file) and findall('_coll', file)] # -- mlu 11-21-2017 -- '_prim_ntuple.out'

                # elif datType == 'collimation' and read == 'secondaries':
                #     name = 'col_secondaries'
                # #     secoDataFiles = [path.join(root, file) for file in files if findall('_seco_', file) and findall('_coll', file)] # -- mlu 11-21-2017 -- '_seco_ntuple.out'
                
                else:
                    raise RuntimeError('Invalid choice of "datType" and/or "read"')
                    
            # clear the opticsList for next run
            #
            if self.verbose: print ("clearing opticsList for next run ... \n")
            del opticsList[:]
                
        
        if frameList == []: raise ValueError('No data collected. List of frames empty:', frameList) 
        
        GlobDatFrame = GlobDatFrame.append(frameList)
        
        # do some forward filling on the origin-volume column to have 
        # source information available throughout the track object. Replace "none" with the value for OrigVol
        #
        if 'OrigVol' in GlobDatFrame:
            if self.verbose: print( 'forward filling OrigVol, replacing string \"none\" ...' )
            GlobDatFrame['OrigVol'] = GlobDatFrame.OrigVol.replace( 'none' ).ffill()
        else: raise Warning("*** No column OrigVol found in the data set!")

        if GlobDatFrame.empty: print ("*** WARNING **** overall dataframe empty!")
        else:
            GlobDatFrame.name = name
            return GlobDatFrame

def readParams(file, output = 0, verbose = 0, filetype = 'csv'):
    """
    Function to read the parameters for FCC-ee and write data to csv. Also allows to do other stuff like 
    changing parameters once an update is released.
        -- file:     input file (spreadsheet)
        -- output:   select if the DF is printed to a text file
        -- filetype: choose a file type for the output; defaults to csv ==> LaTeX csvsimple input!
    
    returns: dataframe containing the 
    """
    # set some variables
    #
    path = '/home/mlueckhof/PhD/Notes/IRDesign/data/'
    
    # read spreadsheet with parameters
    #
    pd.set_option( 'display.float_format', '{:.2g}'.format )
    DF = pd.read_excel( file, dtype = {'LER':float64, 'HER':float64 } )
    DF.name = 'MachineParam'
    # DF.apply( pd.to_numeric, errors = 'ignore' )

    if verbose: print("---------------------------------- \n", "DF contains: \n", DF.keys(), 
                        "\n Data-Types are: \n", DF.dtypes, "\n ----------------------------------")
                        
    if output:
        if filetype == 'csv':
            DF.to_csv( path + 'FCCeeParamList.csv' )
            print ( "Created output:", path + 'FCCeeParamList.csv' )
        else: 
            print (" *** Error: No other filetypes supported yet")
    
    return DF

        
def print_verbose(df):
    """ 
    General verbose output - some information on the data, i.e. keys of the DF
    """
    print ("-------------------------------------")
    print ("DF holds: ", df.keys())
    print ("-------------------------------------")