"""This file is used to store several constants and 
lists/dictionaries that are used throughout the CPPN
code
"""

import matplotlib.patches as mpatches

# this dictionary stores which acitvation numbers corresponde
# to which colors when the CPPN is graphed
NODE_TO_COLOR = {0:'r', 1:'b', 2:'g', 3: 'c', 4:'m', 
				5:'y', 6:'k', 7:'orange', 8:'darkgreen'} 

# when CPPN is graphed, if nodes are closer than this amount
# they should be shifted to be closer apart
CLOSENESS_THRESHOLD = .9

# creates both lists needed for legend in CPPN genotype graphpatch1 = mpatches.Patch(color='#C0C0C0', label='No Act')
PATCH_LIST = [mpatches.Patch(color='r', label='Step'), mpatches.Patch(color='b', label='Sig'),
				mpatches.Patch(color='g', label='Relu'), mpatches.Patch(color='c', label='Sin'),
				mpatches.Patch(color='m', label='Gauss'), mpatches.Patch(color='y', label='Log'), 
				mpatches.Patch(color='k', label='Tanh'), mpatches.Patch(color='orange', label='Square'),
				mpatches.Patch(color='darkgreen', label='Abs')]
