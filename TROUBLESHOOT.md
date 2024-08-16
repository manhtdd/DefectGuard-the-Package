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