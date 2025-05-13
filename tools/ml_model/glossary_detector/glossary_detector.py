import torch
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification
)

class Glossary_detector:
    """Detect abbreviations, terminologies, jargons in a user question which is used to query business metrics."""
    def __init__(self):
        self.name = "glossary detector"
        self.description = "Detect abbreviations, terminologies, jargons in a user question which is used to query business metrics."

        # Disable MPS and force CPU usage
        torch.backends.mps.enabled = False
        torch.set_default_tensor_type(torch.FloatTensor)
        self.device = torch.device("cpu")

        # Label configuration
        labels = ["O", "B-ABBR", "I-ABBR", "B-JARGON", "I-JARGON", "B-TERM", "I-TERM"]
        self.id2label = {i: label for i, label in enumerate(labels)}


        # Later, load the model and tokenizer
        output_dir = "/Users/xiaotaoyi/models/glossary-detector"
        self.model = AutoModelForTokenClassification.from_pretrained(output_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(output_dir)


    def run(self, text):
        with torch.no_grad():  # Disable gradient calculation
            # Get word IDs from tokenizer
            encoding = self.tokenizer(text.split(), is_split_into_words=True, return_tensors="pt")
            word_ids = encoding.word_ids()
            
            # Move inputs to CPU
            inputs = {k: v.to(self.device) for k, v in encoding.items()}
            
            # Ensure model is on CPU
            model = self.model.to(self.device)
            
            outputs = model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)[0].tolist()
            
            current_entity = []
            entities = []
            for idx, (word_id, pred_id) in enumerate(zip(word_ids, predictions)):
                label = self.id2label[pred_id]
                
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

'''
test_text = "Show me top 3 market by tpv in 2024 and its monthly ASP trend"
results = glossary_detector().run(test_text)
print("Detected entities:")
print(results)
for ent in results:
    print(f"- {ent['text']} ({ent['label']})")

test_text = "Show me tpv at the year 2024 by month"
results = glossary_detector().run(test_text)
print("Detected entities:")
print(results)
for ent in results:
    print(f"- {ent['text']} ({ent['label']})")
'''