from importlib.resources import files
import os, gdown

SRC_PATH = str(files('defectguard'))

IDS = {
    'deepjit': {
        'hyperparameters': '18TIg-2DhxI0Ou0vdUg5g8nx6c5GHEzWQ',
        'java': '1ZDCKjsXzwicIRLtfKJi99QgHLHr9wyx1',
        'java_dictionary': '',
        'go': '1vf6LWG2BVkvgl5VOpxguAXYuIITtPOOs',
        'go_dictionary': '',
        'cpp': '1gyhM5FCx9SNOoW7GGVHphBYTD5wehjGP',
        'cpp_dictionary': '',
    },
    'simcom': {
        'hyperparameters': '18TIg-2DhxI0Ou0vdUg5g8nx6c5GHEzWQ',
        'sim_java': '1jEvRx4OwScOHh35_5GhlrXdmpU8Hd1nr',
        'sim_cpp': '1pR-K23rUCAfN6ywRfju4OHZmtvw-Cm47',
        'sim_go': '14it5ddgzhVUo-EVBqNslp7fBtf-fSAqn',
        'com_java': '1K4vSRCsoD_Wd6wsYdwGyfwHePz1m8Ry-',
        'java_dictionary': '',
        'com_go': '1whs8xBN7DoYRcqVzsckatgsQRE2nzC7L',
        'go_dictionary': '',
        'com_cpp': '1kdys9wpy1OymNuEXHpgHzxwvRf87Itj4',
        'cpp_dictionary': '',
    },
    'tlel': {
        'java': '1aVQe7VMPq1Pa_6WOczsfXaIVsDEueCEE',
        'cpp': '1SUtyDCuUDuPAU684l9ivIHLieFsuSOSw',
        'go': '1ALIGUy_PSMubr5Ei_--f_XKXmApBljvv',
    },
    'lapredict': {
        'java': '1fHnfWL-0jNnJDYn7u4bJTnesC9Fe7dNq',
        'cpp': '1_utyJAKKUwzVlM9X4BvbPnWsZbQPo1Zy',
        'go': '1ZhMR1HuJW-x-IcndV_CvpG5VQlJpI16T',
    },
    'lr': {
        'java': '1TZDuG_E5_OCRbA3ZRkxQy1HJ3WeYLxTg',
        'cpp': '1Kuk_L47VYvBtgPShTx0CEld4_q5WYCD8',
        'go': '1Ly7tcC6z3xjZfNtwnd6WlznK17w7iTKS',
    },
    'cc2vec': '',
    'jitline': '',
}

def sort_by_predict(commit_list):
    # Sort the list of dictionaries based on the "predict" value in descending order
    sorted_list = sorted(commit_list, key=lambda x: x['predict'], reverse=True)
    return sorted_list

def vsc_output(data):
    # Extract the commit hashes from "no_code_change_commit"
    no_code_change_commits = data.get("no_code_change_commit", [])
    
    # Extract the "deepjit" list
    deepjit_list = data.get("deepjit", [])
    
    # Create a dictionary with keys from "no_code_change_commit" and values as -1
    new_dict = [{'commit_hash': commit, 'predict': -1} for commit in no_code_change_commits]
    
    # Append the new dictionary to the "deepjit" list
    deepjit_list += (new_dict)
    
    # Update the "deepjit" key in the original data
    data["deepjit"] = deepjit_list

    return data

def check_threshold(data, threshold):
    output = {}
    for model, predicts in data.items():
        if model == "no_code_change_commit":
            continue
        else:
            output[model] = []
        for predict in predicts:
            if predict['predict'] >= threshold:
                output[model].append(predict)
    
    return output

def create_download_list(model_name, language):
    download_list = []
    dictionary = f'{language}_dictionary'
    version = f'{language}'

    if model_name == 'simcom':
        sim_language = f'sim_{version}'
        com_language = f'com_{version}'
        download_list.append(sim_language)
        download_list.append(com_language)
        download_list.append('hyperparameters')
        download_list.append(dictionary)
    elif model_name == 'cc2vec':
        cc2vec_language = f'cc2vec_{version}'
        dextended_language = f'dextended_{version}'
        download_list.append(cc2vec_language)
        download_list.append(dextended_language)
        download_list.append('hyperparameters')
        download_list.append(dictionary)
    elif model_name == 'deepjit':
        download_list.append(version)
        download_list.append('hyperparameters')
        download_list.append(dictionary)
    else:
        download_list.append(version)
    
    return download_list

def download_file(file_id, folder_path):
    if not os.path.isfile(folder_path):
        gdown.download(f'https://drive.google.com/file/d/{file_id}/view?usp=sharing', output=folder_path, fuzzy=True)

def download_folder(model_name, language):
    # Check if the file exists locally
    folder_path = f'{SRC_PATH}/models/metadata/{model_name}'

    if not os.path.exists(folder_path):
        # File doesn't exist, download it
        # Create the directory if it doesn't exist
        print(f"Directory: {folder_path}")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # Download model's metadata
    download_list = create_download_list(model_name, language)
    for item in download_list:
        download_file(IDS[model_name][item], f'{folder_path}/{item}')