# Placeholder for entity matching logic
def resolve_entities(entities):
    resolved = {}
    for e in entities:
        resolved[e['name'].lower()] = e
    return resolved
