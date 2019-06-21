import pandas as pd
import re

class DataSelection:
    
    """
    Tool-kit to refine selection on overall input data. Takes one DF to be processed and this DF is then 
    updated along the way.
    """
    
    def __init__(self, df, verbose):
        self.df = df
        self.verbose = verbose
        self._optics = []
        self._collimation = 0

        # cleanup section: drop columns from received DF that are not required
        self.df.drop( ['mass','seco_pos_eutags', 'xp_eu', 'yp_eu', 'zp_eu', 'Bx_eu', 'By_eu', 'Bz_eu', 'trklen', 'steplen'], axis = 1, inplace = True)


    # STEP 1 -- select a machine and eventually specific optics
    #
    def opticsSelection(self, optics = 'all' ):
        """
        Function to select specific optics, put these into a new dataframe that can be passed for further processing. 
            -- optics:  choose which otics to be put into the new frame. Can be general or specific
            -- verbose: set output level for user information
        RETURN: another frame, holding only data from selected optics but still class object?
        """
        self._optics = optics
        if optics == [] or optics == 'all': 
            self._optics = self.df.optics.unique()
            print('Optics list is empty, inferring from DF:', self._optics)
        
        # set up empty list, looping specified optics and appending to self.df_opt
        #
        self.df_opt = pd.DataFrame()
        tmpList = []

        if self.verbose: 
            print ("-*-*-*-*-*-*-*-*-*-*-*-*-*- \n Following frame(s) selected:")
            for optic in self._optics: print("--", optic)
        
        for opt in self._optics: tmpList.append( self.df[self.df.optics.str.contains(opt)] )
        
        if tmpList == []: raise RuntimeError('No data collected. List of frames empty:', tmpList)
        else:
            self.df_opt = self.df_opt.append(tmpList)
            self.df_opt.name = self.df.name

        if re.findall('col', self.df_opt.name):
            self._collimation = 1
            print ("Found collimator frame - groupby 'CollDim' \n", "-----------------------------")
        else:
            self._collimation = 0
            print ("Found no collimator frame - analysing default data \n", "-----------------------------")
        
    
        # do the slicing based on Creator and charge to secure synchrotron radiation -- mlu 11-21-2017 now hardcoded!
        #
        self.df_opt = self.df_opt[(self.df_opt.Creator == 'SynRad') & (self.df_opt.charge == 0)]
        self.df_opt.name = self.df.name

        return self.df_opt

    def splitNames( self ):
        """
        Function to split the content of the 'Name' column that is written in the default frame by 'readG4out' and 'opticsSelection'.
        It splits the strings of that column into 4 different columns for element, type, number and vacuum.

        RETURNS: a frame with appended columns holding the splitted content
        """
        if self.verbose == 1: 
            print ("-*-*-*-*-*-*-*-*-*-*-*-*-*- \n Selected following data frame:", self.df_opt.name)
        elif self.verbose > 1:
            print (self.df_opt.head())
            print (self.df_opt.Name)
        
        # mlu -- 11-22-2018 -- new implementation of split names:
        # --> split 'Name' and reuse for shorter element name
        # --> split 'OrigVol' and replace with its plain name
        #
        maxlen = self.df_opt.Name.str.split('_').map(len).max()
        if self.verbose: print( 'maximum number of parts in Name:', maxlen )
        if maxlen < 4:
            self.df_opt['Name'], self.df_opt['type'], self.df_opt['vacuum'] = self.df_opt['Name'].str.split('_', maxlen).str 
        elif maxlen >= 4:            
            self.df_opt['Name'], self.df_opt['type'], self.df_opt['number'], self.df_opt['vacuum'] = self.df_opt['Name'].str.split('_', maxlen).str 
            
        if 'OrigVol' not in self.df_opt.keys(): raise KeyError('No column named OrigVol')
        else: self.df_opt['OrigVol'] = self.df_opt['OrigVol'].str.split('_').str[0]
        
        return self.df_opt
    

    # STEP 2 -- check for collimation data and make first selection
    # check for collimation and use switch for groupby further below
    #
    def elmSelection( self, elements = [], origins = [] ):
        """
        Function to select certain elements. Can be useful for plotting to demonstrate effects of or on
        single Elements
            -- elements:    list of names, defaults to all which leaves the frame untrouched
            -- origins:     list of names for selection on OrigVol, different from 'elements'

        RETURNS: sliced DF, according to element selection
        """

        # additional option to select certain element(s), has to be able to accept a list
        # 
        if elements != [] and origins != []:
            raise KeyError(' *** elements and origins cannot be used in parallel!')
        elif not elements == []:
            self.df_opt = self.df_opt[ self.df_opt.Name.isin(elements) ] 
        elif not origins == []:
            self.df_opt = self.df_opt[ self.df_opt.OrigVol.isin(origins) ]
            
        
        # check result of selection above
        #   
        if self.verbose > 1: print ("Sliced data frame: \n", "----------------------------- \n", self.df_opt)
        
        # returns the UPDATED frame from opticsSelection!
        return self.df_opt

    # if verbose: print ("beam types:", self.beamTypes, '\n' "beam sizes:", self.beamSizes)
    def get_beamShapes_and_Size(self):
        """
        Function to read all beam types and sizes from a given frame. Allows to check for plotting if desired 
        type and/or size is/are available.

        RETURNS: list of available beam types and another of beam sizes
        """
        
        self.beamTypes = set(self.df_opt.BeamShape) 
        self.beamSizes = set(self.df_opt.BeamSize)
        
        if self.verbose: print ( "*-*-*-*-*-*-*-*-*-*-*-*-* \n Available types:", self.beamTypes, "\n Available sizes:", self.beamSizes )
        
        # maybe not required to pass them out of the class?
        return self.beamTypes, self.beamSizes

    def sliceFrame( self, beam = 'all', size = 'all', aperture = [] ):
        """
        Function to do sophisticated slicing on the DF produced by opticsSelection. Has to be used as LAST STEP.
            -- beam:    list of beam types, can be 'pencil', 'gauss', 'ring' or 'flat'; default 'all', accepts list
            -- size:    list of beam sizes; default 'all', accepts list
            -- aperture:    pass a list of apertures for selection. Accepts only 4-digit input like APHAPV as 2035. 
        
        RETURNS: a groupby object, grouped by optics, beam-type and -size.
        """
        # create selection based on aperture list
        #
        if aperture != []: self.df_opt = self.df_opt[self.df_opt.CollDim.isin(aperture)]; print( "selected apertures", aperture )
        
        # case 1
        #
        if beam == 'all' and size == 'all' or size == []:
                
            print ('selected all beam types and sizes!')
            
            if self._collimation: grouped = self.df_opt.groupby(['CollDim','optics','BeamShape','BeamSize'])
            else: grouped = self.df_opt.groupby(['optics','BeamShape','BeamSize']) 
            
        # case 2
        #
        elif beam == 'all' and size != 'all':
            DF = pd.DataFrame()
            
            for j in size:
                print ("All beam types of size", j, "selected")
                    
                if j in self.df_opt.BeamSize:
                    tmp = self.df_opt[self.df_opt.BeamSize == j] 
                    DF = DF.append(tmp)
                    if self.verbose: print (tmp.head())
                else:
                    raise KeyError("Selected beam size", j, "not in the list of available beam sizes:", self.df_opt.BeamSize.unique())
            
            if self._collimation: grouped = DF.groupby(['CollDim','optics','BeamSize'])
            else: grouped = DF.groupby(['optics','BeamSize'])

        # case 3    
        #
        elif beam != 'all' and size != 'all':
            
            DF = pd.DataFrame()
            framelist = []
            for i in beam:
                for j in size:
                    print ("Type", i, "selected, with size", j, "sigma")
                        
                    if i in self.df_opt.BeamShape and j in self.df_opt.beamSizes:
                        tmp = self.df_opt[(self.df_opt.BeamShape == i) & (self.df_opt.BeamSize == j)]
                        framelist.append(tmp)
                        
                        if self.verbose > 1: print (tmp)
                    
                    elif i not in self.df_opt.BeamShape:
                        raise KeyError("Selected beam type", i, "not in the list of available beams:", self.df_opt.BeamShape.unique())
                    elif j not in self.df_opt.BeamSize:
                        raise KeyError("Selected beam size", j, "not in the list of available beam sizes:", self.df_opt.BeamSize.unique())
            
            DF = DF.append(framelist)
            if self._collimation: grouped = DF.groupby(['CollDim','optics','BeamShape','BeamSize'])
            else: grouped = DF.groupby(['optics','BeamShape','BeamSize'])

        # case 4
        #
        elif beam != 'all' and size == 'all':
            
            DF = pd.DataFrame()
            for i in beam:
                print ("Type", i, "selected with all sizes.")
                
                if i in self.df_opt.BeamShape.unique():
                    tmp = self.df_opt[self.df_opt.BeamShape == i] 
                    DF = DF.append(tmp)
                    #if self.verbose: print (tmp.head())
                else:
                    raise KeyError("Selected beam type", i, "not in the list of available beams:", self.df_opt.BeamShape.unique())
            
            if self._collimation: grouped = DF.groupby(['CollDim','optics','BeamShape']) #,'BeamSize'])
            else: grouped = DF.groupby(['optics','BeamShape']) #,'BeamSize'])

        else:
            raise RuntimeError("Invalid selection of choice(s)!")

        # definitely required to available outside --> plottig or analysis
        return grouped


    
    # # Add function for aperture selection, pass this to plot_data if needed
    # # extend to more detailed data filtering?
    # #
    # def aper_select(self, aperture, verbose):
    #     """
    #     Function to do some data filtering.
    #         -- aperture:    allows to choose only certain dimensions; provided by calling function
    #         -- verbose:     set level of verbosity, also provided by calling function
        
    #     RETURN: dataframe grouped wrt to aperture selection
    #     """
        
    #     df = self.df
    #     dfName = df.name
        
    #     if verbose: print ( " -*-*-*-*-*-*-*-*-*-*-*-*- \n", dfName, "holds: \n", df.keys() )
        
    #     # create a list of available apertures from the frame
    #     #
    #     aperList = df.CollDim.unique()
    #     if verbose: print ( " -*-*-*-*-*-*-*-*-*-*-*-*- \n", "List of apertures: ", aperList )
        
    #     # slice out SR data from overall frame df
    #     # pass name from df to sliced df
    #     #
    #     self.df_opt = df[(df.Creator == 'SynRad') & (df.charge == 0)]
    #     self.df_opt.name = dfName
    
    #     # check the df name, if collimation data, groupby apertures
    #     #
    #     if re.findall('col', self.df_opt.name):
    #         print ("found collimator frame - groupby 'CollDim' \n ----------------------------- \n")
    #         if verbose: print ("available dimensions:", aperList)

    #     if aperture == 'all':
    #         # add the aperture option here?
    #         print ('selected all apertures!')
    #         grouped = self.df_opt.groupby(['CollDim', 'optics', 'BeamShape'])
            
    #     else:
    #         DF = pd.DataFrame()
            
    #         for i in aperture:
    #             print ('aperture selected:', i)
    #             if i in aperList:
    #                 tmp = self.df_opt[self.df_opt.CollDim == i]
    #                 # ~ hits = self.df_opt[(self.df_opt.) & ()]
    #                 DF = DF.append(tmp)
    #             else:
    #                 raise ValueError('Selected aperture', i, 'not in the list. Available are:', aperList)
                
    #         grouped = DF.groupby(['CollDim', 'optics', 'BeamShape']) 

    #     return grouped


    


