"""This file contains all code for creating the playground for
CPPN using the Tkinter python GUI library.

The GUI contains a graph of the nodes genotype and phenotype
and a text box included to change the values of the CPPNs 
weights for given connections.
"""

import tkinter as tk
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import time

from FULL_CPPN_getpixels import getNormalizedInputs
from FULL_CPPN_struct import Genotype
from FULL_CPPN_constants import NODE_TO_COLOR, CLOSENESS_THRESHOLD, PATCH_LIST

# sets the time between updates when sweeping through weights in seconds
TIME_DELAY = 2


def init_playground(genotype, num_x, num_y):
	"""Main function for the playground
	that contains the main GUI animation 
	loop and all Tk config
	"""

	# initiate figure and subplot needed for graphing
	f = Figure(figsize=(10, 10), dpi=100)
	subp_1 = f.add_subplot(211)
	subp_2 = f.add_subplot(212)

	# initiate GUI
	master = tk.Tk()
	master.title("CPPN Playground")

	# create graphs of genotype and phenotype
	
	graph_genotype_GUI(genotype, subp_2)
	# get outputs for current genotype
	norm_in = getNormalizedInputs(num_x, num_y)
	outputs = []
	for ins in norm_in:
		outputs.append(genotype.getOutput(ins)[0])
	outputs_np = np.array(outputs, copy=True)
	subp_1.imshow(np.reshape(outputs_np, (num_x, num_y)), cmap='Greys')

	# create canvas for GUI
	canvas = FigureCanvasTkAgg(f, master)
	canvas.show()
	canvas.get_tk_widget().pack()

	# create labels for text entry and text entry
	tk.Label(master, text="Innovation Number").pack(pady=(10,0))
	tk.Label(master, text="New Weight").pack()
	innov_e = tk.Entry(master)
	weight_e = tk.Entry(master)
	innov_e.pack(pady=(10,0))
	weight_e.pack()

	# create buttons for exit and entry
	tk.Button(master, text="Set Weight", command=(lambda: update_CPPN(genotype, innov_e, weight_e, subp_1, subp_2, norm_in, num_x, num_y, canvas))).pack()
	tk.Button(master, text="Sweep Weights", command=(lambda: sweep_CPPN(genotype, innov_e, subp_1, subp_2, norm_in, num_y, num_y, canvas))).pack()
	tk.Button(master, text="Exit", command=master.quit).pack(pady=(20,10))


	# initiate main loop for GUI
	tk.mainloop()


def sweep_CPPN(genotype, E1, subp_1, subp_2, norm_in, num_x, num_y, canvas):
	"""Sweeps over a range of weights for a certain connection to show the phenotype of 
	the CPPN with several different values for that weight
	"""

	# get value from widget field
	innov_num = E1.get()

	# find index of desired connection
	index = -1
	for con_ind in range(len(genotype.connections)):
		if(genotype.connections[con_ind].getInnovationNumber() == innov_num):
			index = con_ind
	old_weight = genotype.connections[con_ind].getWeight()

	sweep_weight = 10
	while(sweep_weight > -10):
		genotype.connections[con_ind].setWeight(sweep_weight)
		# clear both subplots so new graphs can be placed into the GUI
		subp_1.clear()
		subp_2.clear()

		# create graphs again and put graphs onto them
		outputs = []
		for ins in norm_in:
			outputs.append(genotype.getOutput(ins)[0])
		outputs_np = np.array(outputs, copy=True)
		subp_1.imshow(np.reshape(outputs_np, (num_x, num_y)), cmap='Greys')

		graph_genotype_GUI(genotype, subp_2)

		canvas.show()
		canvas.get_tk_widget().pack()
		sweep_weight -= .5
		time.sleep(TIME_DELAY)

	# reset the graphs to their old state with the original weight
	genotype.connections[con_ind].setWeight(old_weight)
	# clear both subplots so new graphs can be placed into the GUI
	subp_1.clear()
	subp_2.clear()

	# create graphs again and put graphs onto them
	outputs = []
	for ins in norm_in:
		outputs.append(genotype.getOutput(ins)[0])
	outputs_np = np.array(outputs, copy=True)
	subp_1.imshow(np.reshape(outputs_np, (num_x, num_y)), cmap='Greys')

	graph_genotype_GUI(genotype, subp_2)

	canvas.show()
	canvas.get_tk_widget().pack()



def update_CPPN(genotype, E1, E2, subp_1, subp_2, norm_in, num_x, num_y, canvas):
	"""Function for taking values from the user 
	and using them to update weight values in the 
	CPPN - user chooses new weight for a certain
	connection/innov num
	"""

	# get values from fields, should all be comma separated
	innov_nums = E1.get().split(",")
	new_weights = E2.get().split(",")

	# get all values from the above lists
	for innov_num, new_weight in zip(innov_nums, new_weights):
		# search through connections to find the correct
		# weight to change
		for con in genotype.connections:
			if(con.getInnovationNumber() == int(innov_num)):
				con.setWeight(float(new_weight))

	# clear both subplots so new graphs can be placed into the GUI
	subp_1.clear()
	subp_2.clear()

	# create graphs again and put graphs onto them
	outputs = []
	for ins in norm_in:
		outputs.append(genotype.getOutput(ins)[0])
	outputs_np = np.array(outputs, copy=True)
	subp_1.imshow(np.reshape(outputs_np, (num_x, num_y)), cmap='Greys')

	graph_genotype_GUI(genotype, subp_2)

	canvas.show()
	canvas.get_tk_widget().pack()





def graph_genotype_GUI(genotype, subp):
	"""Function used to graph genotype of CPPN, function is same as
	the one inside of the CPPN structure function but can be added to
	a subplot of Figure f to be included in the GUI display for the
	playground

	Parameters:
	genotype -- genotype of CPPN being graphed
	f -- Figure instance into which the graph is being placed
	"""

	# create the networkx graph and associated node position for genotype
	graph = genotype.gen_networkx_graph()
	pos = genotype.gen_positions_for_networkx(graph)
	
	# add all nodes into graph with colors
	for node in genotype.nodes:
		color = NODE_TO_COLOR[node.getActKey()]
		nx.draw_networkx_nodes(graph, pos,
								ax=subp, 
								nodelist=[node.getNodeNum()],
								node_color=color,
								node_size=400, alpha=0.8)
	# add all connections into graph with colors
	for con in genotype.connections:
		 color = 'b' if con.getWeight() < 0 else 'r'
		 edge_tuple = (con.getNodeIn().getNodeNum(), 
		 				con.getNodeOut().getNodeNum())
		 nx.draw_networkx_edges(graph, pos,
		 						ax=subp,
		 						edgelist = [edge_tuple],
		 						width=3, alpha=0.5, 
		 						edge_color=color, arrows=True)
		
	# add innovation number labels for connections
	labels = nx.get_edge_attributes(graph, 'data')
	nx.draw_networkx_edge_labels(graph, pos, ax=subp, labels=labels)

	# create graph with title/legend and display
	plt.title("CPPN Genotype Visualization")
	subp.legend(handles=PATCH_LIST, loc='upper right')


if __name__ == '__main__':
	init_playground(Genotype(2, 1), 50, 50)