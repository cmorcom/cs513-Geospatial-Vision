Command line format should be:

python .\satellite-retrieval.py [x1] [y1] [x2] [y2] [detail-level] 

	optional args: [-d <tile directory>] [-s <map filename>] [-v]
		- use -d to specify a (non-default) directory to store the tile data
		- use -s to specify a (non-default) map filename
		- use -v to display verbose messages

example (creates a 4352x8074 pixel aerial view of IIT):
python .\satellite-retrieval.py -87.629563 41.831082 -87.623598 41.839606 20 -d iit-tiles -v -s map_of_IIT.jpeg


Note: please use a detail-level of less than 20 unless you know all tiles in the region have a higher detail level
