#!bin/bash

defectguard -debug -log_to_file inferencing \
    -model lr lapredict tlel \
    -repo_language JavaScript \
    -repo_owner eslint \
    -repo_name eslint \
    -pull_numbers 18519 \
    -access_key input/github.json