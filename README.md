## GPP Commit Analysis

To perform the commit analysis, first perform the raw vector generation of the github commits:

```shell
cd ./Diffs_new/
python ./new_cluster.py
```

This will generate two processed files `commits2.pkl` and `vectors2.npy` that are required in later analysis. **Notice that these two files are already included in the repo and you can use them directly.**

Then process the malicious code snippets:

```shell
cd ./Diffs_malicious/
python ./new_cluster.py
```

This will generate two processed files `mcommits2.pkl` and `mvectors2.npy` that are required in later analysis. **These two files are also included in the repo and you can use them directly.**

So to perform the actual analysis, locate to `Diffs_new/Analysis.ipynb` and use Jupyter Lab/Notebook to load the notebook. There are three code sections:

1. **Common Section**: This is required for data loading and pre-processing. You should run the whole section every time you want to perform analysis.
2. **SparsePCA + K-Means**: This section performs the PCA dimension reduction and K-Means.
3. **SparsePCA + DBSCAN**: This section performs the PCA dimension reduction and DBSCAN.

Run the **Common Section** every time you start new analysis, and choose one of the remaining section to run, and you will get the final results. You can also tune the parameters (e.g., `n_clusters`) after observing the visualization results to get better fitting results.