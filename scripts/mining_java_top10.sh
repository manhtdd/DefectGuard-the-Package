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
    echo "!defectguard -debug -log_to_file mining -repo_name $repo -repo_path /kaggle/working/input -repo_language Java -pyszz_path /kaggle/working/DefectGuard-the-Package/AI4C-SZZ -num_core 4"
}

for repo in "${repos[@]}"; do
  mine "$repo"
done
