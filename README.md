# ML Pipeline Placement System
The increasing demand for ML solutions has underscored the need for methods that accelerate both model development and deployment. MLOps has emerged as a response to this need by automating and streamlining the entire ML lifecycle, with ML pipelines playing a central role. Since the computational requirements of pipeline tasks can vary significantly, the use of heterogeneous computing environments has become essential for efficient execution. However, existing MLOps platforms are incapable of making well-founded placement decisions in such environments, often leading to suboptimal task allocation and reduced efficiency.

Given the limitations of current MLOps platforms, this repository provides an end-to-end solution for optimising the execution of ML pipelines in heterogeneous environments. With this solution, the goal is not to replace existing platforms, but rather to enhance them by providing scheduling and placement capabilities, which are currently lacking.

This solution contains two important modules:
1. **Pipeline definition library**: platform-agnostic library to define ML pipelines.
2. **Pipeline placement system**: system that listens for pipeline submissions, schedules them, places their tasks on available nodes in a cluster, and triggers their execution.

## Project Structure
This project is structured as follows:

```
.
├── client/               # Source code of the pipeline definition library
├── server/               # Source code of the placement system
├── pipelines/            # Examples of pipeline definitions using the library
├── images/               # Docker images used by the tasks in the pipelines
├── data/                 # Datasets used in the pipelines
├── results/              # Performance results of the placement system
├── utils/                # Utility scripts to upload datasets to NFS server
└── README.md             # This file
```

## Pipeline Definition Library
The pipeline definition library consists in a Python package that provides intuitive abstractions to define individual tasks and organise them into a complete pipeline.

Each task must be encapsulated within a standalone Python file. These files include not only the core task logic but also any necessary libraries and dependencies. To further enhance modularity and simplify task integration into pipelines, each task must be implemented as a Python function.

A pipeline is defined in a standalone Python file, where the tasks are imported as standard Python functions. This file serves as the entry point for the pipeline, allowing to specify the tasks to be executed, their arguments, and the order of execution.

To provide context to the placement system, each pipeline must be accompanied by a metadata file. The metadata file should be named `metadata.json` and placed in the same directory as the pipeline definition file. The following information should be included:

- **Task types**: Mapping of task names to their types (preprocessing, training, or evaluation).
- **Datasets**: Details of the datasets used in the pipeline (dataset name, dataset type, total samples, features, etc.).
- **ML model**: Information about the ML model used in the pipeline (model identifier and model-specific parameters).

Concrete examples of pipeline definitions using the library can be found in `pipelines/`.

To submit a pipeline to the placement system, the pipeline definition file just needs to be executed like any other Python script. The library will automatically handle the submission process to the placement system.


## Pipeline Placement System
The placement system, implemented as a FastAPI application and served by an Uvicorn server, exposes a REST API used by the definition library. This API includes a dedicated submission endpoint that handles POST requests containing the pipeline files.

To locally run the placement system, run the following command from the `server/` directory:

```bash
fastapi dev main
```

### Environment Variables
The placement system requires several environment variables to be set for proper configuration. These variables can be defined in a `.env` file in the `server/` directory. The following variables are required:

- `KFP_URL`: The URL of the Kubeflow Pipelines (KFP) API.
- `PROMETHEUS_URL`: The URL of the Prometheus server for monitoring the cluster nodes.
- `PIPELINES_DIR`: The directory where the pipeline related files are stored (server-side).
- `WAIT_INTERVAL`: The interval (in seconds) to wait for new pipeline submissions (defaults to 15).
- `UPDATE_INTERVAL`: The interval (in seconds) to query the KFP API for pipeline status updates (defaults to 5).

### Placement Strategies
The placement system supports the integration of custom placement strategies. These strategies are implemented as Python classes that inherit from the `PlacerInterface` abstract class, which is defined in the `server/placers/interface.py` module. The placement strategy is responsible for scheduling the pipelines and mapping their tasks to the available nodes in the cluster.

To uniquely identify each placement strategy, the strategies must be registered in the Placement Decision Unit class, which is defined in the `server/components/decision_unit.py` module. The registration is done by adding a name and the corresponding class to the `placers` dictionary.

When running the placement system, the desired placement strategy can be selected by setting the `PLACER` environment variable. Currently, the following placement strategies are available:

```bash
PLACER="random_random"
PLACER="fifo_random"
PLACER="fifo_round_robin"
PLACER="custom"
```

### Performance Results
To evaluate the performance of the placement system, after running the desired pipelines, when the system is stopped, it will generate a `pipelines.json` file and a `n_pipelines.csv` file in the pipelines' directory (defined by the `PIPELINES_DIR` environment variable).

The `pipelines.json` file contains detailed information about each pipeline and its tasks, including their execution times, waiting times, and the nodes on which they were executed. The `n_pipelines.csv` file provides the evolution of the number of running and waiting pipelines over time.

To obtain relevant performance metrics from the generated files, the `results/` directory contains the `analysis_utils.py` script, which provides utility functions to process the data. These functions provide insights into the performance of the placement system, namely:

- **Total execution time**: The total time elapsed from the submission of the first pipeline to the completion of the last pipeline;
- **Average waiting time**: The average time each pipeline spent waiting from submission to execution;
- **Pipeline execution time**: The time taken to execute each individual pipeline;
- **Pipeline waiting time**: The time each pipeline spent waiting for resources before execution;
- **Running vs Waiting Pipelines**: The evolution of the number of running and waiting pipelines over time.

To analyse and visualise the performance results, a Jupyter notebook is provided in the `results/` directory. This notebook uses the utility functions to process the data and generate relevant plots. The notebook allows for an interactive exploration of the performance metrics, providing a comprehensive overview of the placement system's efficiency.

## Authors
- **Pedro Rodrigues** - [pedro535](https://github.com/pedro535)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
