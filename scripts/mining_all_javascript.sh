#!/bin/bash

repos=(
    # "iptv"
    # "preact"
    "phaser"
    "bootstrap"
    # "moment"
    # "Ghost"
    # "eslint"
    # "mongoose"
    # "codemirror5"
    # "uppy"
)

mine() {
    defectguard -debug mining \
        -repo_name "$repo" \
        -repo_path input/ \
        -repo_language JavaScript \
        -pyszz_path /app/pyszz_v2 
}

for repo in "${repos[@]}"; do
  mine "$repo"
done
