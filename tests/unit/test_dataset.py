from datasets import load_dataset

ds = load_dataset("ai4privacy/pii-masking-400k", split="train[:1]")
print(ds[0])
print(ds.features)
