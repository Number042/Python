import sys
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
        
        if verbose == 1: 
            print ("Selected frame contains: \n", " ------------------------ \n", self.frame.head())
    
        elif verbose > 1: 
            print ("collectInfo(), line: ", sys._getframe().f_lineno)
            print ("Selected frame complete: \n", " ------------------------ \n", self.frame)
        
        event_last = 999999999
        track_last = 999999999
 
        # initiate all necessary arrays
        #
        Z_pos = []; Z_org = []; Z_hit = []; 
        E_org = []; E_hit = []
        srcName = []

        for row in self.frame.index:
            
            event = self.frame.get_value(row,'Event')
            track = self.frame.get_value(row,'Track')
            z_eu  = self.frame.get_value(row,'z_eu')
            mat   = self.frame.get_value(row,'Material')
            energ = self.frame.get_value(row,'ptot')
            process = self.frame.get_value(row, 'ProcName')
            creator = self.frame.get_value(row, 'Creator')
            
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
        
        # returns several lists
        #
        return Z_pos, Z_org, Z_hit
