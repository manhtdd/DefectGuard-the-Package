#!/bin/bash

# Define arrays for repository names and clone URLs
repo_names=(
    "FFmpeg" 
    "qemu"
)
repo_clone_urls=(
    "https://github.com/FFmpeg/FFmpeg" 
    "https://github.com/qemu/qemu"
)

# Loop over the arrays
for i in "${!repo_names[@]}"; do
    repo_name=${repo_names[$i]}
    repo_clone_url=${repo_clone_urls[$i]}
    
    # Run the defectguard mining command
    defectguard mining \
        -dg_save_folder . \
        -mode remote \
        -repo_name "$repo_name" \
        -repo_clone_url "$repo_clone_url" \
        -repo_language C \
        -pyszz_path pyszz_v2
done