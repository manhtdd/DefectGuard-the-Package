# Some expected bugs and their fixes

## 1. Exit Docker container when run a DefectGuard's command

If you run build and create a our Docker image using `docker compose`, this could happen. The solution is exit the container, stop the container with `docker compose down` and then start the container with `docker compose up -d` again.

## 2. No Nivida-driver on a CPU-only machine

`docker-compose.yml` contains scripts for running with GPU(s). If you do not have GPU(s), please command out code from line 12 them re-run `docker compose up -d` command. And `pip install` only the `cpu-only-requiremnts.txt`.

```
deploy:
    resources:
    reservations:
        devices:
        - driver: nvidia
            count: all
            capabilities: [gpu]
```

## 3. `out` folder is not found by PySZZ

PySZZ is surpose to create its own `out` folder. If it does not create the folder, then you have to create for it.

```
mkdir <path/to/PySZZ>/out
```

## 4. Pretrain of models is download eventhrough I do not need it

Some models still require you to download its hyperparameters, pretrain is also downloaded with it. The pretrain will not be load into the model.

## 5. ERROR: No commits found. Try run git log at your repo's location

```
root@7a34b70ebc48:/app# defectguard mining -repo_name javascript-algorithms -repo_path input -repo_language JavaScript -pyszz_path pyszz_v2
Running on repository: javascript-algorithms
        at: /app/input
Continue extracting repository ...
Start extracting repository ...
ERROR: No commits found. Try run git log at your repo's location
Execute location: /app/input/javascript-algorithms
Command: git log --all --no-decorate --no-merges --pretty=format:"%H"
```

If you encounter an ERROR like this, please try to copy the command on the output (e.g. `git log --all --no-decorate --no-merges --pretty=format:"%H"`) and try to execute the command at the `Execute location` like below:

```
git -C /app/input/javascript-algorithms log --all --no-decorate --no-merges --pretty=format:"%H"
```

If you get an output like below:

```
fatal: detected dubious ownership in repository at '/app/input/javascript-algorithms'
To add an exception for this directory, call:

        git config --global --add safe.directory /app/input/javascript-algorithms
```
Then simply run the above command: `git config --global --add safe.directory /app/input/javascript-algorithms`. This should solve your problem now.

Else, please contact me to get support.