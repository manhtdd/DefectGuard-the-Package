#!/bin/bash

# Check if a repository name was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <repository_name>"
    exit 1
fi

# Assign the provided repository name to a variable
repo_name=$1

# List of models for evaluation
models=("deepjit" "simcom" "tlel" "lr" "lapredict")

# Evaluate each model
for model in "${models[@]}"; do
    defectguard evaluating \
        -model $model \
        -from_pretrain \
        -repo_name $repo_name \
        -repo_language JavaScript
done
