import json

# Read the current stories file
with open('.agents/artifacts/stage-4/stories.json', 'r') as f:
    data = json.load(f)

# Fix the links_to structure for each story
for story in data.get('stories', []):
    old_links = story.get('links_to', {})
    if isinstance(old_links, dict) and 'requirements' in old_links:
        # Convert nested structure to proper object format
        new_links = {
            "fr": [],
            "nfr": [],
            "con": [],
            "goal": [],
            "flow": []
        }
        
        # Extract FRs and NFRs from requirements
        for req in old_links.get('requirements', []):
            if req.startswith('FR-'):
                new_links['fr'].append(req)
            elif req.startswith('NFR-'):
                new_links['nfr'].append(req)
            elif req.startswith('CON-'):
                new_links['con'].append(req)
        
        # Extract GOALs
        for goal in old_links.get('goals', []):
            new_links['goal'].append(goal)
        
        # Extract FLOWs
        for flow in old_links.get('flows', []):
            new_links['flow'].append(flow)
        
        story['links_to'] = new_links

# Write back the corrected file
with open('.agents/artifacts/stage-4/stories.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Fixed stories.json links_to structure to proper object format")
