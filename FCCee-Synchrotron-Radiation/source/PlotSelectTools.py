import sys
import pandas as pd
class Tracking:
    
    """
    Tool kit to do extended selection on tracking information from G4
    """
    
    def __init__(self, verbose, collimation):
        self.collimation = collimation
        self.verbose = verbose
        
    def collectInfo(self, df, verbose):
        """
        Method to collect basic information from the .out of G4 in arrays (basically for plotting)
            -- frame:   refers to the data frame object resulting from a groupby operation
        """
        
        if verbose == 1: 
            print ("Selected frame contains: \n", " ------------------------ \n", df.head())
    
        elif verbose > 1: 
            print ("collectInfo(), line: ", sys._getframe().f_lineno)
            print ("Selected frame complete: \n", " ------------------------ \n", df)
        
        event_last = 999999999
        track_last = 999999999
 
        # initiate all necessary arrays
        #
        Z_pos = []; Z_org = []; Z_hit = []; 
        E_org = []; E_hit = []
        srcName = []

        for row in df.index:
            
            event = df.get_value(row,'Event')
            track = df.get_value(row,'Track')
            z_eu  = df.get_value(row,'z_eu')
            mat   = df.get_value(row,'Material')
            energ = df.get_value(row,'ptot')
            process = df.get_value(row, 'ProcName')
            creator = df.get_value(row, 'Creator')
            
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
                
                
        if verbose > 1: print("Collected data in \n", "Z_pos: \n ------------------------- \n", Z_pos, "\n Z_org: \n ------------------------- \n", Z_org, "\n Z_hit: \n ------------------------- \n", Z_hit) 
        
        # returns a tuple of lists
        #
        return Z_pos, Z_org, Z_hit, E_org, E_hit

    def sliceFrame(self, df_sliced, beamTypes, beamSizes, beam, size, verbose):

        # case 1
        #
        if beam == 'all' and size == 'all' or size == []:
                
            print ('selected all beam types and sizes!')
            
            if self.collimation: grouped = df_sliced.groupby(['CollDim','optics','BeamShape','BeamSize'])
            else: grouped = df_sliced.groupby(['optics','BeamShape','BeamSize']) 
            
        # case 2
        #
        elif beam == 'all' and size != 'all':
            DF = pd.DataFrame()
            
            for j in size:
                print ("All beam types of size", j, "selected")
                    
                if j in beamSizes:
                    tmp = df_sliced[df_sliced.BeamSize == j] 
                    DF = DF.append(tmp)
                    if self.verbose: print (tmp.head())
                else:
                    raise KeyError("Selected beam size", j, "not in the list of available beam sizes:", beamSizes)
            
            if self.collimation: grouped = DF.groupby(['CollDim','optics','BeamSize'])
            else: grouped = DF.groupby(['optics','BeamSize'])

        # case 3    
        #
        elif beam != 'all' and size != 'all':
            
            DF = pd.DataFrame()
            framelist = []
            for i in beam:
                for j in size:
                    print ("Type", i, "selected, with size", j, "sigma")
                        
                    if i in beamTypes and j in beamSizes:
                        tmp = df_sliced[(df_sliced.BeamShape == i) & (df_sliced.BeamSize == j)]
                        framelist.append(tmp)
                        
                        if self.verbose > 1: print (tmp)
                    
                    elif i not in beamTypes:
                        raise KeyError("Selected beam type", i, "not in the list of available beams:", beamTypes)
                    elif j not in beamSizes:
                        raise KeyError("Selected beam size", j, "not in the list of available beam sizes:", beamSizes)
            
            DF = DF.append(framelist)
            if self.collimation: grouped = DF.groupby(['CollDim','optics','BeamShape','BeamSize'])
            else: grouped = DF.groupby(['optics','BeamShape','BeamSize'])

        # case 4
        #
        elif beam != 'all' and size == 'all':
            
            DF = pd.DataFrame()
            for i in beam:
                print ("Type", i, "selected with all sizes.")
                
                if i in beamTypes:
                    tmp = df_sliced[df_sliced.BeamShape == i] 
                    DF = DF.append(tmp)
                    #if self.verbose: print (tmp.head())
                else:
                    raise KeyError("Selected beam type", i, "not in the list of available beams:", beamTypes)
            
            if self.collimation: grouped = DF.groupby(['CollDim','optics','BeamShape']) #,'BeamSize'])
            else: grouped = DF.groupby(['optics','BeamShape']) #,'BeamSize'])

        else:
            raise RuntimeError("Invalid selection of choice(s)!")

        return grouped