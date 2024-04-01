import os
from .utils.logger import logger
from .JITCrawler import BasicPipeline
from argparse import Namespace

def mining(params):
    logger("Start DefectGuard")

    # create save folders
    folders = ["save", "repo", "dataset"]
    for folder in folders:
        if not os.path.exists(os.path.join(params.dg_save_folder, folder)):
            os.mkdir(os.path.join(params.dg_save_folder, folder))

    user_input = {
        "models": params.models,
        "dataset": params.dataset,
        "cross": params.cross,
        "device": params.device,
    }

    logger(user_input)

    # User's input handling
    cfg = {
        "mode": params.mode,
        "repo_owner": params.repo_owner,
        "repo_name": params.repo_name,
        "repo_path": params.repo_path,
        "repo_language": params.repo_language,
        "repo_save_path": os.path.join(params.dg_save_folder, "save"),
        "extractor_save": True,
        "create_dataset": True,
        "pyszz_path": params.pyszz_path,
        "dataset_save_path": os.path.join(params.dg_save_folder, "dataset"),
        "processor_save": True,
    }

    if params.mode == "remote":
        cfg["repo_clone_path"] = os.path.join(params.dg_save_folder, "repo")
        cfg["repo_clone_url"] = f"https://github.com/{params.repo_owner}/{params.repo_name}.git"
        cfg["extractor_check_uncommit"] = False
    else:
        cfg["extractor_check_uncommit"] = params.uncommit

    cfg = Namespace(**cfg)    
    crawler = BasicPipeline(cfg)
    crawler.set_repo(cfg)
    crawler.run()
