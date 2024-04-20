#!bin/bash

defectguard -debug inferencing \
    -model deepjit \
    -dg_save_folder . \
    -repo_path input \
    -repo_name Tic-tac-toe-Game-using-Network-Socket-APIs \
    -repo_language C \
    -top 10 \