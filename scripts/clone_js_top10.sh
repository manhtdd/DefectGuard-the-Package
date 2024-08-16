#!/bin/bash

# Array of GitHub repository URLs
repos=(
  "https://github.com/facebook/react"
  "https://github.com/trekhleb/javascript-algorithms"
  "https://github.com/airbnb/javascript"
  "https://github.com/twbs/bootstrap"
  "https://github.com/vercel/next.js"
  "https://github.com/Chalarangelo/30-seconds-of-code"
  "https://github.com/nodejs/node"
  "https://github.com/axios/axios"
  "https://github.com/facebook/create-react-app"
  "https://github.com/mrdoob/three.js"
)

repo_names=(
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

# Loop through each repository URL and clone it
for ((i=0; i<${#repos[@]}; i++)); do
  repo="${repos[$i]}"
  repo_name="${repo_names[$i]}"
  git clone "$repo" "./input/js_top10/$repo_name"
done
