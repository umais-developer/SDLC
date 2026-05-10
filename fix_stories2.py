import json

# Read the current stories file
with open('.agents/artifacts/stage-4/stories.json', 'r') as f:
    data = json.load(f)

# Fix the links_to structure for each story
for story in data.get('stories', []):
    links = story.get('links_to', [])
    
    # Create new object format
    new_links = {
        "fr": [],
        "nfr": [],
        "con": [],
        "goal": [],
        "flow": []
    }
    
    # If it's already a flat list, categorize each item
    if isinstance(links, list):
        for item in links:
            if item.startswith('FR-'):
                new_links['fr'].append(item)
            elif item.startswith('NFR-'):
                new_links['nfr'].append(item)
            elif item.startswith('CON-'):
                new_links['con'].append(item)
            elif item.startswith('GOAL-'):
                new_links['goal'].append(item)
            elif item.startswith('FLOW-'):
                new_links['flow'].append(item)
    
    story['links_to'] = new_links

# Write back the corrected file
with open('.agents/artifacts/stage-4/stories.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Fixed stories.json links_to to object format")
