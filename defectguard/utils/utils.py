from importlib.resources import files
import os, gdown

SRC_PATH = str(files('defectguard'))

IDS = {
    'deepjit': {
        'hyperparameters': '1US-qs1Ly9wfRADcEMLBtTa8Ao91wNwOv',
        'platform': '11Qjj84btTuqbYGpphmin0spMuGgJerNa',
        'platform_cross': '1BTo26TU2G58OsBxoM-EidyijfnQZXuc4',
        'platform_dictionary': '1C6nVSr0wLS8i8bH_IptCUKdqrdiSngcv',
        'platform_dictionary_cross': '1XY4J3bCKo7IWMXcA2DJqVzzAD8XOZi-b',
    },
    'cc2vec': {
        'qt_dictionary': '1GTgkEcZdwVDzp0Tq86Uch_j5f4assfSU',
        'dextended_qt': '1uuSeYee40Azw1jWD2ln287GZ49ApTMxL',
        'hyperparameters': '1Zim5j4eKfl84r4mGDmRELwAwg8oVQ5uJ',
        'cc2vec_qt': '1-ZQjygr6myPj4ml-VyyiyrGKiL0HV2Td',
    },
    'simcom': {
        'hyperparameters': '1Y9pt5EShp5Z2Q2Ff6EjHp0fxByXWViw6',
        'sim_qt': '1ToELcINTQwmek24M8VvB-4xfiB-TZbkc',
        'sim_platform': '1SJ8UnaMQlaB58E7VsQWbHFmh2ms0QFg_',
        'sim_openstack': '1iJDpDLL19d_dp7mdjxu0ADqN25Hgyxuk',
        'sim_jdt': '1PPz385vq3cuuTf5pqM4k4c018rXoN1If',
        'sim_go': '1nknqQPbgJJXXCJ5pa4G27ymcEY2goxBq',
        'sim_gerrit': '1CmsiNXe5qXtEw6rG7IXLq2KVLslhOcij',
        'platform_dictionary': '19h6kUCiHXTsijXUEArxSx4afS4hdKrvx',
        'com_platform': '1KmUkYFVaH34kBA4pW8qXgv1JV9qCRtkx',
    },
    'tlel': {
        'qt': '1jQ5Uv-7t-qHjV0O3zAYaLB29QCZPY8nE',
        'platform': '1vS26ng_kZ5gdYESyWrfciMacXz74AzhZ',
        'openstack': '1yCOI_5inFnxH1EDS2JpA282UN7Zc1AXV',
        'jdt': '1GUEC7kFCybuoEetr-1Tis_6EmaWXgWwG',
        'go': '1siGmkBSq5qcuoxnhxo2Gc2_IhrVnLmWh',
        'gerrit': '1CI326L7vwokRXxwRdufzOvKtciPUj_TX',
    },
    'jitline': '',
    'lapredict': {
        'qt': '1sginH8lVsEupRtEXsBpFJWR3HHGoW7MS',
        'platform': '',
        'openstack': '',
        'jdt': '',
        'go': '',
        'gerrit': '',
    },
    'lr': {
        'qt': '1xpBW5KZ18E-2teMTCsIrBjGDuO89ceDf',
        'platform': '',
        'openstack': '',
        'jdt': '',
        'go': '',
        'gerrit': '',
    },
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

def create_download_list(model_name, dataset):
    download_list = []
    dictionary = f'{dataset}_dictionary'
    version = f'{dataset}'

    if model_name == 'simcom':
        sim_dataset = f'sim_{version}'
        com_dataset = f'com_{version}'
        download_list.append(sim_dataset)
        download_list.append(com_dataset)
        download_list.append('hyperparameters')
        download_list.append(dictionary)
    elif model_name == 'cc2vec':
        cc2vec_dataset = f'cc2vec_{version}'
        dextended_dataset = f'dextended_{version}'
        download_list.append(cc2vec_dataset)
        download_list.append(dextended_dataset)
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

def download_folder(model_name, dataset, project=None):
    # Check if the file exists locally
    folder_path = f'{SRC_PATH}/models/metadata/{model_name}'

    if not os.path.exists(folder_path):
        # File doesn't exist, download it
        # Create the directory if it doesn't exist
        print(f"Directory: {folder_path}")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # Download model's metadata
    download_list = create_download_list(model_name, dataset)
    for item in download_list:
        download_file(IDS[model_name][item], f'{folder_path}/{item}')

def extract_diff(diff):
    num_added_lines = 0
    list_file_changes = []
    for file_elem in list(diff.items()):
        file_path = file_elem[0]
        file_val = file_elem[1]
            
        file = {"file_name": file_path, "code_changes":[]}
        for ab in file_val["content"]:
            if "ab" in ab:
                continue
            hunk = {"added_code":[], "removed_code":[]}
            if "a" in ab:
                hunk["removed_code"] += [line.strip() for line in ab["a"]]
            if "b" in ab:
                hunk["added_code"] += [line.strip() for line in ab["b"]]
                num_added_lines += len(ab["b"])
            hunk["added_code"] = "\n".join(hunk["added_code"])
            hunk["removed_code"] = "\n".join(hunk["removed_code"])
            file["code_changes"].append(hunk)
        list_file_changes.append(file)
    return list_file_changes, num_added_lines

def commit_to_info(commit):
    if commit:
        list_file_changes, num_added_lines = extract_diff(commit["diff"])
        
        return {
                'commit_hash': commit["commit_id"],
                'commit_message': commit['msg'],
                'main_language_file_changes': list_file_changes,
                'num_added_lines_in_main_language': num_added_lines,
            }
    else:
        return {}