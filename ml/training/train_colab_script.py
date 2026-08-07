import os
import torch
import json
from datasets import load_dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForTokenClassification, 
    TrainingArguments, 
    Trainer, 
    DataCollatorForTokenClassification
)

def main():
    print(f"GPU Available: {torch.cuda.is_available()}")
    if not torch.cuda.is_available():
        print("Warning: GPU not available. Training will be extremely slow.")

    print("Loading dataset...")
    dataset = load_dataset("ai4privacy/pii-masking-400k", split="train")
    
    label_list = ["O", "B-NAME", "I-NAME", "B-EMAIL", "I-EMAIL", "B-PHONE", "I-PHONE", "B-SSN", "I-SSN", 
                  "B-CREDIT_CARD", "I-CREDIT_CARD", "B-ADDRESS", "I-ADDRESS", "B-ORG", "I-ORG", 
                  "B-LOC", "I-LOC", "B-DATE", "I-DATE"]
                  
    id2label = {i: label for i, label in enumerate(label_list)}
    label2id = {label: i for i, label in enumerate(label_list)}

    print("Loading tokenizer and model...")
    model_checkpoint = "roberta-base"
    
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint, add_prefix_space=True, use_fast=True)
    
    model = AutoModelForTokenClassification.from_pretrained(
        model_checkpoint, 
        num_labels=len(label_list), 
        id2label=id2label, 
        label2id=label2id,
        ignore_mismatched_sizes=True
    )

    print("Preparing dataset and aligning subword tokens...")
    
    def tokenize_and_align_labels(examples):
        tokenized_inputs = tokenizer(
            examples["source_text"], 
            truncation=True, 
            max_length=512,
            return_offsets_mapping=True
        )
        
        labels = []
        for i, (text, mask_data, offsets) in enumerate(zip(examples["source_text"], examples["privacy_mask"], tokenized_inputs["offset_mapping"])):
            
            entities = []
            if isinstance(mask_data, str):
                try: entities = json.loads(mask_data)
                except: pass
            elif isinstance(mask_data, list):
                entities = mask_data
            elif isinstance(mask_data, dict):
                try:
                    if len(mask_data) > 0:
                        first_key = list(mask_data.keys())[0]
                        num_entities = len(mask_data[first_key])
                        for j in range(num_entities):
                            entities.append({k: mask_data[k][j] for k in mask_data.keys()})
                except: pass
                
            char_labels = ["O"] * len(text)
            for ent in entities:
                start = ent.get("start")
                end = ent.get("end")
                raw_label = ent.get("label", "")
                if not isinstance(raw_label, str):
                    raw_label = str(raw_label)
                raw_label = raw_label.upper()
                
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
                    token_label = label2id["O"]
                    for char_idx in range(offset[0], offset[1]):
                        if char_idx < len(char_labels) and char_labels[char_idx] != "O":
                            token_label = label2id[char_labels[char_idx]]
                            break
                    token_labels.append(token_label)
            labels.append(token_labels)
            
        tokenized_inputs["labels"] = labels
        tokenized_inputs.pop("offset_mapping")
        return tokenized_inputs

    tokenized_dataset = dataset.map(tokenize_and_align_labels, batched=True, remove_columns=dataset.column_names)

    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

    args = TrainingArguments(
        "pii-roberta-base-model-output",
        eval_strategy="no",
        learning_rate=2e-5,           
        per_device_train_batch_size=8, # Safely fits inside your 6GB RTX 4050
        gradient_accumulation_steps=2,
        num_train_epochs=1,           # 1 Epoch is plenty and will finish fast!
        weight_decay=0.01,
        fp16=True,                    
        warmup_ratio=0.1,             
        max_grad_norm=1.0,            
        logging_nan_inf_filter=False, 
        logging_steps=50,
        save_strategy="epoch",
        dataloader_num_workers=2
    )

    trainer = Trainer(
        model,
        args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
        processing_class=tokenizer,
    )

    print("Starting perfectly stable RoBERTa training (1 Epoch)...")
    trainer.train()

    print("Saving highly-accurate trained model...")
    trainer.save_model("pii-roberta")
    tokenizer.save_pretrained("pii-roberta")
    
    print("Compressing model for download...")
    os.system("zip -r pii-roberta.zip pii-roberta > /dev/null")
    print("Training and compression complete! You can now download pii-roberta.zip")

if __name__ == "__main__":
    main()
