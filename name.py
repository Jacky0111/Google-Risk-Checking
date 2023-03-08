import spacy
import itertools

# Load the small English model
from fuzzywuzzy import fuzz

nlp = spacy.load('en_core_web_sm')

# Define a sentence to analyze
sentence = '''
CC and Chung Chia money laundering is a process of converting cash, funds or property derived from criminal activities to give it a legitimate appearance. It is a process to clean ‘dirty’ money in order to disguise its criminal origin.
'''

person_name_tokens = 'Chia Chung'.split()

# Find all permutations of the person name
person_name_permutations = [
    " ".join(permutation)
    for r in range(1, len(person_name_tokens) + 1)
    for permutation in itertools.permutations(person_name_tokens, r)
]
print(person_name_permutations)

# Process the sentence with spaCy
doc = nlp(sentence)

# Iterate over the entities in the sentence and check if any of them are a person
for entity in doc.ents:
    if entity.label_ == 'PERSON':
        print(entity)
        # Iterate over the words and phrases in the document
        for i, token in enumerate(entity):
            print(f'token: {token}')
            # Check if the token matches the first token of any permutation of the person name
            for permutation in person_name_permutations:
                print(f'permutation: {permutation}')
                # Check if the remaining tokens match the subsequent tokens of the permutation
                j = 0
                while i + j < len(doc) and j < len(permutation.split()):
                    distance = fuzz.ratio(doc[i + j].text.lower(), permutation.split()[j].lower())
                    if distance < 65:
                        break
                    j += 1
                # If all tokens match, print the match and break the loop to avoid duplicate matches
                if j == len(permutation.split()):
                    print(i, token, permutation, 'match')
