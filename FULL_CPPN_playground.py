"""This file contains all code for creating the playground for
CPPN using the Tkinter python GUI library.

The GUI contains a graph of the nodes genotype and phenotype
and a text box included to change the values of the CPPNs 
weights for given connections.
"""

import tkinter as tk
from tkinter import simpledialog
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
num_x = 50
num_y = 50


class Playground(tk.Tk):
	"""Main class that contains all handlers for
	the Tkinter GUI
	"""

	def __init__(self, genotype):
		"""Contructer for main GUI container/handler"""

		# instantiate the root
		tk.Tk.__init__(self)
		self.title("CPPN playground")

		# create container to hold all grames in the GUI
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		# initiate GUI

		# add menu bar for the separate Tk frame
		menubar = tk.Menu(self)
		filemenu = tk.Menu(menubar)
		filemenu.add_command(label="Main Page", command=lambda: self.raise_frame("MainPage", container))
		filemenu.add_command(label="Slider Page", command=lambda: self.raise_frame("SliderPage", container))
		filemenu.add_command(label="Save", command=lambda: save_gen_GUI(genotype))
		menubar.add_cascade(label="Options", menu=filemenu)
		self.config(menu=menubar)

		# add frames to the main GUI
		self.frames = {}

		# create main frame
		frame1 = MainPage(container=container, master=self, genotype=genotype)
		self.frames["MainPage"] = frame1
		frame1.grid(row=0, column=0, stick="nsew")

		# raise main page to the front initially
		self.raise_frame("MainPage", container)


	def raise_frame(self, page_name, container):
		"""Raise a certain frame to the front of the GUI
		based on its page_name
		"""

		# find innovation numbers if slider page is being started
		# must initialize the slider page each time because properties are different
		if(page_name == "SliderPage"):
			frame2 = SliderPage(container=container, master=self, genotype=genotype)
			self.frames["SliderPage"] = frame2
			frame2.grid(row=0, column=0, sticky="nsew")
			frame2.add_sliders()
		frame = self.frames[page_name]
		frame.tkraise()



class MainPage(tk.Frame):
	"""class defining the main page handler/container of the CPPN playground GUI"""

	def __init__(self, container, master, genotype):
		"""Constructor for the main GUI frame"""

		# instantiate the frame
		tk.Frame.__init__(self, container)
		
		# connect frame to the controller
		self.controller = master

		f = Figure(figsize=(10, 10), dpi=100)
		subp_1 = f.add_subplot(211)
		subp_2 = f.add_subplot(212)

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
		canvas = FigureCanvasTkAgg(f, self)
		canvas.show()
		canvas.get_tk_widget().pack()

		# create labels for text entry and text entry
		tk.Label(self, text="Innovation Number").pack(pady=(10,0))
		tk.Label(self, text="New Weight").pack()
		innov_e = tk.Entry(self)
		weight_e = tk.Entry(self)
		innov_e.pack(pady=(10,0))
		weight_e.pack()

		# create buttons for exit and entry b      genotype, E1, subp_1, subp_2, norm_in, canvas
		tk.Button(self, text="Apply", command=(lambda: update_CPPN(genotype, innov_e, weight_e, subp_1, subp_2, norm_in, num_x, num_y, canvas))).pack()
		tk.Button(self, text="Sweep Weight", command=(lambda: sweep_CPPN(genotype, innov_e, subp_1, subp_2, norm_in, canvas))).pack()
		tk.Button(self, text="Exit", command=self.quit).pack(pady=(20,10))


class SliderPage(tk.Frame):
	"""Class containing frame for GUI widget that allows 
	users to move sliders to change weights within the CPPN
	"""

	def __init__(self, container, master, genotype):
		"""Constructor for slider frame"""
		tk.Frame.__init__(self, container)

		# must make subplots and canvas instance variables so that the making sliders 
		# method can access them
		# create CPPN graphs to pack onto the GUI
		f = Figure(figsize=(10, 10), dpi=100)
		self.subp_1 = f.add_subplot(211)
		self.subp_2 = f.add_subplot(212)

		# create graphs of genotype and phenotype
		graph_genotype_GUI(genotype, self.subp_2)
		# get outputs for current genotype
		norm_in = getNormalizedInputs(num_x, num_y)
		outputs = []
		for ins in norm_in:
			outputs.append(genotype.getOutput(ins)[0])
		outputs_np = np.array(outputs, copy=True)
		self.subp_1.imshow(np.reshape(outputs_np, (num_x, num_y)), cmap='Greys')

		# create canvas for GUI
		self.canvas = FigureCanvasTkAgg(f, self)
		self.canvas.show()
		self.canvas.get_tk_widget().pack()

		# initialize dictionary of sliders
		self.scale_dict = {}

		# connect frame to the root
		self.controller = master

	def add_sliders(self):
		"""Adds all needed slider items to the slider
		page of the GUI"""

		self.scale_dict = {}
		innov_str = simpledialog.askstring("Get Innovations.", 
			"What innovation numbers do you want sliders for (separate with commas)?")
		innov_nums = innov_str.split(",")
		for innov in innov_nums:
			self.scale_dict[innov] = tk.Scale(self, from_=-20, 
				to=20, orient=tk.HORIZONTAL)
			tk.Label(self, text="Slider for #{0}".format(innov)).pack()
			self.scale_dict[innov].pack(pady=10)
		tk.Button(self, text="Apply", command=lambda: self.slider_update_CPPN()).pack()


		tk.Button(self, text="Exit", command=self.quit).pack(pady=(20,10))

	def slider_update_CPPN(self):
		"""Pulls weight values from all sliders and updates
		the corresponding weights within the CPPN genotype, 
		then regraphs the plot of the CPPN genotype and 
		phenotype
		"""

		# get needed CPPN inputs
		norm_in = getNormalizedInputs(num_x, num_y)

		keys = list(self.scale_dict.keys())
		# for each connection with a slider, update weight to its current value
		for innov_num in keys:
			innov_num_int = int(innov_num)
			for con in genotype.connections:
				if(con.getInnovationNumber() == innov_num_int):
					con.setWeight(self.scale_dict[innov_num].get())

		# replot the CPPN with new weights
		# both subplots must be cleared to replace them with new ones
		self.subp_1.clear()
		self.subp_2.clear()

		outputs = []
		for ins in norm_in:
			outputs.append(genotype.getOutput(ins)[0])
		outputs_np = np.array(outputs, copy=True)
		self.subp_1.imshow(np.reshape(outputs_np, (num_x, num_y)), cmap='Greys')

		graph_genotype_GUI(genotype, self.subp_2)

		self.canvas.show()
		self.canvas.get_tk_widget().pack()


def save_gen_GUI(genotype):
	"""Method for saving the current state of a genotype 
	to a file that can be accessed later using pickle.
	"""

	filename = simpledialog.askstring("Get filepath.", "Where do you want the file to be saved?")
	# make sure user did not cancel request for filepath
	if(filename != None):
		genotype.save(filename)



def sweep_CPPN(genotype, E1, subp_1, subp_2, norm_in, canvas):
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
	genotype = Genotype(2,1)
	app = Playground(genotype)
	app.mainloop()