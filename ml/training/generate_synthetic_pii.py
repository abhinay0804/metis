import json
import random
import os
from faker import Faker

fake = Faker()

PII_TEMPLATES = [
    "Please contact {name} at {email} or call {phone}. Their address is {address}.",
    "The account number for {name} is {ssn} and the credit card on file is {credit_card}.",
    "Employee {name} lives at {address}. Emergency contact: {phone}.",
    "Invoice for {name}: Please send payment to {address}. Email confirmation to {email}.",
    "My SSN is {ssn} and my credit card is {credit_card}. Name: {name}.",
    "Forward the documents to {email} and CC {name}.",
    "Contact {name} ({phone}) for support. Address: {address}.",
    "User {name} registered with {email} and provided SSN: {ssn}.",
    "Billing details: {name}, {credit_card}, {address}.",
    "Reach out to {name} via {email} or {phone}. SSN on record: {ssn}."
]

def generate_pii_document():
    template = random.choice(PII_TEMPLATES)
    
    # Generate fake data
    data = {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "address": fake.address().replace('\n', ', '),
        "ssn": fake.ssn(),
        "credit_card": fake.credit_card_number()
    }
    
    # Fill template
    text = template.format(**data)
    
    # Store the exact strings that were inserted
    entities = []
    for key, value in data.items():
        if value in text:
            start = text.find(value)
            end = start + len(value)
            entities.append({
                "entity": key.upper(),
                "value": value,
                "start": start,
                "end": end
            })
            
    return {
        "text": text,
        "entities": entities
    }

def main(num_samples=1000, output_path="synthetic_pii_data.json"):
    print(f"Generating {num_samples} synthetic PII documents...")
    dataset = []
    for _ in range(num_samples):
        dataset.append(generate_pii_document())
        
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)
        
    print(f"Dataset saved to {output_path}")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_pii_data.json")
    main(100, out_path)
