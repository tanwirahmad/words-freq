## Parse VOSViewer

The __parse_viewer.py__ script requires a corpus file (i.e., collection of all the documents), VOSViewer generated map and network file. The script will generate an image file to visulize the clusters (described in the map and network files) including documents indexes. Further, the script also presents the cluster information in a textual format.

### Optional Requirement
If you want to generate a graph of clusters, you need to install `pygraphviz` python library. You can use the following command to install it using `pip`:

```pip install pygraphviz```

Read more about installation at http://pygraphviz.github.io/documentation/latest/install.html