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

from FULL_CPPN_getpixels import getNormalizedInputs
from FULL_CPPN_struct import Genotype
from FULL_CPPN_constants import NODE_TO_COLOR, CLOSENESS_THRESHOLD, PATCH_LIST


def init_playground(genotype, num_x, num_y):
	"""Main function for the playground
	that contains the main GUI animation 
	loop and all Tk config
	"""

	# initiate figure and subplot needed for graphing
	f = Figure(figsize=(10, 10), dpi=100)
	subp = f.add_subplot(211)

	# initiate GUI
	master = tk.Tk()
	master.title("CPPN Playground")

	# create graphs of genotype and phenotype
	
	graph_genotype_GUI(genotype, f)
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


def graph_genotype_GUI(genotype, f):
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

	# create matplotlib figure used for graph
	subp = f.add_subplot(212)
	
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