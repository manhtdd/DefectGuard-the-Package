# Objective 1: Performance of Just-in-Time Defect Prediction techniques in industry environment

To archive this objective, we have 2 testing scenarios:
1. Evaluate pre-trained models on an industry dataset.
2. Fine-tune and evaluate newly fine-tuned models on the same dataset.

## Setup

Refer to the `README.md` for [Docker](https://github.com/manhtdd/DefectGuard-the-Package?tab=readme-ov-file#via-docker-recommended) setup instructions or the [From Scratch](https://github.com/manhtdd/DefectGuard-the-Package?tab=readme-ov-file#from-scratch) section if Docker is not an option.

`defectguard` can be run from any location on your local machine. For simplicity, follow the pipeline where this repo is cloned.

## 1. Setup your project

We'll use the [javascript-algorithms](https://github.com/trekhleb/javascript-algorithms.git) repository as an example. The path that lead to the wanted project is only needed for step 2. From step 2 onward, we only need your project's name.

```
mkdir input
git -C input clone https://github.com/trekhleb/javascript-algorithms.git
```

Incase your projects located elsewhere (e.g. `/home/manhtd/Downloads` instead of `/home/manhtd/Documents/DefectGuard-the-Package/input`), please kindly update the `volumes` part of the `docker-compose.yml` as following:

```
services:
  defectguard:
    container_name: defectguard
    image: defectguard:1.0
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - .:/app
      - /home/manhtd/Downloads:/projects # Please add the path to your path here instead
    stdin_open: true
    tty: true
```

## 2. Extract features and code changes from the project

Before running Defect Prediction models, we need to label code changes and extract neccessary features from them by run the following command:
```
defectguard mining \
    -repo_name javascript-algorithms \
    -repo_path input/ \ # Relative path to your project is input/javascript-algorithms
    -repo_language JavaScript \
    -pyszz_path pyszz_v2
```
Note that, this step require your `pyszz` to be correctly set up as mentioned in [Installation](https://github.com/manhtdd/DefectGuard-the-Package?tab=readme-ov-file#installation) section.

The extracted features and code changes will be saved in the `dg_cache/save` directory.

```
dg_cache
├── dataset
│   └── javascript-algorithms
│       ├── commit
│       │   ├── cc2vec_javascript-algorithms_test.pkl
│       │   ├── cc2vec_javascript-algorithms_train.pkl
│       │   ├── cc2vec_javascript-algorithms_val.pkl
│       │   ├── cc2vec.pkl
│       │   ├── deepjit_javascript-algorithms_test.pkl
│       │   ├── deepjit_javascript-algorithms_train.pkl
│       │   ├── deepjit_javascript-algorithms_val.pkl
│       │   ├── deepjit.pkl
│       │   ├── dict.pkl
│       │   ├── javascript-algorithms_train_dict.pkl
│       │   ├── simcom_javascript-algorithms_test.pkl
│       │   ├── simcom_javascript-algorithms_train.pkl
│       │   ├── simcom_javascript-algorithms_val.pkl
│       │   └── simcom.pkl
│       └── feature
│           ├── features.csv
│           ├── javascript-algorithms_test.csv
│           └── javascript-algorithms_train.csv
├── repo
└── save
    └── javascript-algorithms
        ├── bszz.yml
        ├── commit_ids.pkl
        ├── extracted_info.json
        ├── repo_bug_fix.json
        ├── repo_commits_0.pkl
        └── repo_features.pkl
```
## 3. Evaluating Pre-Trained Models

For the first scenario, we will use a pre-written script:

**NOTE**: this script run with assumption the main language of the repo is JavaScript. Please check the script before running it.
```
bash scripts/objective_1_evaluate.sh javascript-algorithms
```

Or perform the steps manually for each models `deepjit`, `simcom`, `tlel`, `lapredict`, and `lr`:

```
defectguard evaluating \
    -model deepjit \
    -from_pretrain \
    -repo_name javascript-algorithms \
    -repo_language JavaScript
```

Outputs, including prediction scores and AUC, are stored in `dg_cache/save`.

```
dg_cache
├── dataset...
├── repo
└── save
    └── javascript-algorithms
        ...
        ├── predict_scores
        │   ├── com.csv
        │   ├── deepjit.csv
        │   ├── lapredict.csv
        │   ├── lr.csv
        │   ├── sim.csv
        │   └── tlel.csv
        └── results
            └── auc.csv
```
The `auc.csv` will display results as follows:
```
Project Name,lapredict,lr,tlel,deepjit,sim,com,simcom
javascript-algorithms,0.596969696969697,0.2545454545454545,0.4939393939393939,0.593939393939394,0.3909090909090909,0.5545454545454546,0.3999999999999999
```
**NOTE**: Back up `dg_cache` before re-evaluating the same project.

## 4. Fine-Tuning and Evaluating Models (ABORT)

For the second scenario, use the following scripts based on your preference for the number of training epochs:

**NOTE**: this script run with assumption the main language of the repo is JavaScript and run on CPU. Please check the script before running it.

Since `epochs` for fine-tuning is a hyperparameter that is yet to be decided. We would like to try out these 2 values first, which are 5 epochs and 10 epochs. Please ensure to back up `dg_cache` between each script.
```
bash scripts/objective_1_fine_tune_evaluate.sh javascript-algorithms 5
```
```
bash scripts/objective_1_fine_tune_evaluate.sh javascript-algorithms 10
```

Or perform the steps manually. Start by fine-tuning deep learning-based models (`deepjit`, `simcom`) and retraining machine learning-based models (`lapredict`, `lr`, `tlel`):
```
defectguard training \
    -model deepjit \ # simcom
    -from_pretrain \
    -repo_name javascript-algorithms \
    -repo_language JavaScript \
    -epochs 5 \ # or 10
    -device cuda
```
```
defectguard training \
    -model lapredict \ # tlel, lr
    -repo_name javascript-algorithms \
    -repo_language JavaScript
```

Model checkpoints are saved in `dg_cache/save`.
```
dg_cache
├── dataset
├── repo
└── save
    └── javascript-algorithms
        ...
        ├── com.pt
        ├── deepjit.pt
        ├── lapredict.pkl
        ├── lr.pkl
        ├── sim.pkl
        └── tlel.pkl
```

Evaluate the machine learning-based models `tlel`, `lapredict`, `lr`:
```
defectguard evaluating \
    -model tlel \ # lapredict, lr
    -repo_name javascript-algorithms \
    -repo_language JavaScript \
```

Evaluate the deeplearning-based models `deepjit`, `simcom`:
```
defectguard evaluating \
    -model simcom \
    -repo_name javascript-algorithms \
    -repo_language JavaScript \
    -dictionary defectguard/models/metadata/simcom/JavaScript_dictionary
```
```
defectguard evaluating \
    -model deepjit \
    -repo_name javascript-algorithms \
    -repo_language JavaScript \
    -dictionary defectguard/models/metadata/deepjit/JavaScript_dictionary
```

Output of these models, including prediction score and auc, are save at `dg_cache/save`

```
dg_cache
├── dataset...
├── repo
└── save
    └── javascript-algorithms
        ...
        ├── predict_scores
        │   ├── com.csv
        │   ├── deepjit.csv
        │   ├── lapredict.csv
        │   ├── lr.csv
        │   ├── sim.csv
        │   └── tlel.csv
        └── results
            └── auc.csv
```
The updated `auc.csv` might look like this:
```
Project Name,lapredict,lr,tlel,deepjit,sim,com,simcom
javascript-algorithms,0.596969696969697,0.4606060606060606,0.2696969696969696,0.33636363636363636,0.3909090909090909,0.5545454545454546,0.3999999999999999
```
**NOTE**: Ensure `dg_cache` is backed up before re-evaluating on the same project.

## Expected final output

Finally, we will be asking for all the predict_scores and results
```
final_results
├── project_1
|   └── evaluate_only
|       ├── predict_scores
|       │   ├── com.csv
|       │   ├── deepjit.csv
|       │   ├── lapredict.csv
|       │   ├── lr.csv
|       │   ├── sim.csv
|       │   └── tlel.csv
|       └── results
|           └── auc.csv
├── project_2
...
└── project_n
```
