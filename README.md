# DefectGuard: An Integrated, Efficient and Effective Tool for JIT Defect Prediction

## About

- DefectGuard is a python package
- Basic functionalities:
  - Mining commits from Git repositories
  - Post-processing, training, inferencing JITDP model via CLI or import library
- DefectGuard had been integrated into VSC _(extension)_, Jenkins & GitHub Action _(via command)_

## Installation

### SrcML

DefectGuard requires PySZZ for mining data functionality. SrcML is required by PySZZ. Please install it before mining data.

```
# Install libarchive13 libcurl4 libxml2
sudo apt-get install libarchive13 libcurl4 libxml2

# Install libssl
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    rm -rf libssl1.1_1.1.1f-1ubuntu2_amd64.deb

# Install SrcML
RUN wget http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu20.04.deb && \
    dpkg -i srcml_1.0.0-1_ubuntu20.04.deb && \
    rm -rf srcml_1.0.0-1_ubuntu20.04.deb
```

### PySZZ

DefectGuard requires this external tool for mining data functionality. Please install it before mining data.

```
git clone https://github.com/grosa1/pyszz_v2.git
```

### Dependencies

Check out this [requirements.txt](https://github.com/manhtdd/DefectGuard-the-Package/blob/main/requirements.txt)

```
pip install -r requirements.txt
```

### Setup DefectGuard

```
python setup.py develop
```

## Installation via Docker (RECOMMENDED)

```
docker compose up --build -d
docker exec -it defectguard /bin/bash
```

Inside docker container:

```
# This setup pyszz and defectguard
bash scripts/setup.sh
```

### If you want Docker container to access GPU(s), please download `nvidia-container-toolkit`

**Note**: download this outside of the container

Install the `nvidia-container-toolkit` package as per official documentation at Github.

We also provide [a quick-run script](https://github.com/manhtdd/DefectGuard-the-Package/blob/main/scripts/setup_nvidia_container_toolkit.sh) for Debian-based OS

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

## Output of DefectGuard

### Folder's structure
```bash
.
├── dg_cache
│   ├── dataset // default folder for saving dataset
│   ├── save // default folder for saving extracted data
│   ├── repo // default folder for cloning github repository
```

### Extracted Data's folder structure

A sample structure of extracted data:
```bash
.
├── save
|   ├── repo_name
|   |   ├── commit_ids.pkl
|   |   ├── etracted_info.json // the config for Extractor
|   |   ├── repo_bug_fix.json // the bug_fix file for running PySZZ
|   |   ├── repo_commits_{num}.pkl // files storing commits information
|   |   ├── repo_features.pkl // files storing commits features
```

### Processed Data's folder structure

A sample structure of processed data:
```bash
.
├── dataset
|   ├── repo_name
|   |   ├── commits
|   |   |   ├── cc2vec.pkl
|   |   |   ├── deepjit.pkl
|   |   |   ├── simcom.pkl
|   |   |   ├── dict.pkl
|   |   ├── features
|   |   |   ├── feature.csv
```

### Repository's structure

In case this tool is run on `mode="local"`, please follow this repository's structure paths:
```bash
.
├── repo_path
|   ├── repo_owner
|   |   ├── repo_name
|   |   |   ├── .git
|   |   |   ├── other repo content
```

## Troubleshoot

Find here: https://github.com/manhtdd/DefectGuard-the-Package/blob/main/TROUBLESHOOT.md