#!/bin/bash

repos=(
  "react"
  "javascript-algorithms"
  "javascript"
  "bootstrap"
  "next.js"
  "30-seconds-of-code"
  "node"
  "axios"
  "create-react-app"
  "three.js"
)

mine() {
    defectguard -debug -log_to_file mining \
        -repo_name "$repo" \
        -repo_path input/js_top10/ \
        -repo_language JavaScript \
        -pyszz_path /app/pyszz_v2 
}

for repo in "${repos[@]}"; do
  mine "$repo"
done
