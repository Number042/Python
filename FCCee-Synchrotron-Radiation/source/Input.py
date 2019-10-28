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
    
    def __init__(self, path):
        self.path = path        
        
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
            tmp_df = pd.read_table(file, sep = r'\s+')

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
        directory = self.path

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
            if verbose:
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

    
    def readG4out(self, optics = 'fcc_ee', read = 'primaries', datType = 'default', verbose = 0):
        """
        Method to read in the G4 output
            -- optics:  string to preselect which machine to search for
            -- read:    option to choose whether primary or secondary data should be read; defaults to primaries
            -- datType: switch between default and collimation 
            
        returns: a data frame
        """
        # path(s) given during intialization of the object
        #
        filepath = self.path
        
        primDataFiles = []; secoDataFiles = []
        check_strings = '_prim|_seco'
        
        print ("files are in:", filepath) 
        print (" *********************************************** ")
        GlobDatFrame = pd.DataFrame()
        frameList = []
        opticsList = []

        for pth in filepath:
            j = 0
            for root, dirs, files in walk(pth, topdown = True):
                
                # exclude all hidden files and directories which have nothing to do with accelerators
                #
                dirs[:] = [d for d in dirs if not d[0] == '.' and optics in d and listdir(pth + d)]
                files = [f for f in files if not f[0] == '.' and optics in f]

                if verbose: print ( " subdirectories exist for following optics: \n", dirs, "\n -----------------------------")
                    
                print (" accessing directory:", root, "...")
                if dirs != []:
                    k = 0
                    for d in dirs:
                        print('subdir', d, 'contains files ... ')
                        opticsList.append(str(dirs[k]))
                        k += 1
                        if verbose > 1: 
                            print ("optics read from subdir:")
                            for optic in opticsList: print(" -- ", optic)
                else:
                    print ("    ==> no subdirectories.")        

                # check if the opticsList is empty before filling by files --> useful for working on temporary!
                # 
                if files != []:
                    print ("    ==> found data. \n")
                    if verbose > 1: print (files)
                    if opticsList == []:
                        print ("Try now to read optics type from file names ... \n")
                        
                    for f in files:
                            
                        if verbose > 1: print ( "current file: ", f )
                            
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
                    DatFrame = pd.DataFrame()
                    name = 'def_primaries'
                    
                    primDataFiles = [path.join(root, file) for file in files if findall('_prim_', file) and not findall('_coll', file)] # -- mlu 11-21-2017 -- '_prim_ntuple.out'
                    if verbose: print ("list of files: \n", primDataFiles)
                    
                    self.aperList = []; self.beamList = []; self.beamSizes = []
                    for file in primDataFiles:
    
                        if verbose: print ("   --> appending file:", file, "...")
                        tmp_df = self.getBeam_and_Aper_Info(file)

                        print( "counter j = ", j, "writing optic: ", opticsList[j], " to tmp_df ..." )
                        tmp_df['optics'] = opticsList[j]
                        
                        DatFrame = DatFrame.append(tmp_df)
                        j += 1
                        
                    if DatFrame.empty: print (" *** WARNING *** DatFrame empty!")
                    else: 
                        frameList.append(DatFrame)
                        print ("DatFrame appended \n")
                    
                elif datType == 'default' and read == 'secondaries':
                    DatFrame2 = pd.DataFrame()
                    name = 'def_secondaries'
                    
                    secoDataFiles = [path.join(root, file) for file in files if findall('_seco_', file) and not findall('_coll', file)] # -- mlu 11-21-2017 -- '_seco_ntuple.out'
                    if verbose: print ("list of files: \n", secoDataFiles)

                    self.aperList = []; self.beamList = []; self.beamSizes = []
                    for file in secoDataFiles:

                        if verbose: print ("   --> appending file:", file, "...")
                        tmp_df = self.getBeam_and_Aper_Info(file)

                        print ("counter j = ", j, "writing optics: ", opticsList[j], " to tmp_df ...") 
                        tmp_df['optics'] = opticsList[j]
                        
                        DatFrame2 = DatFrame2.append(tmp_df)
                        j += 1
                        
                    if DatFrame2.empty: print ("*** WARNING *** DatFrame2 empty!")
                    else:
                        frameList.append(DatFrame2)
                        print ("DatFrame2 appended \n")

                elif datType == 'collimation' and read == 'primaries':
                    DatFrame3 = pd.DataFrame()
                    name = 'col_primaries'
                    
                    primDataFiles = [path.join(root, file) for file in files if findall('_prim_', file) and findall('_coll', file)] # -- mlu 11-21-2017 -- '_prim_ntuple.out'
                    if verbose: print ("list of files: \n", primDataFiles)
                    
                    self.aperList = []; self.beamList = []; self.beamSizes = []
                    for file in primDataFiles:
                        
                        if verbose: print ("    --> appending file:", file, "...")
                        tmp_df = self.getBeam_and_Aper_Info(file)
                        
                        print( "counter j = ", j, "writing optic: ", opticsList[j], " to tmp_df ..." )
                        tmp_df['optics'] = opticsList[j]
                        
                        DatFrame3 = DatFrame3.append(tmp_df)
                        j += 1
                    
                    if DatFrame3.empty: print ("*** WARNING **** DatFrame3 empty!")
                    else: 
                        frameList.append(DatFrame3)
                        print ("DatFrame3 appended \n")

                elif datType == 'collimation' and read == 'secondaries':
                    DatFrame4 = pd.DataFrame()
                    name = 'col_secondaries'
                    
                    secoDataFiles = [path.join(root, file) for file in files if findall('_seco_', file) and findall('_coll', file)] # -- mlu 11-21-2017 -- '_seco_ntuple.out'
                    if verbose: print ("list of files: \n", secoDataFiles)
                    
                    self.aperList = []; self.beamList = []; self.beamSizes = []
                    for file in secoDataFiles:
                        
                        if verbose: print ("    --> appending file:", file, "...")
                        tmp_df = self.getBeam_and_Aper_Info(file)

                        print ("counter j = ", j, "writing optics: ", opticsList[j], " to tmp_df ...") 
                        tmp_df['optics'] = opticsList[j]
                        
                        DatFrame4 = DatFrame4.append(tmp_df)
                        j += 1                
                    
                    if DatFrame4.empty: print ("*** WARNING *** DatFrame4 empty!")
                    
                    else: 
                        frameList.append(DatFrame4)
                        print ("DatFrame4 appended \n")
                
                else:
                    raise RuntimeError('Invalid choice of "datType" and/or "read"')
                    
            # clear the opticsList for next run
            #
            if verbose: print ("clearing opticsList for next run ... \n")
            del opticsList[:]
                
        
        if frameList == []: raise ValueError('No data collected. List of frames empty:', frameList) 
        
        GlobDatFrame = GlobDatFrame.append(frameList)
        
        # do some forward filling on the origin-volume column to have 
        # source information available throughout the track object
        #
        if 'OrigVol' in GlobDatFrame:
            GlobDatFrame['OrigVol'] = GlobDatFrame.OrigVol.replace('None', nan).ffill()
        
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

def checkRing(df, verbose = 0):
    """
    Method to quickly check, if a sequence is closed (ring) or not. If not closed, give fudge factor (2pi - offset)
        -- df:    pass data frame to the function, for example from read_twiss
    """
    angleSum = df.ANGLE.sum()
    if verbose: print ("check")
    print ("---------------------------------- \n Checking, if ring is closed: \n", "angleSum = ", angleSum)
    twoPi = 2*pi
    
    if angleSum != twoPi:
        fudge = 2*pi - angleSum
        print (" ** Ring not closed - offset of: ", fudge)           
        
def print_verbose(df):
    """ 
    General verbose output - some information on the data, i.e. keys of the DF
    """
    print ("-------------------------------------")
    print ("DF holds: ", df.keys())
    print ("-------------------------------------")

def get_apertures():
    
    # collect all apertures available in a list
    #
    directory = path.expanduser('~/Codes/Projects/FCCee/Collimator/Data/')
    aperlist = []
    dataFiles = []

    for root, dirs, files in walk(directory, topdown = True):

        # exclude all hidden files and directories
        #
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        
        # loop through elements and collect apertures, if existing
        #
        for element in files:
            if element.endswith('seco_ntuple.out'):
                dataFiles.append(element)
                
                aper = findall(r'\D(\d{4})\D', element)
                if verbose: print ("appending aperture:", int(aper[0]), " ..." )
                aperList.append(int(aper[0]))
            else:
                raise RuntimeError('No specifications found. List of apertures empty:', aperList)
                
    # write out apertures
    #
    #~ for i in dataFiles:
        #~ aper = findall(r'\D(\d{4})\D', i) 
        #~ aperlist.append(int(aper[0]))
    
    return aperlist