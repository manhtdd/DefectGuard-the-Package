# Objective 1: Performance of Just-in-Time Defect Prediction techniques in industry environment

To archive this objective, we have 2 testing scenarios:
1. Using our pre-train models and evaluate these models on industry dataset
2. Fine-tune and evaluate these new fine-tuned models on industry dataset

## 0. Setup environment

Please checkout docker setup in README.md _(or From Scratch section if you do not have docker)_

`defectguard` can run from anywhere in your local machine. To keep it simple, the following pipeline will be ran where this cloned repo is.

## 1. Setup your project

For simplicity, we will be using this [javascript-algorithms](https://github.com/trekhleb/javascript-algorithms.git) repo as example.

```
mkdir input
git -C input clone https://github.com/trekhleb/javascript-algorithms.git
```

## 2. Extract features and code changes from the project

Please make sure your pyszz is setup for this setup to work.
Run the following command:
```
defectguard mining \
    -repo_name javascript-algorithms \
    -repo_path input/ \ # Meaning the relative path to your project is input/javascript-algorithms
    -repo_language JavaScript \
    -pyszz_path pyszz_v2
```

The extracted features and code changes are saved at `dg_cache/save`

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
## 3. Use the extracted features and code changes to make the evaluation

For 1st scenario: "Using our pre-train models and evaluate these models on industry dataset"

We have 5 models: `deepjit`, `simcom`, `tlel`, `lapredict`, `lr`
```
defectguard evaluating \
    -model deepjit \
    -from_pretrain \
    -repo_name javascript-algorithms \
    -repo_language JavaScript
```

Output of these models, including prediction score and auc, are saved at `dg_cache/save`

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
The `auc.csv` will look like below:
```
Project Name,lapredict,lr,tlel,deepjit,sim,com,simcom
javascript-algorithms,0.596969696969697,0.2545454545454545,0.4939393939393939,0.593939393939394,0.3909090909090909,0.5545454545454546,0.3999999999999999
```
**NOTE**: If you want to re-evaluate on the same project, make sure to save `dg_cache` to other place before hand.

## 4. Use the extracted features and code changes to fine-tune and evaluate

For 2nd scenario: "Fine-tune and evaluate these new fine-tuned models on industry dataset"

Fine-tune the deeplearning-based models `deepjit`, `simcom`:
```
defectguard training \
    -model deepjit \
    -from_pretrain \
    -repo_name javascript-algorithms \
    -repo_language JavaScript \
    -epochs 2 \
    -device cuda
```

Re-train the machine learning-based models `lapredict`, `lr`, `tlel`:
```
defectguard training \
    -model lapredict \
    -repo_name javascript-algorithms \
    -repo_language JavaScript
```

Checkpoint of these models are saved at `dg_cache/save`
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
    -model tlel \
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
The `auc.csv` will look like below:
```
Project Name,lapredict,lr,tlel,deepjit,sim,com,simcom
javascript-algorithms,0.596969696969697,0.4606060606060606,0.2696969696969696,0.33636363636363636,0.3909090909090909,0.5545454545454546,0.3999999999999999
```
**NOTE**: If you want to re-evaluate on the same project, make sure to save `dg_cache` to other place before hand.