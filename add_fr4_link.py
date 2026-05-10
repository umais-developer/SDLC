import json

# Read the current stories file
with open('.agents/artifacts/stage-4/stories.json', 'r') as f:
    data = json.load(f)

# Find STORY-4-1 and add FR-4 to its links
for story in data['stories']:
    if story['id'] == 'STORY-4-1':
        # Add FR-4 to the requirements (database storage is part of tracking state)
        if 'FR-4' not in story['links_to']['fr']:
            story['links_to']['fr'].insert(0, 'FR-4')

# Write back the corrected file
with open('.agents/artifacts/stage-4/stories.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Added FR-4 to STORY-4-1 (database storage linked with persistence)")
