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

## Placement strategies

The current implementation of the placement strategy is divided into two main steps:
1. The placement itself, which is responsible for selecting the suitable node for each component
2. The scheduling, which is responsible for selecting the order in which the pipelines are executed

### Placement
The placement strategy is responsible for selecting the suitable node for each component of the pipeline. The implemented strategy follows a heuristic approach.

To place the preprocessing components, the system heavily relies on the size of the dataset, more specifically, the size that the dataset in memory. To estimate the size that a dataset will take in memory, we rely on the number of samples of the dataset and the type of each feature. To select the best node to preprocess the dataset, we check which node has sufficient memory to store the dataset in memory plus an additional overhead of 50% of the dataset size (add as server parameter). The selection process also considers the current memory usage of the node.

For training components, we considered the following heuristics:
- If the model is a traditional model (lr, linr, and dt), the system selects a node from "low" to "med"
- If the model is a ensemble model (rf) or a support vector machine (svm), the system selects a node from "med"
- If the model is a deep learning model (nn, cnn), the system selects a node from "high"

In order to maximaze the number of pipelines running simultaneously, before choosing a node, the system checks if the pipeline already has a node assigned for one of its components. If so, and if the node belongs to the required category, the system selects that node. If not, the system selects a node from the required category with the lowest number of components assigned to it, this way we balance the load between the nodes.

For model evaluation components, the strategy used is the same as the previous one, the only difference is the category of the node selected. For traditional models, the system selects a node from "low" to "med", for ensemble models and support vector machines, the system selects a node from low to "med", and for deep learning models, the system selects a node from "med" to "high".

### Scheduling
For scheduling, the system follows the Shortest Job First scheduling approach.
In order to sort the jobs from the shortest to the longest, we use the estimations of number of operations that the job is going to take. These estimations are determined based on the theoretical computational complexity of the ML algorithm used by the component.