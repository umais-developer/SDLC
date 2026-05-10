import json

# Read the current stories file
with open('.agents/artifacts/stage-4/stories.json', 'r') as f:
    data = json.load(f)

# Remove EPIC-6 (database storage)
data['epics'] = [e for e in data['epics'] if e['id'] != 'EPIC-6']

# Remove STORY-6-1
data['stories'] = [s for s in data['stories'] if s['id'] != 'STORY-6-1']

# Write back the corrected file
with open('.agents/artifacts/stage-4/stories.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Removed EPIC-6 and STORY-6-1 (FR-4 is non-user-facing, covered by components)")
