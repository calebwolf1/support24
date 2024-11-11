from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load pre-trained RoBERTa model and tokenizer
# model_name = "roberta-base-mnli"  # RoBERTa fine-tuned on MNLI
model_name = "textattack/roberta-base-MNLI"  # Alternative smaller faster model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Precision-oriented threshold for entailment
ENTAILMENT_THRESHOLD = 0.8
CONTRADICTION_THRESHOLD = 0.3

def check_claim_with_nli(claim, paragraphs):
    """    
    Parameters:
        claim (str): The claim to validate.
        paragraphs (list of str): List of paragraphs (evidence) from different sources.
        
    Returns:
        results (list of dict): List of dictionaries with the paragraph and its classification result.
    """
    results = []
    
    for paragraph in paragraphs:
        # Encode the claim and paragraph as a pair
        inputs = tokenizer(claim, paragraph, return_tensors="pt", truncation=True, padding=True)
        
        # Get model predictions
        with torch.no_grad():
            outputs = model(**inputs) # Forward pass
            logits = outputs.logits 
            probabilities = torch.softmax(logits, dim=1)[0]  # index 0 for first item in batch size of 1
            
        # Extract probabilities for entailment, contradiction, and neutral
        entailment_prob = probabilities[2].item()
        contradiction_prob = probabilities[0].item()
        neutral_prob = probabilities[1].item()
        
        # Classify based on threshold
        if entailment_prob >= ENTAILMENT_THRESHOLD:
            result = "entails"  # Supports the claim
        elif contradiction_prob >= CONTRADICTION_THRESHOLD:
            result = "contradicts"  # Refutes the claim
        else:
            result = "neutral"  # No clear support or refutation
        
        # Append result with probability information
        results.append({
            "paragraph": paragraph,
            "entailment_prob": entailment_prob,
            "contradiction_prob": contradiction_prob,
            "neutral_prob": neutral_prob,
            "result": result
        })
    
    return results

# Example usage
claim = "Climate change is contributing to more extreme weather patterns."
paragraphs = "As global temperatures rise, scientists have observed an increase in the frequency and intensity of extreme weather events like hurricanes, heatwaves, and flooding, which are linked to the ongoing effects of climate change."

results = check_claim_with_nli(claim, paragraphs)
for idx, res in enumerate(results):
    print(f"Source {idx+1}:")
    # print(f"Paragraph: {res['paragraph']}")
    print(f"Entailment Probability: {res['entailment_prob']:.2f}")
    print(f"Contradiction Probability: {res['contradiction_prob']:.2f}")
    print(f"Neutral Probability: {res['neutral_prob']:.2f}")
    print(f"Result: {res['result']}")
    print("----")
