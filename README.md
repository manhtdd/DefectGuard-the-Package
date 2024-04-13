# DefectGuard: An Integrated, Efficient and Effective Tool for JIT Defect Prediction

## Bug Challenge

### Bug's Description

The print of Namespace after running a feature succesfully is an unwanted behavior. No `print()` or `logger()` is found.

```
root@b035f973f717:/app# bash scripts/test_train.sh 
Namespace(debug=False, log_to_file=False, dg_save_folder='.', mode='local', repo_name='Tic-tac-toe-Game-using-Network-Socket-APIs', repo_owner='', repo_path='', repo_language='C++', uncommit=False, model='lapredict', dataset='', epochs=1, dictionary='', hyperparameters='', device='cpu', func=<function training at 0x73129fbe9a20>)
```

### How to replicate the bug

1. Create DefectGuard image
```
bash scripts/docker_start.sh
```

2. Inside the docker container

- Clone a test repo
```
bash scripts/clone_test_repo.sh
```
- Run mining feature (the bug will spawns here)
```
bash scripts/test_mining.sh
```
- Run training feature (the bug will spawns here)
```
bash scripts/test_training.sh
```