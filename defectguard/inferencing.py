import os, json, time
from .utils.logger import logger
from .models import (
    DeepJIT,
    CC2Vec,
    SimCom,
    LAPredict,
    LogisticRegression,
    TLELModel,
    JITLine,
)
from .utils.utils import (
    commit_to_info,
    sort_by_predict,
    vsc_output,
    check_threshold,
)
from .JITCrawler import BasicPipeline
from argparse import Namespace

def init_model(model_name, dataset, cross, device):
    project = "cross" if cross else "within"
    match model_name:
        case "deepjit":
            return DeepJIT(dataset=dataset, project=project, device=device)
        case "cc2vec":
            return CC2Vec(dataset=dataset, project=project, device=device)
        case "simcom":
            return SimCom(dataset=dataset, project=project, device=device)
        case "lapredict":
            return LAPredict(dataset=dataset, project=project, device=device)
        case "tlel":
            return TLELModel(dataset=dataset, project=project, device=device)
        case "jitline":
            return JITLine(dataset=dataset, project=project, device=device)
        case "la":
            return LAPredict(dataset=dataset, project=project, device=device)
        case "lr":
            return LogisticRegression(dataset=dataset, project=project, device=device)
        case _:
            raise Exception("No such model")

def inferencing(params):
    logger("Start DefectGuard")
    start_whole_process_time = time.time()

    # create save folders
    dg_cache_path = f"{params.dg_save_folder}/dg_cache"
    folders = ["save", "repo", "dataset"]
    if not os.path.exists(dg_cache_path):
        os.mkdir(dg_cache_path)
    for folder in folders:
        if not os.path.exists(os.path.join(dg_cache_path, folder)):
            os.mkdir(os.path.join(dg_cache_path, folder))

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
        "repo_save_path": f"{dg_cache_path}/save",
        "extractor_save": True,
        "create_dataset": False,
    }

    if params.mode == "remote":
        cfg["repo_clone_path"] = os.path.join(params.dg_save_folder, "repo")
        cfg["repo_clone_url"] = f"https://github.com/{params.repo_owner}/{params.repo_name}.git"
    else:
        cfg["extractor_check_uncommit"] = params.uncommit
        
    cfg = Namespace(**cfg)

    # extract repo
    start_extract_time = time.time()
    
    crawler = BasicPipeline(cfg)
    crawler.set_repo(cfg)
    crawler.run()

    if len(params.commit_hash) == 0:
        params.commit_hash = crawler.extractor.get_top_commits(params.top)    
    commits, features, not_found_ids = crawler.repo.get_commits(params.commit_hash)
    user_input["commit_hashes"] = [id for id in params.commit_hash if id not in not_found_ids]
    user_input["features"] = features
    user_input["commit_info"] = []
    for i in range(len(user_input["commit_hashes"])):
        user_input["commit_info"].append(commit_to_info(commits[i]))

    end_extract_time = time.time()

    if len(user_input["commit_info"]) > 0:
        # Load Model
        model_list = {}
        for model in params.models:
            model_list[model] = init_model(
                model, params.dataset, params.cross, params.device
            )

        # Inference
        outputs = {"no_code_change_commit": not_found_ids}
        for model in model_list.keys():
            start_inference_time = time.time()

            outputs[model] = (
                sort_by_predict(model_list[model].handle(user_input))
                if params.sort
                else model_list[model].handle(user_input)
            )

            end_inference_time = time.time()

            logger(
                f"Inference time of {model}: {end_inference_time - start_inference_time}"
            )

        if params.vsc:
            outputs = vsc_output(outputs)

        print(json.dumps(outputs, indent=2))

        if not params.no_warning:
            defect_outputs = check_threshold(outputs, params.threshold)
            for model, commits in defect_outputs.items():
                for commit in commits:
                    raise Exception(
                        f"{model}: commit {commit['commit_hash']} has {commit['predict']} chance of being defect. Please review it."
                    )

    end_whole_process_time = time.time()

    logger(f"Extract features time: {end_extract_time - start_extract_time}")
    logger(f"Whole process time: {end_whole_process_time - start_whole_process_time}")
    logger(f"Whole process time: {end_whole_process_time - start_whole_process_time}")