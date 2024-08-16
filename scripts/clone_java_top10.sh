#!/bin/bash

# Array of GitHub repository URLs
repos=(
  "https://github.com/Snailclimb/JavaGuide"
  "https://github.com/GrowingGit/GitHub-Chinese-Top-Charts"
  "https://github.com/krahets/hello-algo"
  "https://github.com/iluwatar/java-design-patterns"
  "https://github.com/macrozheng/mall"
  "https://github.com/doocs/advanced-java"
  "https://github.com/MisterBooo/LeetCodeAnimation"
  "https://github.com/spring-projects/spring-boot"
  "https://github.com/elastic/elasticsearch"
  "https://github.com/kdn251/interviews"
)

repo_names=(
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


# Loop through each repository URL and clone it
for ((i=0; i<${#repos[@]}; i++)); do
  repo="${repos[$i]}"
  repo_name="${repo_names[$i]}"
  git clone "$repo" "./input/java_top10/$repo_name"
done
