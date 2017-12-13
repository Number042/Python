import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import collections as clt
import sys
import os
import difflib as dl  
import re

class DataReader:
    
    """
    Data-wrapper class to read in tfs or G4 output
        -- project: a name for the current project
        -- path: takes a single or list of path(s) to search for files
    """
    
    def __init__(self, path):
        self.path = path
    
    def readParams(file, output = 0, filetype = 'csv'):
        """
        Function to read the parameters for FCC-ee and write data to csv. Also allows to do other stuff like 
        changing parameters once an update is released.
            -- file:     input file (spreadsheet)
            -- output:   select if the DF is printed to a text file
            -- filetype: choose a file type for the output; defaults to csv ==> LaTeX csvsimple input!
        
        returns: dataframe containing the 
        """
        # set some variables
        path = '/home/mlueckhof/PhD/Notes/IRDesign/data/'
        # read spreadsheet with parameters
        DF = pd.read_excel(file)
        DF.name = 'FCCeeParam'
        
        if output:
            if filetype == 'csv':
                DF.to_csv(path+'FCCeeParamList.csv')
                print ("Created output:", path+'FCCeeParamList.csv')
            else: 
                print (" *** Error: No other filetypes supported yet")
        
        return DF
        
        
        
    def getBeam_and_Aper_Info(self, file):
        
        # input to check for beam characteristics and aperture information
        pattern = 'pencil|gauss\d{2}|gauss\d{1}|ring\d{2}|ring\d{1}|flat\d{2}|flat\d{1}'
        types = 'pencil|gauss|ring|flat'
        beamSize = '\d{2}|\d{1}'
        aperSize = r'\D(\d{4})\D'
        
        beaminfo = re.findall(pattern, file)
        aper = re.findall(aperSize, file)
        
        if beaminfo:
            print ("    * beam found: ", beaminfo[0])
            tmp_df = pd.read_table(file, sep = r'\s+')

            bemsh = re.findall(types, beaminfo[0])
            if bemsh:
                self.beamList.append(bemsh[0])
                tmp_df['BeamShape'] = bemsh[0]

            bemsi = re.findall(beamSize, beaminfo[0])
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
            
            for root, dirs, files in os.walk(i, topdown = True):
                
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
                
                beaminfo = re.findall(pattern, element)
                if beaminfo:
                    print ("    * beam found: ", beaminfo[0])
                    bemsh = re.findall(types, beaminfo[0])
                    if bemsh:
                        beamList.append(bemsh[0])
                    bemsi = re.findall(size, beaminfo[0])
                    if bemsi:
                        beamSizes.append(int(bemsi[0]))
                else:
                    beamList.append('pencil'); beamSizes.append(0)
                
            return beamList, beamSizes

    
    def readG4out(self, read = 'primaries', datType = 'default', verbose = 0):
        """
        Method to read in the G4 output
            -- read:    option to choose whether primary or secondary data should be read; defaults to primaries
            -- datType: switch between default and collimation 
            
        returns: a data frame
        """
        # path(s) given during intialization of the object
        #
        path = self.path
        
        primDataFiles = []; secoDataFiles = []
        check_strings = '_prim|_seco'
        
        print ("files are in:", path) 
        print (" *********************************************** ")
        GlobDatFrame = pd.DataFrame()
        frameList = []
        opticsList = []

        for i in path:
            j = 0
            for root, dirs, files in os.walk(i, topdown = True):
                
                # exclude all hidden files and directories
                #
                dirs[:] = [d for d in dirs if not d[0] == '.']
                files = [f for f in files if not f[0] == '.']
                
                print (" accessing directory:", root, "...")
                if dirs != []:
                    print (" subdirectories exist for following optics: \n", dirs, "\n -----------------------------")
                    k = 0
                    for d in dirs:
                        opticsList.append(str(dirs[k]))
                        k += 1
                    if verbose >1: 
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
                                if not re.findall('_coll', f): 
                                    optic = re.split('_b1_prim',f) 
                                    opticsList.append(str(optic[0])) 
                            elif read == 'secondaries' and 'seco' in f:
                                if not re.findall('_coll_', f):
                                    optic = f.split('_b1_seco')
                                    opticsList.append(str(optic[0]))
                                    
                        elif datType == 'collimation':
                             
                            if read == 'primaries' and  'prim' in f:
                                if re.findall('_coll_', f):
                                    optic = re.split('_b\d{1}_\d{4}_', f) 
                                    opticsList.append(str(optic[0])) 
                            elif read == 'secondaries' and 'seco' in f:
                                if re.findall('_coll_', f):
                                    optic = re.split('_b\d{1}_\d{4}_', f)
                                    opticsList.append(str(optic[0]))
                                    
                    if opticsList == []: 
                        print("*** WARNING *** opticsList empty --> optics specification for \n", f, "\n failed!")
                    
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
                    
                    primDataFiles = [os.path.join(root, file) for file in files if re.findall('_prim_', file) and not re.findall('_coll', file)] # -- mlu 11-21-2017 -- '_prim_ntuple.out'
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
                    
                    secoDataFiles = [os.path.join(root, file) for file in files if re.findall('_seco_', file) and not re.findall('_coll', file)] # -- mlu 11-21-2017 -- '_seco_ntuple.out'
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
                    
                    primDataFiles = [os.path.join(root, file) for file in files if re.findall('_prim_', file) and re.findall('_coll', file)] # -- mlu 11-21-2017 -- '_prim_ntuple.out'
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
                    
                    secoDataFiles = [os.path.join(root, file) for file in files if re.findall('_seco_', file) and re.findall('_coll', file)] # -- mlu 11-21-2017 -- '_seco_ntuple.out'
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
            GlobDatFrame['OrigVol'] = GlobDatFrame.OrigVol.replace('None', np.nan).ffill()
        
        if GlobDatFrame.empty: print ("*** WARNING **** overall dataframe empty!")
        else:
            GlobDatFrame.name = name
            return GlobDatFrame


class DataSelection:
    
    """
    Tool-kit to do some selection on overall input data.
    """
    
    def __init__(self, df):
        self.df = df

    def opticsSelection(self, optics = 'all', verbose = 0):
        
        """
        Function to select specific optics, put these into a new dataframe that can be passed for further processing. 
            -- optics:  choose which otics to be put into the new frame, defaults to 'all'
        
        returns: another frame, holding only data from selected optics
        """
        # set dataframe to the one passed as class object
        #
        df = self.df
        
        # set up default (empty) frame and list
        #
        df_opt = pd.DataFrame()
        tmpList = []
        
        # case 1: no specific optics selection
        #
        if optics == 'all':
            df_opt = df
        
        # case 2: optics specified
        #
        else:
            if verbose: 
                print ("-*-*-*-*-*-*-*-*-*-*-*-*-*- \n Following frame(s) selected:")
                for optic in optics: print("--", optic)
            
            for opt in optics:
                tmp_df = df[df.optics == opt]
                tmpList.append(tmp_df)
                if verbose >1: print (tmp_df.head())
            if tmpList == []: raise RuntimeError('No data collected. List of frames empty:', tmpList)
        
            else:
                df_opt = df_opt.append(tmpList)
                df_opt.name = df.name
                
                
        df_opt.name = df.name
        return df_opt
        
    
    def get_beamShapes_and_Size(self, verbose = 0):
        """
        Function to read all beam types and sizes from a given frame. Allows to check for plotting if desired 
        type and/or size is/are available.
            -- df:      dataframe to pass to this function
            -- verbose: set verbosity level; defaults to 0
        """
        
        df = self.df
        
        beamTypes = set(df.BeamShape) 
        beamSize = set(df.BeamSize)
        
        if verbose: print ("*-*-*-*-*-*-*-*-*-*-*-*-* \n Available types:", beamTypes, "\n Available sizes:", beamSize)
        
        return beamTypes, beamSize

    def splitNames(df, verbose = 0):
        """
        Function to split the content of the 'Name' column that is written in the default frame by 'readG4out' and 'opticsSelection'.
        It splits the strings of that column into 4 different columns for element, type, number and vacuum.
            -- df:      user needs to pass in the data frame to be splitted. If just using self object, another frame would be created
                        from class instance, regardless of possible previous optics selection.
            -- verbose: set the verbosity level
        returns: a frame with appended columns holding the splitted content
        """
        
        dfName = df.name
        
        if verbose == 1: 
            print ("-*-*-*-*-*-*-*-*-*-*-*-*-*- \n Selected following data frame:", df.name)
        elif verbose > 1:
            print (df.head())
            print (df.Name)
        
        # do a selection here, depending on the optics 
        # -- mlu 11-16-2017 -- has to be made more intelligent 
        # to deal with complex 'Name' expressions or left out!
        #
        names = df.Name.tolist()
        maxString = max(names, key = len)
        string = maxString.split('_')
        numbElements = len(string)
        
        if verbose: print ("number of elements: ", numbElements, " from ", string)
        
        if numbElements == 4:
            columns = ['element', 'type', 'eleNumber', 'vacuum']
        else:
            columns = ['element', 'type', 'vacuum']
            
        if verbose: print ("columns selected: ", columns)

        #~ if 'SingleBend' in df.optics.tolist():
            #~ df_split = pd.DataFrame(df.Name.str.split('_').tolist(), columns = ['element', 'type', 'eleNumber', 'vacuum']) # ['element', 'type', 'vacuum']
        #~ else:
            #~ df_split = pd.DataFrame(df.Name.str.split('_').tolist(), columns = ['element', 'type', 'vacuum']) # ['element','type','eleNumber','vacuum']

        df_split = pd.DataFrame(df.Name.str.split('_').tolist(), columns = columns)
        
        if verbose == 1: 
            print ("-*-*-*-*-*-*-*-*-*-*-*-*-*- \n Splitted 'Name' into: \n", columns) #['element','type','eleNumber','vacuum'])
        elif verbose > 1:
            print ("-*-*-*-*-*-*-*-*-*-*-*-*-*- \n Split-Frame contains: \n", df_split.dtypes)
        
        if verbose > 1: print (df_split.head())
        
        # concat the new frame to original, join on 'inner' to insert additional columns
        #
        frames = [df, df_split]
        df = pd.concat(frames, axis = 1, join = 'inner')
        
        if verbose: print("*-*-*-*-*-*-*-*-*-*-*-*-* \n dataframe holds following keys and dtypes: \n", df.dtypes)
        
        df.name = dfName
        return df
        
class Tracking:
    
    """
    Tool kit to do extended selection on tracking information from G4
    """
    
    def __init__(self, frame, verbose):
        self.frame = frame
        self.verbose = verbose
        
    def collectInfo(self, verbose):
        """
        Method to collect basic information from the .out of G4 in arrays (basically for plotting)
            -- frame:   refers to the data frame object resulting from a groupby operation
        """
        
        frame = self.frame
        verbose = self.verbose
        
        if verbose: 
            print ("Selected frame contains: \n", " ------------------------ \n", frame.head())
    
        elif verbose > 1: 
            print (sys._getframe().f_lineno)
            print ("Selected frame complete: \n", " ------------------------ \n", frame)
        
        event_last = 999999999
        track_last = 999999999
 
        # initiate all necessary arrays
        #
        Z_pos = []; Z_org = []; Z_hit = []; 
        E_org = []; E_hit = []
        srcName = []

        for row in frame.index:
            
            event = frame.get_value(row,'Event')
            track = frame.get_value(row,'Track')
            z_eu  = frame.get_value(row,'z_eu')
            mat   = frame.get_value(row,'Material')
            energ = frame.get_value(row,'ptot')
            process = frame.get_value(row, 'ProcName')
            creator = frame.get_value(row, 'Creator')
            
            if(process == 'initStep' and creator == 'SynRad'):
                Z_org.append(z_eu)
                E_org.append(energ*10**6)

            if(event_last != event or track_last != track):
                event_last = event
                track_last = track
                Z_pos.append(z_eu)
                
            elif(mat == 'Cu'): # 'Fe'
                Z_hit.append(z_eu)
                E_hit.append(energ)
                
                
        #~ if verbose > 1: print ("Collected data in \n", "Z_pos: \n ------------------------- \n", Z_pos, "\n Z_org: \n ------------------------- \n", Z_org, 
                               #~ "\n Z_hit: \n ------------------------- \n", Z_hit) 
        
        # returns several lists
        #
        return Z_pos, Z_org, Z_hit
            
# read twiss files, should be as flexible as possible
class TfsReader:
    
    def __init__(self, tfs):
        self.tfs = tfs
        
        
    def read_twiss(self, verbose = 0):
        """
        Function to read general twiss files.
        """
        tfs = self.tfs

        df = pd.read_table(tfs, sep = "\s+", skiprows = 45, index_col = False) 

        # read columns and drop the first one (*) to actually match the right header
        #
        cols = df.columns
        twissHeader = cols[1:]

        # drop NaN column and reset header
        #
        df = df.dropna(axis = 1, how = 'any')
        df.columns = twissHeader

        df = df.drop(df.index[0])
        df = df.convert_objects(convert_numeric = True)

        if verbose:
            print("----------------------------------")
            print(" DF contains: \n", df.keys(), "\n data tpes are: \n", df.dtypes)
            print("----------------------------------")

        return df
    
    def read_survey(self, verbose = 0):
        """
        Function to read general survey files.
        """

        surveyHeader = ['S', 'X', 'Y', 'Z', 'THETA', 'PHI', 'PSI']
    
     
    
def checkRing(df, verbose = 0):
    """
    Method to quickly check, if a sequence is closed (ring) or not. If not closed, give fudge factor (2pi - offset)
        -- df:    pass data frame to the function, for example from read_twiss
    """
    angleSum = df.ANGLE.sum()
    if verbose: print ("check")
    print ("---------------------------------- \n Checking, if ring is closed: \n", "angleSum = ", angleSum)
    twoPi = 2*np.pi
    
    if angleSum != twoPi:
        fudge = 2*np.pi - angleSum
        print (" ** Ring not closed - offset of: ", fudge)           
        

   

            

def print_verbose(df):
    # General verbose output - some information on the data
    # print keys of the DF
    #
    print ("-------------------------------------")
    print ("DF holds: ", df.keys())
    print ("-------------------------------------")

def get_apertures():
    
    # collect all apertures available in a list
    #
    directory = os.path.expanduser('~/Codes/Projects/FCCee/Collimator/Data/')
    aperlist = []
    dataFiles = []

    for root, dirs, files in os.walk(directory, topdown = True):

        # exclude all hidden files and directories
        #
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        
        # loop through elements and collect apertures, if existing
        #
        for element in files:
            if element.endswith('seco_ntuple.out'):
                dataFiles.append(element)
                
                aper = re.findall(r'\D(\d{4})\D', element)
                if verbose: print ("appending aperture:", int(aper[0]), " ..." )
                aperList.append(int(aper[0]))
            else:
                raise RuntimeError('No specifications found. List of apertures empty:', aperList)
                
    # write out apertures
    #
    #~ for i in dataFiles:
        #~ aper = re.findall(r'\D(\d{4})\D', i) 
        #~ aperlist.append(int(aper[0]))
    
    return aperlist

    
# Add function for aperture selection, pass this to plot_data if needed
# extend to more detailed data filtering?
#
def aper_select(df, aperture = 'all'):
    """
    Function to do some data filtering.
        -- aperture: allows to choose only certain dimensions; defaults to 'all'
    """
    aperList = get_apertures()
    
    if re.findall('col', df.name):
        print ("found collimator frame - groupby 'CollDim' \n", "-----------------------------")
        print (aperList)

    if aperture == 'all':
        # add the aperture option here?
        print ('selected all apertures!')
        grouped = df.groupby('CollDim')
        
    else:
        grouped = pd.DataFrame()
        for i in aperture:
            print ('aperture selected:', i)
            if i in aperList:
                tmp = df[df.CollDim==i]
                grouped = grouped.append(tmp)
#                 print (tmp.head())
            else:
                print (" ** Error: selected aperture", i, "not in the list.")
                
#     print (grouped)
    return grouped

    
