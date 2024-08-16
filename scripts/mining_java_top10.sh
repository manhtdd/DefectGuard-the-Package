#!/bin/bash

repos=(
  "javaguide"
  "github-chinese-top-charts"
  "hello-algo"
  "java-design-patterns"
  "mall"
  "advanced-java"
  "leetcodeanimation"
  "spring-boot"
  "elasticsearch"
  "interviews"
)

mine() {
    defectguard -debug -log_to_file mining \
        -repo_name "$repo" \
        -repo_path input/java_top10/ \
        -repo_language Java \
        -pyszz_path /app/pyszz_v2 
}

for repo in "${repos[@]}"; do
  mine "$repo"
done
