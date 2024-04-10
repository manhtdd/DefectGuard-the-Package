import os
from argparse import Namespace

def training(params):
    # create save folders
    dg_cache_path = f"{params.dg_save_folder}/dg_cache"
    folders = ["save", "repo", "dataset"]
    if not os.path.exists(dg_cache_path):
        os.mkdir(dg_cache_path)
    for folder in folders:
        if not os.path.exists(os.path.join(dg_cache_path, folder)):
            os.mkdir(os.path.join(dg_cache_path, folder))

    # User's input handling
    cfg = {
        "mode": params.mode,
        "repo_owner": params.repo_owner,
        "repo_name": params.repo_name,
        "repo_path": params.repo_path,
        "repo_language": params.repo_language,
        "repo_save_path": f"{dg_cache_path}/save",
        "extractor_save": True,
        "create_dataset": False,
    }

    if params.mode == "remote":
        cfg["repo_clone_path"] = f"{dg_cache_path}/repo"
        cfg["repo_clone_url"] = f"https://github.com/{params.repo_owner}/{params.repo_name}.git"
        cfg["extractor_check_uncommit"] = False
    else:
        cfg["extractor_check_uncommit"] = params.uncommit
        
    cfg = Namespace(**cfg)