#!/bin/bash

repos=(
  "curl"
  "scrcpy"
  "netdata"
  "redis"
  "ventoy"
  "obs-studio"
  "git"
  "ffmpeg"
  "php-src"
  "wrk"
)

mine() {
    defectguard -debug -log_to_file mining \
        -repo_name "$repo" \
        -repo_path input/c_top10/ \
        -repo_language C \
        -pyszz_path /app/pyszz_v2 
}

for repo in "${repos[@]}"; do
  mine "$repo"
done
