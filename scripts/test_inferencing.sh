#!bin/bash

defectguard -debug -log_to_file inferencing \
    -model deepjit \
    -reextract \
    -dg_save_folder . \
    -repo_path input \
    -repo_name Tic-tac-toe-Game-using-Network-Socket-APIs \
    -repo_language C \
    -top 23 \