"""Contains all helper functions for the off file segmentation code"""

def parse_label_segments(og_labels):
	"""parses a labeling format of off files that has a title followed
	by all points in the segment corresponding to that title, gets all
	of the numbers in each segment and turns them into a list (str originally)
	and returns a list of such lists where each index corresponds to
	a point in a segment
	"""
	
	# store each list of points in a result array
	result = []
	
	# parse each list of points
	for i in range(1, len(og_labels), 2):
		# separate the large string into all the separate points
		point_list = og_labels[i]
		point_list = point_list.split(" ")
		
		# last list element stores a newline character
		del point_list[len(point_list) - 1]
		
		# map all elements in the point list to an integer
		point_list = list(map(int, point_list))
		result.append(point_list)
		
	return result
		
def parse_vertices(face_list, labels):
	"""takes a 2D list of integers (labels) representing the segments for the
	the mesh and creates a list of vertices for each segment from the
	vertices list 

	results in a 2D array where each element in the 2D array is a list of faces
	(3 vertices each) corresponding to the mesh segment
	"""
	
	# each index stores a list of all faces for a segment
	segments = []
	
	# go through each set of vertices and grab all the vertices for
	# a corresponding segments
	for segment in labels:
		tmp_faces = []
		for face_num in segment:
			tmp_faces.append(face_list[face_num - 1])
		
		# append each segment into the overall list
		segments.append(tmp_faces)
	
	return segments
