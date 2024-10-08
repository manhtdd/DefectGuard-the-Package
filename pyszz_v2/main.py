import argparse
import json
import logging as log
import os
from time import time as ts

import dateparser
import yaml
from typing import Dict
from szz.ag_szz import AGSZZ
from szz.aszz.a_szz import ASZZ
from szz.b_szz import BaseSZZ
from szz.util.check_requirements import check_requirements
from szz.dfszz.df_szz import DFSZZ
from szz.l_szz import LSZZ
from szz.ma_szz import MASZZ, DetectLineMoved
from szz.r_szz import RSZZ
from szz.ra_szz import RASZZ
from szz.pd_szz import PyDrillerSZZ
from szz.vszz.v_szz import VSZZ
from szz.common.issue_date import parse_issue_date
from pathlib import Path
import random
from multiprocessing import Manager

def main(input_json: str, out_json: str, conf: Dict, repos_dir: str, id: int = 0):    
    with open(input_json, 'r') as in_file:
        bugfix_commits = json.loads(in_file.read())
    tot = len(bugfix_commits)

    # if os.path.exists(out_json):
    #     out_json = out_json.replace('.json', f'.{random.randint(1, 99)}.json')
    with open(out_json, 'w') as out:
        json.dump(bugfix_commits, out, indent=4)

    log.basicConfig(filename= f'log/{input_json}_{id}.log',level=log.INFO, format='%(asctime)s :: %(funcName)s - %(levelname)s :: %(message)s')
    log.getLogger('pydriller').setLevel(log.WARNING)

    for i, commit in enumerate(bugfix_commits):
        bug_inducing_commits = set()
        repo_name = commit['repo_name']
        repo_url = f'https://test:test@github.com/{repo_name}.git'  # using test:test as git login to skip private repos during clone
        fix_commit = commit['fix_commit_hash']

        log.info(f'{i + 1} of {tot}: {repo_name} {fix_commit}')
        
        issue_date = None
        if conf.get('issue_date_filter', None):
            issue_date = parse_issue_date(commit)
        
        szz_name = conf['szz_name']
        if szz_name == 'b':
            b_szz = BaseSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = b_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=True)
            bug_inducing_commits = b_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=issue_date)
        elif szz_name == 'ag':
            ag_szz = AGSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = ag_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=True)
            bug_inducing_commits = ag_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        max_change_size=conf.get('max_change_size'),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=issue_date)
        elif szz_name == 'ma':
            ma_szz = MASZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = ma_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=True)
            bug_inducing_commits = ma_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        max_change_size=conf.get('max_change_size'),
                                        detect_move_from_other_files=DetectLineMoved(conf.get('detect_move_from_other_files')),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=issue_date,
                                        filter_revert_commits=conf.get('filter_revert_commits', False))
        elif szz_name == 'r':
            r_szz = RSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = r_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=True)
            bug_inducing_commits = r_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        max_change_size=conf.get('max_change_size'),
                                        detect_move_from_other_files=DetectLineMoved(conf.get('detect_move_from_other_files')),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=issue_date,
                                        filter_revert_commits=conf.get('filter_revert_commits', False))
        elif szz_name == 'l':
            l_szz = LSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = l_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=True)
            bug_inducing_commits = l_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        max_change_size=conf.get('max_change_size'),
                                        detect_move_from_other_files=DetectLineMoved(conf.get('detect_move_from_other_files')),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=issue_date,
                                        filter_revert_commits=conf.get('filter_revert_commits', False))
        elif szz_name == 'ra':
            ra_szz = RASZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = ra_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=True)
            bug_inducing_commits = ra_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        max_change_size=conf.get('max_change_size'),
                                        detect_move_from_other_files=DetectLineMoved(conf.get('detect_move_from_other_files')),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=issue_date,
                                        filter_revert_commits=conf.get('filter_revert_commits', False))
        elif szz_name == 'pd':
            pd_szz = PyDrillerSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = pd_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=True)
            bug_inducing_commits = pd_szz.find_bic(fix_commit_hash=fix_commit,
                                                   impacted_files=imp_files,
                                                   issue_date_filter=conf.get('issue_date_filter'),
                                                   issue_date=issue_date)
        elif szz_name == 'a':
            a_szz = ASZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            bug_inducing_commits = a_szz.start(fix_commit_hash=fix_commit, commit_issue_date=issue_date, **conf)

        elif szz_name == 'df':
            df_szz = DFSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            bug_inducing_commits = df_szz.start(fix_commit_hash=fix_commit, commit_issue_date=issue_date, **conf)
        elif szz_name == "v":
            v_szz = VSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir, ast_map_path=conf.get('ast_map_path'))
            imp_files = v_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=True)
            bug_inducing_commits = v_szz.find_bic(fix_commit_hash=fix_commit,
                                            impacted_files=imp_files,
                                            ignore_revs_file_path=None,
                                            issue_date_filter=conf.get('issue_date_filter'),
                                            issue_date=issue_date)

        else:
            log.info(f'SZZ implementation not found: {szz_name}')
            exit(-3)

        log.info(f"result: {bug_inducing_commits}")
        if szz_name == "v":
            bugfix_commits[i]["inducing_commit_hash"] = [bic for bic in bug_inducing_commits if bic]
        else:
            bugfix_commits[i]["inducing_commit_hash"] = [bic.hexsha for bic in bug_inducing_commits if bic]
        with open(out_json, 'w') as out:
            json.dump(bugfix_commits, out, indent=4)

    log.info(f"results saved in {out_json}")
    log.info("+++ DONE +++")

def split_json(input_json: str, input_name: str, num_core: int = 1):
    with open(input_json, 'r') as in_file:
        bugfix_commits = json.loads(in_file.read())
    tot = len(bugfix_commits)
    sublist_length = tot // num_core

    sublists = [bugfix_commits[i:i + sublist_length] for i in range(0, tot, sublist_length)]
    out_file = []
    for id in range(num_core):
        out_file.append(f'temp/{input_name}_{id}.json')
        with open(out_file[id], 'w') as out:
            json.dump(sublists[id], out, indent=4)
    return out_file

if __name__ == "__main__":
    check_requirements()

    parser = argparse.ArgumentParser(description='USAGE: python main.py <bugfix_commits.json> <conf_file path> <repos_directory(optional)>\n* If <repos_directory> is not set, pyszz will download each repository')
    parser.add_argument('input_json', type=str, help='/path/to/bug-fixes.json')
    parser.add_argument('conf_file', type=str, help='/path/to/configuration-file.yml')
    parser.add_argument('repos_dir', type=str, nargs='?', help='/path/to/repo-directory')
    parser.add_argument('num_core', type=int, default=1, help='number of cores, default = 1')
    args = parser.parse_args()

    if not os.path.isfile(args.input_json):
        log.error('invalid input json')
        exit(-2)
    if not os.path.isfile(args.conf_file):
        log.error('invalid conf file')
        exit(-2)

    with open(args.conf_file, 'r') as f:
        conf = yaml.safe_load(f)

    log.info(f"parsed conf yml '{args.conf_file}': {conf}")
    szz_name = conf['szz_name']
    input_name = args.input_json.rsplit('/', 1)[-1].split('.')[0]

    out_dir = 'out'
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    conf_file_name = Path(args.conf_file).name.split('.')[0]

    input_json = split_json(args.input_json, input_name, args.num_core)
    out_json = [os.path.join(out_dir, f'bic_{conf_file_name}_{input_name}_{id}.json') for id in range(args.num_core)]

    if not szz_name:
        log.error('The configuration file does not define the SZZ name. Please, fix.')
        exit(-3)

    log.info(f'Launching {szz_name}-szz')

    manager = Manager()
    import concurrent.futures as cf
    futures = []
    with cf.ProcessPoolExecutor(args.num_core) as pp:
        for id in range(args.num_core):
            futures.append(pp.submit(main, input_json[id], out_json[id], conf, args.repos_dir))
    for future in cf.as_completed(futures):
         future.result()
