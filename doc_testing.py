import glob
import doctest
import cugraph
import python.cugraph.cugraph as cugraph
import cudf

relativepath = "python/cugraph/cugraph/"


# Look for doc strings in non-special (__xx__.py) and non-testing files
non_underscored = set(glob.glob(relativepath+"**/[!_]*.py", recursive=True))
testfiles1 = set(glob.glob(relativepath+"**/tests/**/[!_]*.py", recursive=True))
testfiles2 = set(glob.glob(relativepath+"**/test/[!_]*.py", recursive=True))
testfiles3 = set(glob.glob(relativepath+"**/test**.py", recursive=True))

filtered = non_underscored - testfiles1 - testfiles2 - testfiles3
print(len(filtered))

# Look at non-special .py files in 'traversal' module, recursive not need be True in this case
traversalfiles = glob.glob(relativepath + "traversal/[!_]**.py", recursive=True)
treefiles = glob.glob(relativepath + "tree/[!_]**.py", recursive=True)
utilityfiles = glob.glob(relativepath + "utilities/[!_]**.py", recursive=True)
structurefiles = glob.glob(relativepath + "structure/[!_]**.py", recursive=True)

for file in structurefiles:
    print("Testing " + file)
    print(doctest.testfile(file))
