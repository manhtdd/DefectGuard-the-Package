repos=(
  "https://github.com/Genymobile/scrcpy"
  "https://github.com/netdata/netdata"
  "https://github.com/redis/redis"
  "https://github.com/ventoy/Ventoy"
  "https://github.com/obsproject/obs-studio"

)

repo_names=(
  "scrcpy"
  "netdata"
  "redis"
  "ventoy"
  "obs-studio"
)

input_folder="./input/c_top10"
dataset_folder="./dg_cache/dataset"
repo_id="LongK/DefectGuard-PR"
token=$1
commit_message=${2:-"Update dataset"}

switch_to_PR_mode() {
    cd pyszz_v2
    git checkout commit-w-file-PR-only
    cd ..
}

upload_dataset() {
    if [ ! -d "$dataset_folder" ]; then
        echo "Error: Folder '$dataset_folder' does not exist."
        exit 1
    fi

    # Push dataset to Hugging Face Hub
    huggingface-cli repo upload $dataset_folder --repo_id $repo_id --commit-message "$commit_message" --token $token

    # Check if the upload was successful
    if [ $? -eq 0 ]; then
        echo "Dataset successfully pushed to Hugging Face Hub."
        rm -rf 
    else
        echo "Error: Failed to push dataset."
        exit 1
    fi
}

mine() {
    defectguard -debug -log_to_file mining \
        -repo_name "$repo" \
        -repo_path input/c_top10/ \
        -repo_language C \
        -pyszz_path /app/pyszz_v2 
}


switch_to_PR_mode
# Loop through each repository URL and clone it
for ((i=0; i<${#repos[@]}; i++)); do
  repo="${repos[$i]}"
  repo_name="${repo_names[$i]}"
  git clone "$repo" "$input_folder/$repo_name"
  echo "Mining $repo_name"
  mine "$repo_name"
  upload_dataset
  rm -rf "$input_folder/$repo_name"
done