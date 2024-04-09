#!bin/bash

defectguard inferencing \
    -models deepjit \
    -dataset platform \
    -repo_name Tic-tac-toe-Game-using-Network-Socket-APIs \
    -repo_name /home/manh/Documents/DefectGuard \
    -uncommit \
    -top 10 \
    -repo_language C \
    -dg_save_folder . \
    -debug \
    -log_to_file
