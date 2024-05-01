#!/bin/bash

# Check if a repository name was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <repository_name> [epochs]"
    exit 1
fi

# Assign the provided repository name to a variable
repo_name=$1

# Check if epochs was provided, otherwise use default
epochs=${2:-5} # Default is 2 if not provided

# List of models to train and evaluate
models=("deepjit" "simcom" "lapredict" "tlel" "lr")

# Training models
for model in "${models[@]}"; do
    if [[ "$model" == "deepjit" || "$model" == "simcom" ]]; then
        defectguard training \
            -model $model \
            -from_pretrain \
            -repo_name $repo_name \
            -repo_language JavaScript \
            -epochs $epochs \
            -device cpu
    else
        defectguard training \
            -model $model \
            -repo_name $repo_name \
            -repo_language JavaScript
    fi
done

# Evaluating models
for model in "${models[@]}"; do
    if [[ "$model" == "simcom" || "$model" == "deepjit" ]]; then
        defectguard evaluating \
            -model $model \
            -repo_name $repo_name \
            -repo_language JavaScript \
            -dictionary defectguard/models/metadata/${model}/JavaScript_dictionary
    else
        defectguard evaluating \
            -model $model \
            -repo_name $repo_name \
            -repo_language JavaScript
    fi
done
