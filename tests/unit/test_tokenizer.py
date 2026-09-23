import sys
from transformers import AutoTokenizer, AutoModelForTokenClassification

model_path = "/app/ml/models/pii-roberta"
try:
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    print("Tokenizer loaded!")
    text = "JOHN DOE EMP001234 JANE SMITH EMP005678"
    tokens = tokenizer(text)
    print("Tokens:", tokens)
    print("Decoded:", tokenizer.decode(tokens['input_ids']))
    
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    import torch
    with torch.no_grad():
        outputs = model(torch.tensor([tokens['input_ids']]))
        preds = outputs.logits.argmax(dim=-1)[0]
    
    print("Preds:", preds)
except Exception as e:
    import traceback
    traceback.print_exc()
