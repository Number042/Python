import sys
import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)
import pandas as pd

class Tracking:
    
    """
    Tool kit to do extended selection on tracking information from G4
    """
    
    def __init__(self, verbose):
        self.verbose = verbose
        
    def collectInfo(self, df ):
        """
        Method to collect basic information from the .out of G4 in arrays (basically for plotting)
            -- frame:   refers to the data frame object resulting from a groupby operation
        """
        
        if self.verbose == 1: 
            print ("Selected frame contains: \n", " ------------------------ \n", df.head())
    
        elif self.verbose > 1: 
            print ("collectInfo(), line: ", sys._getframe().f_lineno)
            print ("Selected frame complete: \n", " ------------------------ \n", df)
        
        event_last = 999999999
        track_last = 999999999
 
        # initiate all necessary arrays -- SLOW --> IMPROVE !!
        # get_value is deprecated and likely to be removed in future releases. This can lead to broken code!
        # at[] or .iat[] both seem slower than get_value() ==> keep get_value() for now. 
        #
        Z_pos = []; Z_org = []; Z_hit = []
        E_org = []; E_hit = []

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
                
                
        if self.verbose > 1: print("Collected data in \n", "Z_pos: \n ------------------------- \n", Z_pos, "\n Z_org: \n ------------------------- \n", Z_org, "\n Z_hit: \n ------------------------- \n", Z_hit) 
        
        # returns a tuple of lists
        #
        return Z_pos, Z_org, Z_hit, E_org, E_hit

