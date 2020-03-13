import matplotlib as mpl

myColors = ['royalblue', 'orangered', 'darkseagreen', 'peru', 'teal', 'orange','red', 'green', 'blue', 'lime','slategray']
myStyle = ['-', ':', '--', '-.', '-', ':']

# --------------------------- RC PARAMS STYLE SECTION -------------------------------------
mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['axes.labelsize'] = 26
mpl.rcParams['axes.titlesize'] = 28  
mpl.rcParams['figure.figsize'] = 15., 10.    # figure size in inches
mpl.rcParams['xtick.labelsize'] = 24 
mpl.rcParams['ytick.labelsize'] = 24 
mpl.rcParams['legend.fontsize'] = 16
mpl.rcParams['agg.path.chunksize'] = 10000
# --------------------------- ----------------------- -------------------------------------

# functions to align two y axis, given that twinx was chosen
#
def align_yaxis(ax1, v1, ax2, v2):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    adjust_yaxis(ax2,(y1-y2)/2,v2)
    adjust_yaxis(ax1,(y2-y1)/2,v1)
    
def adjust_yaxis(ax,ydif,v):
    """shift axis ax by ydiff, maintaining point v at the same location"""
    inv = ax.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, ydif))
    miny, maxy = ax.get_ylim()
    miny, maxy = miny - v, maxy - v
    if -miny>maxy or (-miny==maxy and dy > 0):
        nminy = miny
        nmaxy = miny*(maxy+dy)/(miny+dy)
    else:
        nmaxy = maxy
        nminy = maxy*(miny+dy)/(maxy+dy)
    ax.set_ylim(nminy+v, nmaxy+v)