#!bin/bash

defectguard inferencing \
    -models la \
    -dataset qt \
    -repo_name Tic-tac-toe-Game-using-Network-Socket-APIs \
    -repo_path /home/manh/Documents/DefectGuard \
    -uncommit \
    -top 10 \
    -repo_language C \
    -dg_save_folder . \
