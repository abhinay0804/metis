import os
from huggingface_hub import snapshot_download

def download_dataset():
    print("Downloading logo dataset from Hugging Face...")
    local_dir = os.path.abspath("data/logo_dataset")
    os.makedirs(local_dir, exist_ok=True)
    
    snapshot_download(
        repo_id="haydarkadioglu/brand-eye-dataset",
        repo_type="dataset",
        local_dir=local_dir,
        max_workers=4
    )
    print(f"Dataset successfully downloaded to {local_dir}")

if __name__ == "__main__":
    download_dataset()
