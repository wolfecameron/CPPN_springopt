"""This file contains all code for creating the playground for
CPPN using the Tkinter python GUI library.

The GUI contains a graph of the nodes genotype and phenotype
and a text box included to change the values of the CPPNs 
weights for given connections.
"""

import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from FULL_CPPN_getpixels import getNormalizedInputs
from FULL_CPPN_struct import Genotype


def init_playground(genotype, num_x, num_y):
	"""Main function for the playground
	that contains the main GUI animation 
	loop and all Tk config
	"""

	# initiate figure and subplot needed for graphing
	f = Figure(figsize=(5,5), dpi=100)
	subp = f.add_subplot(111)

	# initiate GUI
	master = tk.Tk()
	master.title("CPPN Playground")

	# create graphs of genotype and phenotype
	
	#genotype.graph_genotype()
	# get outputs for current genotype
	norm_in = getNormalizedInputs(num_x, num_y)
	outputs = []
	for ins in norm_in:
		outputs.append(genotype.getOutput(ins)[0])
	outputs_np = np.array(outputs, copy=True)
	subp.imshow(np.reshape(outputs_np, (num_x, num_y)), cmap='Greys')

	# create canvas for GUI
	canvas = FigureCanvasTkAgg(f, master)
	canvas.show()
	canvas.get_tk_widget().pack()

	# create labels for text entry and text entry
	tk.Label(master, text="Innovation Number").pack()
	tk.Label(master, text="New Weight").pack()
	innov_e = tk.Entry(master)
	weight_e = tk.Entry(master)
	innov_e.pack()
	weight_e.pack()

	# create buttons for exit and entry
	tk.Button(master, text="Exit", command=master.quit).pack()
	tk.Button(master, text="Submit", command=(lambda: update_CPPN(genotype, innov_e, weight_e))).pack()

	# initiate main loop for GUI
	tk.mainloop()



def update_CPPN(E1, E2):
	"""Function for taking values from the user 
	and using them to update weight values in the 
	CPPN - user chooses new weight for a certain
	connection/innov num
	"""

	# get values from fields
	innov_num = E1.get()
	new_weight = E2.get()
	print(innov_num)
	print(new_weight)
	input()

	# search through connections to find the correct
	# weight to change
	for con in genotype.connections:
		if(con.getInnovationNumber() == int(innov_num)):
			con.setWeight(float(new_weight))


if __name__ == '__main__':
	init_playground(Genotype(2, 1), 50, 50)