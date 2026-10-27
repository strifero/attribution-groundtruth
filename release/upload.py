import shutil, glob
from huggingface_hub import HfApi

S = "/home/sean/tda/release/stage"
for d in glob.glob(f"{S}/**/__pycache__", recursive=True):
    shutil.rmtree(d)
api = HfApi()
api.create_repo("strifero/attribution-groundtruth", repo_type="dataset", exist_ok=True)
api.upload_folder(repo_id="strifero/attribution-groundtruth", repo_type="dataset", folder_path=f"{S}/dataset",
                  commit_message="Ground-truth training-data attribution benchmark")
print("dataset done", flush=True)
for r in "AB":
    rid = f"strifero/tda-124m-{r}"
    api.create_repo(rid, exist_ok=True)
    api.upload_large_folder(repo_id=rid, repo_type="model", folder_path=f"{S}/models/tda-124m-{r}")
    print(rid, "done", flush=True)
print("UPLOAD DONE")
