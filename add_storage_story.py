import json

# Read the current stories file
with open('.agents/artifacts/stage-4/stories.json', 'r') as f:
    data = json.load(f)

# Add new epic for database storage
new_epic = {
    "id": "EPIC-6",
    "name": "Database Storage and Record Management",
    "description": "System-level capability to persist prescription records with referential integrity and governance",
    "stories": ["STORY-6-1"],
    "priority": "P0",
    "user_persona": "System"
}
data['epics'].append(new_epic)

# Add new story for FR-4
new_story = {
    "id": "STORY-6-1",
    "epic": "EPIC-6",
    "title": "Store captured prescription records in governed database",
    "description": "System must write all extracted prescription records to designated database schema with referential integrity and governance controls.",
    "user_persona": "System",
    "links_to": {
        "fr": ["FR-4"],
        "nfr": [],
        "con": [],
        "goal": ["GOAL-2"],
        "flow": []
    },
    "components": [
        "PrescriptionRepository"
    ],
    "acceptance_criteria": [
        "System writes all extracted prescription records to designated database schema",
        "Database write operations enforce referential integrity and data type constraints",
        "Storage location is controlled under organization's data governance standards",
        "Records remain accessible for queries by Operations and Compliance systems"
    ],
    "depends_on": [],
    "delivery_order": 0
}
data['stories'].append(new_story)

# Update all delivery_order values to account for new story
for i, story in enumerate(data['stories']):
    if 'delivery_order' not in story or story['delivery_order'] == 0:
        story['delivery_order'] = i + 1

# Write back the corrected file
with open('.agents/artifacts/stage-4/stories.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Added EPIC-6 and STORY-6-1 for FR-4 (database storage)")
