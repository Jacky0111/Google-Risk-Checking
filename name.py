import spacy
from fuzzywuzzy import fuzz
import itertools

nlp = spacy.load('en_core_web_sm')

essay = "Jn Smth was born in New York City. He studied at Harvard University and later became a successful businessman."

# Set the person name you want to detect as a keyword
person_name = "John Smith"

# Process the essay text using spaCy
doc = nlp(essay)

# Split the person name into individual tokens
person_name_tokens = person_name.split()

# Find all permutations of the person name
person_name_permutations = [
    " ".join(permutation)
    for r in range(1, len(person_name_tokens) + 1)
    for permutation in itertools.permutations(person_name_tokens, r)
]

print(person_name_permutations)

# Iterate over the words and phrases in the document
for i, token in enumerate(doc):
    # Check if the token matches the first token of any permutation of the person name
    for permutation in person_name_permutations:
        # Check if the remaining tokens match the subsequent tokens of the permutation
        j = 0
        while i + j < len(doc) and j < len(permutation.split()):
            distance = fuzz.ratio(doc[i + j].text.lower(), permutation.split()[j].lower())
            if distance < 65:
                break
            j += 1
        # If all tokens match, print the match and break the loop to avoid duplicate matches
        if j == len(permutation.split()):
            print(f"Detected person name: {permutation}")
            print("Matched tokens:")
            for k in range(i, i + len(permutation.split())):
                print(doc[k].text)
            print("\n")
            break
