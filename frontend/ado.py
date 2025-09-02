import os
import json
import streamlit as st

def load_stories_from_json(usecase_path):
    """Load stories from JSON files"""
    stories_data = {}
    
    # Read FR stories from JSON
    fr_json = os.path.join(usecase_path, "ra-fr.json")
    if os.path.exists(fr_json):
        try:
            with open(fr_json, 'r') as f:
                fr_data = json.load(f)
                if 'userStories' in fr_data:
                    for idx, story in enumerate(fr_data['userStories'], 1):
                        story_id = story.get('id', '')
                        stories_data[story_id] = {
                            'title': story.get('title', ''),
                            'as_a': story.get('asA', ''),
                            'i_want': story.get('iWantTo', ''),
                            'so_that': story.get('soThat', ''),
                            'points': story.get('storyPoints', 1),
                            'priority': story.get('priority', 'Medium'),
                            'tags': ", ".join(story.get('tags', [])),
                            'ac_list': story.get('acceptanceCriteria', [])
                        }
        except Exception as e:
            st.error(f"Error reading FR JSON: {str(e)}")
    
    return stories_data