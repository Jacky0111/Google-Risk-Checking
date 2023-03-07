import spacy

# Load the small English model
nlp = spacy.load('en_core_web_sm')

# Define a sentence to analyze
sentence = '''Money laundering is a process of converting cash, funds or property derived from criminal activities to give it a legitimate appearance. It is a process to clean ‘dirty’ money in order to disguise its criminal origin.

'''
# Process the sentence with spaCy
doc = nlp(sentence)

# Iterate over the entities in the sentence and check if any of them are a person
for entity in doc.ents:
    if entity.label_ == 'PERSON':
        print(entity)