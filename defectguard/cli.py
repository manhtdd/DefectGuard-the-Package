import argparse, os, time, json, random
from .utils.utils import (
    commit_to_info,
    SRC_PATH,
    sort_by_predict,
    vsc_output,
    check_threshold,
)
from .JITCrawler import BasicPipeline
from .models import (
    DeepJIT,
    CC2Vec,
    SimCom,
    LAPredict,
    LogisticRegression,
    TLELModel,
    JITLine,
)
from .utils.logger import ic
from argparse import Namespace
from datetime import datetime
import numpy as np
import torch

__version__ = "0.1.32"


def seed_torch(seed=42):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    # torch.cuda.manual_seed_all(seed) # if you are using multi-GPU.
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


seed_torch()


def read_args():
    available_languages = [
        "Python",
        "Java",
        "C++",
        "C",
        "C#",
        "JavaScript",
        "TypeScript",
        "Ruby",
        "PHP",
        "Go",
        "Swift",
    ]
    models = ["deepjit", "cc2vec", "simcom", "lapredict", "tlel", "jitline", "la", "lr"]
    dataset = ["gerrit", "go", "platform", "jdt", "qt", "openstack"]
    modes = ["local", "remote"]
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument("-dg_save_folder", type=str, required=True, help="")
    parser.add_argument(
        "-mode", type=str, default="local", help="Mode of extractor", choices=modes
    )
    parser.add_argument("-repo_name", type=str, required=True, help="Repo name")
    parser.add_argument("-repo_owner", type=str, default="", help="Repo owner name")
    parser.add_argument(
        "-repo_path", type=str, default="", help="Path to git repository"
    )
    parser.add_argument(
        "-commit_hash", nargs="+", type=str, default=[], help="List of commit hashes"
    )
    parser.add_argument("-top", type=int, default=0, help="Number of top commits")
    parser.add_argument(
        "-main_language",
        type=str,
        default="",
        choices=available_languages,
        help="Main language of repo",
    )

    parser.add_argument(
        "-models",
        nargs="+",
        type=str,
        default=[],
        choices=models,
        help="List of deep learning models",
    )
    parser.add_argument(
        "-dataset",
        type=str,
        default="openstack",
        choices=dataset,
        help="Dataset's name",
    )
    parser.add_argument("-cross", action="store_true", help="Cross project")
    parser.add_argument(
        "-uncommit",
        action="store_true",
        help="Include uncommit in list when using -top",
    )

    parser.add_argument(
        "-device", type=str, default="cpu", help="Eg: cpu, cuda, cuda:1"
    )

    parser.add_argument(
        "-sort", action="store_true", help="Sort output of model by predict score"
    )
    parser.add_argument("-vsc", action="store_true", help="Output for vsc")
    parser.add_argument(
        "-debug", action="store_true", help="Turn on system debug print"
    )
    parser.add_argument(
        "-log_to_file", action="store_true", help="Logging to file instead of stdout"
    )

    parser.add_argument(
        "-threshold", type=float, default=0.5, help="Threshold for warning"
    )
    parser.add_argument(
        "-no_warning", action="store_true", help="Supress output warning"
    )

    return parser


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


def main():
    params = read_args().parse_args()

    if not params.debug:
        ic.disable()

    if params.log_to_file:
        # Create a folder named 'logs' if it doesn't exist
        if not os.path.exists(f"{SRC_PATH}/logs"):
            os.makedirs(f"{SRC_PATH}/logs")

        # Define a file to log IceCream output
        log_file_path = os.path.join(f"{SRC_PATH}/logs", "logs.log")

        # Replace logging configuration with IceCream configuration
        ic.configureOutput(
            prefix=f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | ',
            outputFunction=lambda x: open(log_file_path, "a").write(x + "\n"),
        )

    ic("Start DefectGuard")
    start_whole_process_time = time.time()

    # create save folders
    folders = ["save", "repo", "dataset"]
    for folder in folders:
        os.mkdir(os.path.join(params.dg_save_folder, folder))

    user_input = {
        "models": params.models,
        "dataset": params.dataset,
        "cross": params.cross,
        "device": params.device,
    }

    ic(user_input)

    # User's input handling
    cfg = {
        "mode": params.mode,
        "repo_owner": params.repo_owner,
        "repo_name": params.repo_name,
        "repo_path": params.repo_path,
        "main_language": params.main_language,
        "repo_save_path": os.path.join(params.dg_save_folder, "save"),
        "extractor_save": True,
        "extractor_check_uncommit": params.uncommit,
    }
    if params.mode == "remote":
        cfg["repo_clone_path"] = os.path.join(params.dg_save_folder, "repo")
        cfg["repo_clone_url"] = f"https://github.com/{params.repo_owner}/{params.repo_name}.git"
    cfg = Namespace(**cfg)

    # extract repo
    start_extract_time = time.time()
    
    crawler = BasicPipeline(cfg)
    crawler.run()
    if len(params.commit_hash) == 0:
        params.commit_hash = crawler.extractor.get_top_commits(params.top)    
    commits, features, not_found_ids = crawler.repo.get_commits(params.commit_hash)
    user_input["commit_hashes"] = [
        id for id in params.commit_hash if id not in not_found_ids
    ]
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

            ic(
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

    ic(f"Extract features time: {end_extract_time - start_extract_time}")
    ic(f"Whole process time: {end_whole_process_time - start_whole_process_time}")
    ic(f"Whole process time: {end_whole_process_time - start_whole_process_time}")
