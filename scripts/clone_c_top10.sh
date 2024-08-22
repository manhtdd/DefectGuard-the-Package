#!/bin/bash

# Array of GitHub repository URLs
repos=(
  "https://github.com/Genymobile/scrcpy"
  "https://github.com/netdata/netdata"
  "https://github.com/redis/redis"
  "https://github.com/ventoy/Ventoy"
  "https://github.com/obsproject/obs-studio"
  "https://github.com/git/git"
  "https://github.com/FFmpeg/FFmpeg"
  "https://github.com/php/php-src"
  "https://github.com/wg/wrk"
  "https://github.com/curl/curl"
)

repo_names=(
  "scrcpy"
  "netdata"
  "redis"
  "ventoy"
  "obs-studio"
  "git"
  "ffmpeg"
  "php-src"
  "wrk"
  "curl"
)

# Loop through each repository URL and clone it
for ((i=0; i<${#repos[@]}; i++)); do
  repo="${repos[$i]}"
  repo_name="${repo_names[$i]}"
  git clone "$repo" "./input/c_top10/$repo_name"
done
