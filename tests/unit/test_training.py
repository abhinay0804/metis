import torch
import json
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForTokenClassification

print("Loading dataset...")
dataset = load_dataset("ai4privacy/pii-masking-400k", split="train[:50]")

label_list = ["O", "B-NAME", "I-NAME", "B-EMAIL", "I-EMAIL", "B-PHONE", "I-PHONE", "B-SSN", "I-SSN", 
                "B-CREDIT_CARD", "I-CREDIT_CARD", "B-ADDRESS", "I-ADDRESS", "B-ORG", "I-ORG", 
                "B-LOC", "I-LOC", "B-DATE", "I-DATE"]
                
id2label = {i: label for i, label in enumerate(label_list)}
label2id = {label: i for i, label in enumerate(label_list)}

tokenizer = AutoTokenizer.from_pretrained("roberta-base", add_prefix_space=True, use_fast=True)
model = AutoModelForTokenClassification.from_pretrained(
    "roberta-base", 
    num_labels=len(label_list), 
    id2label=id2label, 
    label2id=label2id,
    ignore_mismatched_sizes=True
)

def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(
        examples["source_text"], 
        truncation=True, 
        max_length=512,
        return_offsets_mapping=True
    )
    
    labels = []
    for i, (text, mask_json, offsets) in enumerate(zip(examples["source_text"], examples["privacy_mask"], tokenized_inputs["offset_mapping"])):
        try:
            entities = json.loads(mask_json)
        except:
            entities = []
            
        char_labels = ["O"] * len(text)
        for ent in entities:
            start = ent.get("start")
            end = ent.get("end")
            raw_label = ent.get("label", "").upper()
            
            if start is None or end is None:
                continue
            
            mapped_label = "O"
            if "NAME" in raw_label: mapped_label = "NAME"
            elif "EMAIL" in raw_label: mapped_label = "EMAIL"
            elif "PHONE" in raw_label or "TELEPHONE" in raw_label: mapped_label = "PHONE"
            elif "SSN" in raw_label or "ID" in raw_label or "PASSPORT" in raw_label: mapped_label = "SSN"
            elif "CREDIT" in raw_label or "IBAN" in raw_label or "ACCOUNT" in raw_label: mapped_label = "CREDIT_CARD"
            elif "CITY" in raw_label or "STREET" in raw_label or "ZIP" in raw_label or "BUILDING" in raw_label or "STATE" in raw_label or "COUNTRY" in raw_label: mapped_label = "ADDRESS"
            elif "ORG" in raw_label or "COMPANY" in raw_label: mapped_label = "ORG"
            elif "LOC" in raw_label: mapped_label = "LOC"
            elif "DATE" in raw_label or "DOB" in raw_label or "TIME" in raw_label or "YEAR" in raw_label: mapped_label = "DATE"
            
            if mapped_label == "O":
                continue
                
            char_labels[start] = f"B-{mapped_label}"
            for j in range(start + 1, end):
                char_labels[j] = f"I-{mapped_label}"
        
        token_labels = []
        for offset in offsets:
            if offset[0] == 0 and offset[1] == 0:
                token_labels.append(-100)
            else:
                char_label = char_labels[offset[0]]
                if char_label in label2id:
                    token_labels.append(label2id[char_label])
                else:
                    token_labels.append(label2id["O"])
        labels.append(token_labels)
        
    tokenized_inputs["labels"] = labels
    tokenized_inputs.pop("offset_mapping")
    return tokenized_inputs

print("Tokenizing...")
tokenized_dataset = dataset.map(tokenize_and_align_labels, batched=True, remove_columns=dataset.column_names)

from transformers import DataCollatorForTokenClassification
data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

print("Preparing batch...")
batch = data_collator([tokenized_dataset[i] for i in range(4)])
print(f"Batch labels unique: {torch.unique(batch['labels'])}")
print(f"Batch labels shape: {batch['labels'].shape}")
print(f"Batch input_ids shape: {batch['input_ids'].shape}")

optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

for step in range(5):
    outputs = model(**batch)
    loss = outputs.loss
    print(f"Step {step} Loss: {loss.item()}")
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
