"""Segments off files into several off files based on the results of the segmentation stored in
a separate txt file"""

from seg_help import parse_label_segments, parse_vertices

# file paths to the off file and the labels file
DIR_PATH = "/home/wolfecameron/Desktop/shape_seg/PSB_COSEG_MESHES/cosegCandelabra/"
OFF_FILE_NAME = "model10.off"
LABEL_FILE_NAME = "model10_labels.txt" 

# open the files to be used for segmentation
with open(DIR_PATH + OFF_FILE_NAME, "r") as off_file:
	with open(DIR_PATH + LABEL_FILE_NAME, "r") as label_file:
		# read text from each of the respective files
		off_cont = off_file.readlines()
		del off_cont[0] # 0 and 1 do not contain vertices
		del off_cont[0]
		label_cont = label_file.readlines()
		segments = parse_label_segments(label_cont)
		# get faces for each segment corresponding to labels
		segment_faces = parse_vertices(off_cont, segments)
		
		print(segment_faces[0])
