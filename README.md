# ML Pipeline Placement System
Placement system for ML pipelines on heterogeneous environments.

## Upload datasets to NFS Server
To upload a dataset to the NFS server, first the dataset must be in a folder in the ```data/``` directory. Then, run the following command:

```bash
.utils/nfs.sh upload <dataset_folder>
```

To remove a dataset from the NFS server, run the following command:

```bash
.utils/nfs.sh remove <dataset_name>
```
