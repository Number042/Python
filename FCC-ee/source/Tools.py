import matplotlib.pyplot as plt
from numpy import sqrt

# fuction to calculate S with IP in the center
#
def rel_s( df, row, Lmax = 0):
    """
    Shift the IP in the center of S. (KEK convention SAD, LER?)
    """
    if Lmax == 0:
        if row['S'] > df.S.max()/2:
            rel_s = row['S'] - df.S.max()  
        else:
            rel_s = row['S']
    else:
        if row['S'] > Lmax/2: rel_s = row['S'] - Lmax
        else: rel_s = row['S']
    
    return rel_s

# # old convention
#     def rel_s( self, df, row ):
#         """
#         Shift the IP in the center of S.
#         """
#         if row['S'] < df.S.max()/2:
#             rel_s = -row['S']
#         elif row['S'] > df.S.max()/2:
#             rel_s = df.S.max() - row['S']
        
#         return rel_s

def calcAper(s):
    r = 0.040
    if((-3.640000000 <= s) & (s < -2.725000000)): r = .040000000
    if((-2.725000000 <= s) & (s < -2.675000000)): r = (-0.100000) * s + (-.232500000)
    if((-2.675000000 <= s) & (s < -1.750000000)): r = .035000000
    if((-1.750000000 <= s) & (s < -1.630000000)): r = (-0.100000) * s + (-.140000000)
    if((-1.630000000 <= s) & (s < -1.590000000)): r = (-0.025000) * s + (-.017750000)
    if((-1.590000000 <= s) & (s < -1.252000000)): r = .022000000
    if((-1.252000000 <= s) & (s < -1.172000000)): r = (-0.100000) * s + (-.103200000)
    if((-1.172000000 <= s) & (s < -1.092000000)): r = (-0.006250) * s + (.006675000)
    if((-1.092000000 <= s) & (s <  -.620500000)): r = .013500000
    if(( -.620500000 <= s) & (s <  -.452000000)): r = (-0.020772) * s + (0.000611276)
    if(( -.452000000 <= s) & (s <  -.220000000)): r = (-0.021552) * s + (0.000258621)
    if(( -.220000000 <= s) & (s <  -.203340000)): r = (-0.002401) * s + (.004471789)
    if(( -.203340000 <= s) & (s <  -.112170000)): r = (0.003071) * s + (.005584495)
    if(( -.112170000 <= s) & (s <   .094990000)): r = (0.004007) * s + (.005689416)

    if(( .094990000 <= s) & (s <  .245000000)):   r = (0.026198) * s + (.003581428)
    if(( .245000000 <= s) & (s <  .620500000)):   r = (0.009321) * s + (.007716378)
    if(( .620500000 <= s) & (s < 1.092000000)):   r = .013500000
    if((1.092000000 <= s) & (s < 1.172000000)):   r = (0.006250) * s + (.006675000)
    if((1.172000000 <= s) & (s < 1.252000000)):   r = (0.100000) * s + (-.103200000)
    if((1.252000000 <= s) & (s < 1.590000000)):   r = .022000000
    if((1.590000000 <= s) & (s < 1.630000000)):   r = (0.025000) * s + (-.017750000)
    if((1.630000000 <= s) & (s < 1.750000000)):   r = (0.100000) * s + (-.140000000)
    if((1.750000000 <= s) & (s < 2.350000000)):   r = .035000000
    if((2.350000000 <= s) & (s < 2.400000000)):   r = (0.100000) * s + (-.200000000)
    if((2.400000000 <= s) & (s < 3.315000000)):   r = .040000000
    
    return r

# easier way to setup a subplot arrangement
#
def sbplSetUp(count, dim = [15,10], asp = 'auto'):
    """
    Create an array of subplots.
        -- count: number of generated plots
        -- dim: specify dimension of the matplotlib window
        -- asp: set aspect ratio, defaults to auto, equal can be chosen
    """
    plt.figure( figsize = (dim[0], dim[1]) )
    axs = []
    for i in range(count):
        if count == 3: 
            ax = plt.subplot( 331 + i ) 
        else: ax = plt.subplot( 321 + i ) 
        ax.set_aspect(asp)
        axs.append(ax)
    
    return axs

# quicker way to access twiss parameters for a given element
#
def readTwissParams(tfs, elm):
    i = 0
    with open( tfs ) as file:
        for line in file:
            if line.startswith(' \"%s\"' %elm):
                print('Element,', elm, 'at line', i)
                break
            i += 1
    return i

# add apertures in drift spaces to simplify plotting
#
def inventAper(s, name, aper, collAper ):
    """
    FCC specific function to invent apertures in DRIFT. Uses hard coded values for the moment (design report/mechanical design).
        -- s: S position along the accelerator
        -- name: element name
        -- aper: element aperture from TWISS
        -- collAper: invented aperture setting for collimators
    """
    centralPipeRad = 0.015
    genericPipeRad = 0.035

    if s >= 0 and s < 5.6: 
        if name.startswith('L000013') or name.startswith('IP') or name.startswith('SOL'): invAper = centralPipeRad
        elif name.startswith('DRIFT') and aper == 0: invAper = centralPipeRad
        else: invAper = aper 

    elif s > 5.6 and s < 8.2:
        if name.startswith('DRIFT') and aper == 0: invAper = 0.02
        else: invAper = aper 
            
    elif s > -8.2 and s < -5.6:
        if name.startswith('DRIFT') and aper == 0: invAper = 0.02
        else: invAper = aper 

    elif s > -5.6 and s <= 0:
        if name.startswith('L000013') or name.startswith('IP') or name.startswith('SOL'): invAper = centralPipeRad
        elif name.startswith('DRIFT') and aper == 0: invAper = centralPipeRad
        else: invAper = aper 
        
    elif name.startswith('COLL'): invAper = collAper
    
    else: invAper = genericPipeRad
    
    return invAper

# calculate the beam size based on emittance, beta function, dispersion and energy spread
#
def sigm(bet, disp, eps, delP, scaleXY):
            return sqrt( bet*eps + (disp*delP)**2 )*scaleXY

# critical energy for bends
#
# def epsCrit(gamma, rho):
#     return (3/2*hbar*speed_of_light*gamma**3/rho)/elementary_charge

# radii = [151.631e3, 144.688e3]
# epsC= [ epsCrit(Lrnt, rh)/1e3 for rh in radii] 

import re
def collSet( geomFile, collName, collh, thickness, verbose = 0 ):
    """
    Tool to change aperture in the geometry in the GDML directly. 
    ! Needs to have geometry with collimator closed a bit to have CONE - TUBE - CONE section !
        -- geomFile: geometry to work on
        -- collName: collimator which settings are supposed to be changed
        -- collh: aperture
        -- thickness: beam pipe thickness (material)
        -- verbose: info-output level
    """
    with open( geomFile, "r") as sources:
        lines = sources.readlines()
        
    with open( geomFile, "w") as sources:
        i = 0
        for line in lines:

            if collName in line: 
                if verbose: print('collimator (vac) at lines[', i, ']')
                sources.write( re.sub('rmax="\d+.\d+"', 'rmax="%s"' %str(collh), line) )
                if verbose > 1: print('writing new rmax to line', line)

            elif 'COLL' in line and collName in lines[i+1]:
                if verbose: print('collimator (mat) at lines[', i+1, ']')
                sources.write( re.sub('rmax="\d+.\d+"', 'rmax="%s"' %str(collh + thickness), line) )
                if verbose > 1: print( 'writing new rmax (material thickness) to line', line )
                    
            elif 'DRIFT' in line and collName in lines[i+2]: 
                if verbose: print('drift (vac) with collimator at lines[',i+2,']')
                sources.write( re.sub('rmax2="\d+.\d+"', 'rmax2="%s"' %str(collh), line) )
                if verbose > 1: print('writing new rmax2 to line', line)
            
            elif 'DRIFT' in line and collName in lines[i+3]:
                if verbose: print('drift (mat) with collimator at lines[', i+3, ']')
                sources.write( re.sub('rmax2="\d+.\d+"', 'rmax2="%s"' %str(collh + thickness), line) )
                if verbose > 1: print('writing new rmax2 to line', line)
            
            elif 'DRIFT' in line and collName in lines[i-1]: 
                if verbose: print('drift (mat) with collimator at lines[',i-1,']')
                sources.write( re.sub('rmax1="\d+.\d+"', 'rmax1="%s"' %str(collh + thickness), line) )
                if verbose > 1: print( 'writing new rmax1 (material thickness) to line', line )
                    
            elif 'DRIFT' in line and collName in lines[i-2]: 
                if verbose: print('drift (vac) with collimator at lines[',i-2,']')
                sources.write( re.sub('rmax1="\d+.\d+"', 'rmax1="%s"' %str(collh), line) )
                if verbose > 1: print('writing new rmax1 to line', line)
                
            else: sources.write( line )
            i += 1
    return 0

from numpy import exp
def Gauss(x):
    return x*exp(-x**2/2)

from numpy import log
def tail(y1, y2, N):
    return y1 - log(y2 + 1/exp(N - 1))

