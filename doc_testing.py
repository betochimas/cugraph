import glob
import doctest
import cugraph
import python.cugraph.cugraph as cugraph
import cudf

relativepath = "python/cugraph/cugraph/"
#modules = glob.glob(relativepath + "[!_][!tests]**/")

"""
allmodules = ["centrality/", "comms/", "community/", "components/", "cores/", 
                "dask/", "generators/", "internals/", "layout/", "linear_assigment/", 
                "link_analysis/", "link_prediction/", "proto", "sampling/", 
                "structure/", "structure/graph_implementation/", "traversal/", 
                "tree/", "utilities/"]
"""

premodules = ["generators/", "layout/", "linear_assignment/"]

modules = [relativepath+module for module in premodules]

for module in modules:
    #print(module)
    modulefiles = glob.glob(module + "[!_]**.py", recursive=True)
    print(modulefiles)
    for file in modulefiles:
        print("Testing " + file)
        print(doctest.testfile(file))

