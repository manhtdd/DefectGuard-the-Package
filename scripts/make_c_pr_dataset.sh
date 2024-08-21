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

input_folder="./input/c_top5"
dataset_folder="./dg_cache/dataset"
repo_id="LongK/DefectGuard-PR"
repo_folder="c_top5"
token=$1
echo $token

switch_to_PR_mode() {
    cd pyszz_v2 || exit 1
    git checkout commit-w-file-PR-only
    mkdir out
    cd ..
}

upload_dataset() {
    # local dataset_folder=$1
    # local repo_id=$2
    # local commit_message=$3
    # local token=$4
    if [ ! -d "$1" ]; then
        echo "Error: Folder '$1' does not exist."
        exit 1
    fi

    # Push dataset to Hugging Face Hub
    huggingface-cli upload $2 $1 $repo_folder --repo-type dataset --token=$3

    # Check if the upload was successful
    if [ $? -eq 0 ]; then
        echo "Dataset successfully pushed to Hugging Face Hub."
    else
        echo "Error: Failed to push dataset."
        exit 1
    fi
}

mine() {
    defectguard -debug -log_to_file mining \
        -repo_name "$1" \
        -repo_path input/c_top5/ \
        -repo_language C \
        -pyszz_path ./pyszz_v2 \
        -num_core 8
}


switch_to_PR_mode
# Loop through each repository URL and clone it
for ((i=0; i<${#repos[@]}; i++)); do
  repo="${repos[$i]}"
  repo_name="${repo_names[$i]}"
  git clone "$repo" "$input_folder/$repo_name"
  echo "Mining $repo_name"
  mine "$repo_name"
  upload_dataset $dataset_folder $repo_id $token
  rm -rf "$input_folder/$repo_name"
done