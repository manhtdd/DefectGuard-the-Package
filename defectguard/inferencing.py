import os, json, time
from .utils.logger import logger
from .models import (
    DeepJIT,
    CC2Vec,
    SimCom,
    LAPredict,
    LogisticRegression,
    TLELModel as TLEL,
    JITLine,
)
from .utils.utils import (
    sort_by_predict,
    load_json
)
from .JITCrawler.core.Fetcher import Fetcher

def init_model(model_name, language, device):
    match model_name:
        case "deepjit":
            return DeepJIT(language=language, device=device)
        case "cc2vec":
            return CC2Vec(language=language, device=device)
        case "simcom":
            return SimCom(language=language, device=device)
        case "lapredict":
            return LAPredict(language=language)
        case "tlel":
            return TLEL(language=language)
        case "jitline":
            return JITLine(language=language)
        case "la":
            return LAPredict(language=language)
        case "lr":
            return LogisticRegression(language=language)
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
        "device": params.device,
    }

    logger(user_input)

    start_extract_time = time.time()

    access_key = load_json(params.access_key)
    fetcher = Fetcher(owner=params.repo_owner, repo=params.repo_name, access_token=access_key)
    pull_requests = fetcher.get_pull_request_data(params.pull_numbers)

    logger(pull_requests)
    
    end_extract_time = time.time()

    if len(pull_requests) > 0:
        # Load Model
        model_list = {}
        for model in params.models:
            model_list[model] = init_model(model, params.repo_language, params.device)

        # Inference
        outputs = {}
        for model in model_list.keys():
            start_inference_time = time.time()

            outputs[model] = (
                sort_by_predict(model_list[model].handle(pull_requests))
                if params.sort
                else model_list[model].handle(pull_requests)
            )

            end_inference_time = time.time()

            logger(f"Inference time of {model}: {end_inference_time - start_inference_time}")

        print(json.dumps(outputs, indent=2))

    else:
        raise Exception("No pull request to inference. Please check if your pull requests contain any code change.")

    end_whole_process_time = time.time()

    logger(f"Extract features time: {end_extract_time - start_extract_time}")
    logger(f"Whole process time: {end_whole_process_time - start_whole_process_time}")
    logger(f"Whole process time: {end_whole_process_time - start_whole_process_time}")