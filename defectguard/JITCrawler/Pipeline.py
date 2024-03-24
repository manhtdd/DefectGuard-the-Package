from .core import Repository, Extractor
from .core.utils import clone_repo


class BasicPipeline:
    def __init__(self, cfg):
        # init extractor
        self.extractor = Extractor(
            num_commits_per_file=0,
            language=cfg.repo_language,
            save=cfg.extractor_save,
            check_uncommit=cfg.extractor_check_uncommit,
        )


    def set_repo(self, cfg):
        assert cfg.mode in ["local", "remote"], "Invalid mode: {}".format(cfg.mode)
        if cfg.mode == "local":
            self.repo = self.local_repo(cfg)
        else:
            self.repo = self.remote_repo(cfg)

    def local_repo(self, cfg):
        repo = Repository(
            cfg.repo_owner,
            cfg.repo_name,
            cfg.repo_save_path,
            cfg.repo_path,
            cfg.repo_language,
        )
        return repo

    def remote_repo(self, cfg):
        clone_repo(
            cfg.repo_clone_path,
            cfg.repo_owner,
            cfg.repo_name,
            cfg.repo_clone_url,
        )
        repo = Repository(
            cfg.repo_owner,
            cfg.repo_name,
            cfg.repo_save_path,
            cfg.repo_clone_path,
            cfg.repo_language,
        )
        return repo

    def run(self):
        print("Running repository: {}/{}".format(self.repo.owner, self.repo.name))
        # extract repo
        self.extractor.set_repo(self.repo)
        self.extractor.run()