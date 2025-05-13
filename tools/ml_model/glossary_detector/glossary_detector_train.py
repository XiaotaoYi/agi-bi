import torch
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer
)
from datasets import Dataset
import evaluate
import numpy as np

# Disable MPS and force CPU usage
torch.backends.mps.enabled = False
torch.set_default_tensor_type(torch.FloatTensor)
device = torch.device("cpu")

# Label configuration
labels = ["O", "B-ABBR", "I-ABBR", "B-JARGON", "I-JARGON", "B-TERM", "I-TERM"]
label2id = {label: i for i, label in enumerate(labels)}
id2label = {i: label for i, label in enumerate(labels)}

# Initialize model and tokenizer
model_checkpoint = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForTokenClassification.from_pretrained(
    model_checkpoint,
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id,
    device_map="cpu"  # Force CPU device mapping
)
model = model.to(device)
model.eval()  # Set model to evaluation mode

# Sample training data with multiple entities (expand with your data)
train_examples = [
    {
        "text": "Show me top 3 market by TPV in 2024 and its monthly ASP trend",
        "entities": [
        {"start": 24, "end": 26, "label": "ABBR"},
        {"start": 52, "end": 54, "label": "ABBR"}
        ]
        },
        {
        "text": "Show me top 3 market by TPV in 2024",
        "entities": [
        {"start": 24, "end": 26, "label": "ABBR"}
        ]
        },
        {
        "text": "Compare GMV growth between P2P and B2B sectors last quarter",
        "entities": [
        {"start": 7, "end": 9, "label": "ABBR"},
        {"start": 25, "end": 27, "label": "ABBR"},
        {"start": 33, "end": 35, "label": "ABBR"}
        ]
        },
        {
        "text": "What's the current chargeback ratio for high-risk MCC categories?",
        "entities": [
        {"start": 12, "end": 22, "label": "JARGON"},
        {"start": 38, "end": 40, "label": "ABBR"}
        ]
        },
        {
        "text": "Analyze ARPU trends for digital wallets using NFC technology",
        "entities": [
        {"start": 7, "end": 10, "label": "ABBR"},
        {"start": 42, "end": 44, "label": "ABBR"}
        ]
        },
        {
        "text": "Breakdown of CNP fraud incidents vs CP transactions in 2023",
        "entities": [
        {"start": 12, "end": 14, "label": "ABBR"},
        {"start": 34, "end": 36, "label": "ABBR"}
        ]
        },
        {
        "text": "Forecast FX impact on cross-border settlement amounts",
        "entities": [
        {"start": 8, "end": 9, "label": "ABBR"},
        {"start": 24, "end": 37, "label": "JARGON"}
        ]
        },
        {
        "text": "Monthly comparison of ACH returns vs successful EFT payments",
        "entities": [
        {"start": 20, "end": 22, "label": "ABBR"},
        {"start": 44, "end": 46, "label": "ABBR"}
        ]
        },
        {
        "text": "SCA implementation status across European PSPs",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"},
        {"start": 35, "end": 37, "label": "ABBR"}
        ]
        },
        {
        "text": "Correlation between BNPL adoption and increased MDR costs",
        "entities": [
        {"start": 23, "end": 26, "label": "ABBR"},
        {"start": 49, "end": 51, "label": "ABBR"}
        ]
        },
        {
        "text": "Top 5 acquirer processors by PCI DSS compliance score",
        "entities": [
        {"start": 4, "end": 11, "label": "JARGON"},
        {"start": 26, "end": 31, "label": "ABBR"}
        ]
        },
        {
        "text": "Impact of 3DS on reducing ecommerce chargebacks",
        "entities": [
        {"start": 11, "end": 13, "label": "ABBR"},
        {"start": 32, "end": 42, "label": "JARGON"}
        ]
        },
        {
        "text": "KYC completion rates vs account abandonment in C2C apps",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"},
        {"start": 43, "end": 45, "label": "ABBR"}
        ]
        },
        {
        "text": "Interchange fee analysis for different BIN ranges",
        "entities": [
        {"start": 0, "end": 13, "label": "JARGON"},
        {"start": 42, "end": 44, "label": "ABBR"}
        ]
        },
        {
        "text": "Real-time liquidity monitoring through RTP systems",
        "entities": [
        {"start": 32, "end": 34, "label": "ABBR"}
        ]
        },
        {
        "text": "PSD2 compliance costs for AISP and PISP providers",
        "entities": [
        {"start": 0, "end": 3, "label": "ABBR"},
        {"start": 25, "end": 28, "label": "ABBR"},
        {"start": 34, "end": 37, "label": "ABBR"}
        ]
        },
        {
        "text": "QR code payment adoption vs traditional POS terminal usage",
        "entities": [
        {"start": 0, "end": 1, "label": "ABBR"},
        {"start": 42, "end": 44, "label": "ABBR"}
        ]
        },
        {
        "text": "EMV chip penetration rates in high-risk merchant categories",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"}
        ]
        },
        {
        "text": "SWIFT transaction delays impacting correspondent banking",
        "entities": [
        {"start": 0, "end": 4, "label": "ABBR"}
        ]
        },
        {
        "text": "Monthly breakdown of dispute resolution timelines",
        "entities": [
        {"start": 16, "end": 22, "label": "JARGON"}
        ]
        },
        {
        "text": "AVS mismatch rates in card-not-present transactions",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"}
        ]
        },
        {
        "text": "CBDC pilot programs and their impact on payment rails",
        "entities": [
        {"start": 0, "end": 3, "label": "ABBR"},
        {"start": 42, "end": 53, "label": "JARGON"}
        ]
        },
        {
        "text": "White-label solution adoption among payment facilitators",
        "entities": [
        {"start": 0, "end": 9, "label": "JARGON"}
        ]
        },
        {
        "text": "Dynamic currency conversion (DCC) uptake at ATMs",
        "entities": [
        {"start": 24, "end": 26, "label": "ABBR"}
        ]
        },
        {
        "text": "BNPL providers' exposure to consumer credit risk",
        "entities": [
        {"start": 0, "end": 3, "label": "ABBR"}
        ]
        },
        {
        "text": "Tokenization success rates for recurring billing systems",
        "entities": [
        {"start": 0, "end": 12, "label": "JARGON"}
        ]
        },
        {
        "text": "IVR payment completion rates by age demographic",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"}
        ]
        },
        {
        "text": "Same-day ACH volume growth since implementation",
        "entities": [
        {"start": 9, "end": 11, "label": "ABBR"}
        ]
        },
        {
        "text": "Microdeposit verification success rates in OTP flows",
        "entities": [
        {"start": 41, "end": 43, "label": "ABBR"}
        ]
        },
        {
        "text": "Preauthorization hold patterns in hotel POS systems",
        "entities": [
        {"start": 0, "end": 15, "label": "JARGON"},
        {"start": 36, "end": 38, "label": "ABBR"}
        ]
        },
        {
        "text": "Escrow service usage patterns in marketplace P2P transactions",
        "entities": [
        {"start": 0, "end": 5, "label": "JARGON"},
        {"start": 46, "end": 48, "label": "ABBR"}
        ]
        },
        {
        "text": "Payment gateway API uptime vs transaction success rates",
        "entities": [
        {"start": 16, "end": 18, "label": "ABBR"}
        ]
        },
        {
        "text": "MCC-based risk scoring for merchant underwriting",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"}
        ]
        },
        {
        "text": "Offline payment synchronization challenges in mPOS devices",
        "entities": [
        {"start": 0, "end": 14, "label": "JARGON"},
        {"start": 49, "end": 52, "label": "ABBR"}
        ]
        },
        {
        "text": "VAS revenue contribution to overall PSP income",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"},
        {"start": 31, "end": 33, "label": "ABBR"}
        ]
        },
        {
        "text": "NPP instant payment adoption rates in Australia",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"}
        ]
        },
        {
        "text": "Payment orchestration layer impact on conversion rates",
        "entities": [
        {"start": 0, "end": 19, "label": "JARGON"}
        ]
        },
        {
        "text": "SEPA credit transfer volumes vs direct debits",
        "entities": [
        {"start": 0, "end": 3, "label": "ABBR"}
        ]
        },
        {
        "text": "Multilateral interchange fee regulations impact analysis",
        "entities": [
        {"start": 10, "end": 23, "label": "JARGON"}
        ]
        },
        {
        "text": "Payment link conversion rates by industry vertical",
        "entities": [
        {"start": 0, "end": 10, "label": "JARGON"}
        ]
        },
        {
        "text": "ISO merchant onboarding timelines and drop-off rates",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"}
        ]
        },
        {
        "text": "Payment facilitator model vs traditional acquiring",
        "entities": [
        {"start": 0, "end": 17, "label": "JARGON"}
        ]
        },
        {
        "text": "eKYC completion rates for digital wallet signups",
        "entities": [
        {"start": 0, "end": 3, "label": "ABBR"}
        ]
        },
        {
        "text": "Chargeback representment success rates by reason code",
        "entities": [
        {"start": 0, "end": 19, "label": "JARGON"}
        ]
        },
        {
        "text": "RTGS transaction value caps and liquidity management",
        "entities": [
        {"start": 0, "end": 3, "label": "ABBR"}
        ]
        },
        {
        "text": "Subscription billing failure patterns in SaaS vertical",
        "entities": [
        {"start": 0, "end": 18, "label": "JARGON"}
        ]
        },
        {
        "text": "Payment tokenization rates across card networks",
        "entities": [
        {"start": 7, "end": 19, "label": "JARGON"}
        ]
        },
        {
        "text": "Durbin Amendment impact on debit interchange fees",
        "entities": [
        {"start": 29, "end": 42, "label": "JARGON"}
        ]
        },
        {
        "text": "Whitelisted merchant exemption patterns in AML screening",
        "entities": [
        {"start": 0, "end": 10, "label": "JARGON"},
        {"start": 47, "end": 49, "label": "ABBR"}
        ]
        },
        {
        "text": "Cross-border FX spread analysis for remittance corridors",
        "entities": [
        {"start": 13, "end": 14, "label": "ABBR"},
        {"start": 35, "end": 44, "label": "JARGON"}
        ]
        },
        {
        "text": "PayFac vs traditional ISO underwriting models",
        "entities": [
        {"start": 0, "end": 4, "label": "ABBR"},
        {"start": 22, "end": 24, "label": "ABBR"}
        ]
        },
        {
        "text": "SCT Inst adoption timelines across Eurozone countries",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"}
        ]
        },
        {
        "text": "BIN sponsorship trends in fintech partnerships",
        "entities": [
        {"start": 0, "end": 2, "label": "ABBR"}
        ]
        },
        {
        "text": "Payment reconciliation error rates by processor",
        "entities": [
        {"start": 7, "end": 20, "label": "JARGON"}
        ]
        },
        {
        "text": "Omnichannel payment routing optimization strategies",
        "entities": [
        {"start": 0, "end": 18, "label": "JARGON"}
        ]
        },
        {
        "text": "Standing order failure rates in SEPA Direct Debits",
        "entities": [
        {"start": 32, "end": 34, "label": "ABBR"}
        ]
        },
        {
        "text": "Payment gateway uptime SLA compliance metrics",
        "entities": [
        {"start": 15, "end": 17, "label": "ABBR"}
        ]
        },
        {
        "text": "SoftPOS adoption barriers among small merchants",
        "entities": [
        {"start": 0, "end": 4, "label": "ABBR"}
        ]
        },
        {
        "text": "Push-to-card settlement speeds compared to traditional methods",
        "entities": [
        {"start": 0, "end": 11, "label": "JARGON"}
        ]
        },
        {
        "text": "Payment method mix optimization using ML models",
        "entities": [
        {"start": 35, "end": 36, "label": "ABBR"}
        ]
        },
        {
        "text": "Virtual terminal usage patterns in B2B collections",
        "entities": [
        {"start": 0, "end": 15, "label": "JARGON"},
        {"start": 43, "end": 45, "label": "ABBR"}
        ]
        },
        {
        "text": "Payment exception handling costs in omnichannel retail",
        "entities": [
        {"start": 8, "end": 24, "label": "JARGON"}
        ]
        },
        {
        "text": "Interoperability challenges between different FAST systems",
        "entities": [
        {"start": 43, "end": 46, "label": "ABBR"}
        ]
        },
        {
        "text": "Merchant cash advance repayment rates vs traditional loans",
        "entities": [
        {"start": 0, "end": 18, "label": "JARGON"}
        ]
        },
        {
        "text": "Payment hub architecture for multi-rail processing",
        "entities": [
        {"start": 0, "end": 10, "label": "JARGON"}
        ]
        },
        {
        "text": "Card-present vs card-not-present fraud ratios",
        "entities": [
        {"start": 13, "end": 25, "label": "JARGON"}
        ]
        },
        {
        "text": "Payment initiation success rates through PISP integrations",
        "entities": [
        {"start": 40, "end": 43, "label": "ABBR"}
        ]
        },
        {
        "text": "Merchant discount rate competitiveness analysis",
        "entities": [
        {"start": 0, "end": 17, "label": "JARGON"}
        ]
        },
        {
        "text": "Automated clearing house exception handling volumes",
        "entities": [
        {"start": 0, "end": 19, "label": "JARGON"}
        ]
        },
        {
        "text": "Payment status inquiry API call volumes by channel",
        "entities": [
        {"start": 22, "end": 24, "label": "ABBR"}
        ]
        },
        {
        "text": "Dynamic BIN routing optimization for interchange savings",
        "entities": [
        {"start": 7, "end": 9, "label": "ABBR"},
        {"start": 40, "end": 50, "label": "JARGON"}
        ]
        },
        {
        "text": "Merchant category code (MCC) normalization challenges",
        "entities": [
        {"start": 19, "end": 21, "label": "ABBR"}
        ]
        },
        {
        "text": "Payment gateway response code analysis for failed transactions",
        "entities": [
        {"start": 0, "end": 13, "label": "JARGON"}
        ]
        },
        {
        "text": "Real-time payment finality guarantees in different RTGS systems",
        "entities": [
        {"start": 50, "end": 53, "label": "ABBR"}
        ]
        },
        {
        "text": "Payment scheme participation costs for emerging markets",
        "entities": [
        {"start": 0, "end": 13, "label": "JARGON"}
        ]
        },
        {
        "text": "Buy-now-pay-later default rates by credit tier",
        "entities": [
        {"start": 0, "end": 16, "label": "JARGON"}
        ]
        },
        {
        "text": "Merchant onboarding drop-off rates at KYC stage",
        "entities": [
        {"start": 40, "end": 42, "label": "ABBR"}
        ]
        }
]

# Convert to token-level labels with BIO scheme
def convert_to_bio(examples):
    tokenized_inputs = tokenizer(examples["text"], truncation=True, padding=True)
    labels = []
    
    for i, (text, entities) in enumerate(zip(examples["text"], examples["entities"])):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        
        # Initialize all labels as 'O'
        tokens = text.split()
        bio_labels = ['O'] * len(tokens)
        
        # Mark entity spans
        for entity in entities:
            # Find the word indices that contain the entity
            words = text.split()
            start_char = entity["start"]
            end_char = entity["end"]
            
            # Find the word indices that contain the entity
            start_word = 0
            end_word = 0
            current_pos = 0
            
            for idx, word in enumerate(words):
                if current_pos <= start_char < current_pos + len(word):
                    start_word = idx
                if current_pos < end_char <= current_pos + len(word):
                    end_word = idx
                current_pos += len(word) + 1  # +1 for the space
            
            bio_labels[start_word] = f"B-{entity['label']}"
            for idx in range(start_word + 1, end_word + 1):
                bio_labels[idx] = f"I-{entity['label']}"
        
        # Align labels with tokenizer output
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                if word_idx < len(bio_labels):  # Add safety check
                    label_ids.append(label2id[bio_labels[word_idx]])
                else:
                    label_ids.append(label2id['O'])  # Default to 'O' for out-of-range indices
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx
        
        labels.append(label_ids)
    
    tokenized_inputs["labels"] = labels
    return tokenized_inputs

# Prepare dataset
dataset = Dataset.from_dict({
    "text": [ex["text"] for ex in train_examples],
    "entities": [ex["entities"] for ex in train_examples]
})

tokenized_dataset = dataset.map(
    convert_to_bio,
    batched=True,
    remove_columns=dataset.column_names
)

# Training configuration
training_args = TrainingArguments(
    output_dir="~/models/glossary-detector",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    num_train_epochs=10,
    weight_decay=0.01,
    evaluation_strategy="no",
    save_strategy="epoch",
    logging_steps=10,
    push_to_hub=False,
)

# Metrics evaluation
seqeval = evaluate.load("seqeval")

def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    true_predictions = [
        [id2label[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [id2label[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    results = seqeval.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    compute_metrics=compute_metrics,
)

# Start training
trainer.train()

# Save the trained model and tokenizer
output_dir = training_args.output_dir  # Use the output directory from TrainingArguments
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)

# Later, load the model and tokenizer
model = AutoModelForTokenClassification.from_pretrained(output_dir)
tokenizer = AutoTokenizer.from_pretrained(output_dir)

# Inference function
def detect_entities(text, model, tokenizer):
    with torch.no_grad():  # Disable gradient calculation
        # Get word IDs from tokenizer
        encoding = tokenizer(text.split(), is_split_into_words=True, return_tensors="pt")
        word_ids = encoding.word_ids()
        
        # Move inputs to CPU
        inputs = {k: v.to(device) for k, v in encoding.items()}
        
        # Ensure model is on CPU
        model = model.to(device)
        
        outputs = model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=-1)[0].tolist()
        
        current_entity = []
        entities = []
        for idx, (word_id, pred_id) in enumerate(zip(word_ids, predictions)):
            label = id2label[pred_id]
            
            if word_id is None:
                continue
                
            if label.startswith("B-"):
                if current_entity:
                    entities.append(current_entity)
                current_entity = {
                    "start": word_id,
                    "end": word_id,
                    "label": label[2:],
                    "text": text.split()[word_id]
                }
            elif label.startswith("I-") and current_entity:
                if current_entity["label"] == label[2:]:
                    current_entity["end"] = word_id
                    current_entity["text"] += " " + text.split()[word_id]
            else:
                if current_entity:
                    entities.append(current_entity)
                    current_entity = []
        
        if current_entity:  # Don't forget to add the last entity if exists
            entities.append(current_entity)
        
        return entities

# Example usage
#test_text = "Verify the HTTP QPS and DB RPS metrics on Kubernetes pods"
test_text = "Show me top 3 market by TPV in 2024 and its monthly ASP trend"
results = detect_entities(test_text, model, tokenizer)
print("Detected entities:")
print(results)
for ent in results:
    print(f"- {ent['text']} ({ent['label']})")