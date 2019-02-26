import matplotlib as mpl

myColors = ['royalblue', 'orangered', 'darkseagreen', 'peru', 'teal', 'orange']
myStyle = ['-', ':', '--', '-.', '-', ':']

# --------------------------- RC PARAMS STYLE SECTION -------------------------------------
mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['axes.labelsize'] = 24
mpl.rcParams['axes.titlesize'] = 26  
mpl.rcParams['figure.figsize'] = 15., 10.    # figure size in inches

mpl.rcParams['legend.fontsize'] = 16
mpl.rcParams['agg.path.chunksize'] = 10000
# --------------------------- ----------------------- -------------------------------------