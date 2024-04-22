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
