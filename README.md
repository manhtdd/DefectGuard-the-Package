# DefectGuard: An Integrated, Efficient and Effective Tool for JIT Defect Prediction

## About

- DefectGuard is a python package
- Basic functionalities:
  - Mining commits from Git repositories
  - Post-processing, training, inferencing JITDP model via CLI or import library
- DefectGuard had been integrated into VSC _(extension)_, Jenkins & GitHub Action _(via command)_

## Prerequisite

### PySZZ

DefectGuard requires this external tool for mining data functionality. Please install it before mining data.

Our [Dockerfile](https://github.com/manhtdd/DefectGuard-the-Package/blob/main/Dockerfile) already prepared with PySZZ, please refer to it if you want to install it to your local machine

### Libraries

Check out this [requirements.txt](https://github.com/manhtdd/DefectGuard-the-Package/blob/main/requirements.txt)

```
pip install -r requirements.txt
```

## Installation

### via Docker (RECOMMENDED)

```
docker compose up --build -d
docker exec -it defectguard /bin/bash
```

Inside docker container:

```
bash scripts/setup.sh
```

## Basic usages

### Mining commits from Git repositories

```
defectguard mining \
    -repo_name <project_name> \
    -repo_path <path/to/project> \
    -repo_language <main_language_of_project> \
    -pyszz_path <path/to/project/pyszz_v2>
```

[Example](https://github.com/manhtdd/DefectGuard-the-Package/blob/main/scripts/test_mining.sh)

### Training

```
defectguard training \
    -model <model_name> \
    -repo_name <project_name> \
    -repo_language <main_language_of_project> \
    -epochs <epochs>
```

[Example](https://github.com/manhtdd/DefectGuard-the-Package/blob/main/scripts/test_train.sh)

### Fine-tuning

```
defectguard training \
    -model <model_name> \
    -from_pretrain \
    -repo_name <project_name> \
    -repo_language <main_language_of_project> \
    -epochs <epochs>
```

[Example](https://github.com/manhtdd/DefectGuard-the-Package/blob/main/scripts/test_finetuning.sh)

### Evaluating

```
defectguard evaluating \
    -model <model_name> \
    -repo_name <project_name> \
    -repo_language <main_language_of_project>
```

[Example](https://github.com/manhtdd/DefectGuard-the-Package/blob/main/scripts/test_evaluate.sh)

### Evaluating from our pretrain models

```
defectguard evaluating \
    -model <model_name> \
    -from_pretrain \
    -repo_name <project_name> \
    -repo_language <main_language_of_project>
```

### Inference

Comming Soon

### Integrate into CLI-like Continuous Integration

Comming Soon
