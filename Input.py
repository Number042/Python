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
                    if verbose >2: print ("opticsList:", opticsList[0])
                    
                else:
                    print ("    ==> no subdirectories.")
                
                if files != []:
                    print ("    ==> found data.")
                    if verbose: print (files)
                
                # collect data based on certain parameters
                #

                if datType == 'default' and read == 'primaries':
                    DatFrame = pd.DataFrame()
                    
                    name = 'def_primaries'
                    
                    primDataFiles = [os.path.join(root, file) for file in files if re.findall('_prim_ntuple.out', file) and not re.findall('_coll', file)]
                    if verbose: print ("list of files:", primDataFiles)
                    
                    self.aperList = []; self.beamList = []; self.beamSizes = []
                    for file in primDataFiles:
    
                        tmp_df = self.getBeam_and_Aper_Info(file)

                        if verbose: print ("   --> appending file:", file, "...")
                        DatFrame = DatFrame.append(tmp_df)
                        
                    if DatFrame.empty: print ("WARNING: DatFrame empty!")
                    else: 
                        DatFrame['optics'] = opticsList[j]
                        frameList.append(DatFrame)
                        print ("DatFrame appended")
                        j += 1
                    
                elif datType == 'default' and read == 'secondaries':
                    DatFrame2 = pd.DataFrame()
                    name = 'def_secondaries'
                    
                    secoDataFiles = [os.path.join(root, file) for file in files if re.findall('_seco_ntuple.out', file) and not re.findall('_coll', file)]
                    if verbose: print ("list of files:", secoDataFiles)

                    self.aperList = []; self.beamList = []; self.beamSizes = []
                    for file in secoDataFiles:

                        tmp_df = self.getBeam_and_Aper_Info(file)

                        if verbose: print ("   --> appending file:", file, "...")
                        DatFrame2 = DatFrame2.append(tmp_df)

                    if DatFrame2.empty: print ("WARNING: DatFrame2 empty!")
                    else: 
                        DatFrame2['optics'] = opticsList[j]
                        frameList.append(DatFrame2)
                        print ("DatFrame2 appended")
                        j += 1

                elif datType == 'collimation' and read == 'primaries':
                    DatFrame3 = pd.DataFrame()
                    name = 'col_primaries'
                    
                    primDataFiles = [os.path.join(root, file) for file in files if re.findall('_prim_ntuple.out', file) and re.findall('_coll', file)]
                    if verbose: print ("list of files:", primDataFiles)
                    
                    self.aperList = []; self.beamList = []; self.beamSizes = []
                    for file in primDataFiles:
                        
                        tmp_df = self.getBeam_and_Aper_Info(file)
                        
                        if verbose: print ("    --> appending file:", file, "...")
                        DatFrame3 = DatFrame3.append(tmp_df)
                    
                    if DatFrame3.empty: print ("WARNING: DatFrame3 empty!")
                    else: 
                        DatFrame3['optics'] = opticsList[j]
                        frameList.append(DatFrame3)
                        print ("DatFrame3 appended")
                        j += 1

                elif datType == 'collimation' and read == 'secondaries':
                    DatFrame4 = pd.DataFrame()
                    name = 'col_secondaries'
                    
                    secoDataFiles = [os.path.join(root, file) for file in files if re.findall('_seco_ntuple.out', file) and re.findall('_coll', file)]
                    if verbose: print ("list of files:", secoDataFiles)
                    
                    self.aperList = []; self.beamList = []; self.beamSizes = []
                    for file in secoDataFiles:
                        
                        tmp_df = self.getBeam_and_Aper_Info(file)
                        
                        if verbose: print ("    --> appending file:", file, "...")
                        DatFrame4 = DatFrame4.append(tmp_df)
                    
                    if DatFrame4.empty: print ("WARNING: DatFrame4 empty!")
                    else: 
                        DatFrame4['optics'] = opticsList[j]
                        frameList.append(DatFrame4)
                        print ("DatFrame4 appended")
                        j += 1                
                
                else:
                    raise RuntimeError('Invalid choice of "datType" and/or "read"')
                
        
        if frameList == []: raise ValueError('No data collected. List of frames empty:', frameList) 
        
        GlobDatFrame = GlobDatFrame.append(frameList)
        
        if GlobDatFrame.empty: print ("WARNING: overall dataframe empty!")
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
            -- df:      dataframe to work on
            -- optics:  choose which otics to be put into the new frame, defaults to 'all'
        
        returns: another frame, holding only data from selected optics
        """
        df = self.df
        
        
        df_opt = pd.DataFrame()
        df_opt.name = df.name
        tmpList = []
        
        if optics == 'all':
            df_opt = df
        else:
            if verbose: print ("-*-*-*-*-*-*-*-*-*-*-*-*-*- \n Following frame(s) selected: \n", optics)
            
            for opt in optics:
                tmp_df = df[df.optics == opt]
                tmpList.append(tmp_df)
                if verbose >1: print  (tmp_df.head())
            if tmpList == []: raise RuntimeError('No data collected. List of frames empty:', tmpList)
        
            else:
                df_opt = df_opt.append(tmpList)
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

# read twiss files, should be as flexible as possible

def read_twiss(twissFile, verbose=0):
    """
    Function to read general twiss files.
    """

    df = pd.read_table(twissFile, sep = "\s+", skiprows = 45, index_col = False) 
    
    # read columns and drop the first one (*) to actually match the right header
    #
    cols = df.columns
    twissHeader = cols[1:]
    
    # drop NaN column and reset header
    #
    df = df.dropna(axis = 1, how='any')
    df.columns = twissHeader
    
    df = df.drop(df.index[0])
    df = df.convert_objects(convert_numeric = True)
    
    if verbose:
        print("----------------------------------")
        print(" DF contains: \n", df.keys(), "\n data tpes are: \n", df.dtypes)
        print("----------------------------------")
        
    return df

def read_survey(surveyFile):
    """
    Function to read general survey files.
    """

    surveyHeader = ['S', 'X', 'Y', 'Z', 'THETA', 'PHI', 'PSI']
    
        

            

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
        
        for element in files:
            if element.endswith('seco_ntuple.out'):
                dataFiles.append(element)
    # write out apertures
    #
    for i in dataFiles:
        aper = re.findall(r'\D(\d{4})\D', i) 
        aperlist.append(int(aper[0]))
    
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

    
