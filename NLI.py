from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load pre-trained RoBERTa model and tokenizer
model_name = "textattack/roberta-base-MNLI"  # Smaller, faster model fine-tuned on MNLI
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Thresholds for entailment and contradiction - normally just take the softmax output
ENTAILMENT_THRESHOLD = 0.8
CONTRADICTION_THRESHOLD = 0.3

def check_claim_with_nli(claim, paragraphs):
    """
    Parameters:
        claim (str): The claim to validate.
        paragraphs (list of str): List of paragraphs (evidence) from different sources.
    
    Logic:
        entailment is usually done by checking if a sentence supports a claim or not, not by checking if a paragraph of sentences supports a claim.
        here we're using the majority of the sentences in the paragraph to determine the label of the paragraph. the paragraph is only neutral
        when all the sentences in the paragraph are neutral.        

    Returns:
        majority_label (str): The label (entails, contradicts, or neutral) with the most supporting paragraphs,
                              or "neutral" if there are no supporting or contradicting paragraphs.
    """
    entail_count = 0
    contradict_count = 0
    neutral_count = 0

    for paragraph in paragraphs:
        # Encode the claim and paragraph as a pair
        inputs = tokenizer(claim, paragraph, return_tensors="pt", truncation=True, padding=True)
        
        # Get model predictions
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits 
            probabilities = torch.softmax(logits, dim=1)[0]
        
        # Extract probabilities for each class
        entailment_prob = probabilities[2].item()
        contradiction_prob = probabilities[0].item()
        # neutral_prob = probabilities[1].item()
        
        # Classify based on thresholds and update counts
        if entailment_prob >= ENTAILMENT_THRESHOLD:
            entail_count += 1
        elif contradiction_prob >= CONTRADICTION_THRESHOLD:
            contradict_count += 1
        else:
            neutral_count += 1

    # Determine the majority label
    if entail_count > contradict_count:
        majority_label = "entails"
    elif contradict_count > entail_count:
        majority_label = "contradicts"
    else:
        majority_label = "neutral"  # Only if all are neutral or if neutral has the most count

    return majority_label

# Example usage
claim = "Electric cars are more environmentally friendly than gasoline cars."
paragraphs = [
    "Electric cars produce no tailpipe emissions, making them cleaner in terms of air quality.",
    "The production of electric vehicle batteries has a high environmental impact, especially due to mining.",
    "Studies show that electric cars, when charged from renewable sources, have a significantly lower carbon footprint."
]

majority_result = check_claim_with_nli(claim, paragraphs)
print(f"Majority classification result: {majority_result}")
