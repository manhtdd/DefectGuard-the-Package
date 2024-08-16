#!/bin/bash

# Array of GitHub repository URLs
repos=(
  "https://github.com/iptv-org/iptv"
  "https://github.com/preactjs/preact"
  "https://github.com/phaserjs/phaser"
  "https://github.com/twbs/bootstrap"
  "https://github.com/moment/moment"
  "https://github.com/TryGhost/Ghost"
  "https://github.com/eslint/eslint"
  "https://github.com/Automattic/mongoose"
  "https://github.com/codemirror/codemirror5"
  "https://github.com/transloadit/uppy"
)

repo_names=(
  "iptv"
  "preact"
  "phaser"
  "bootstrap"
  "moment"
  "ghost"
  "eslint"
  "mongoose"
  "codemirror"
  "uppy"
)

# Loop through each repository URL and clone it
for ((i=0; i<${#repos[@]}; i++)); do
  repo="${repos[$i]}"
  repo_name="${repo_names[$i]}"
  git clone "$repo" "./input/$repo_name"
done
