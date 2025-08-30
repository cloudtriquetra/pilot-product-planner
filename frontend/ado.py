import re


def parse_story(story_text, story_type="FR"):
    # Define patterns based on story type
    if story_type == "FR":
        story_pattern = re.compile(
            r'As a (.*?), I want to (.*?), so that (.*?)\.'  # Story narrative
            r'\s*- Story Points: (\d+)\s*'                    # Story points
            r'- Priority: (.*?)\s*'                           # Priority
            r'- Tags: (.*?)$',                               # Tags
            re.DOTALL
        )
    else:  # QUS/NFR pattern
        story_pattern = re.compile(
            r'As a (.*?), I need (.*?), so that (.*?)\.'     # NFR narrative
            r'\s*- Story Points: (\d+)\s*'                    # Story points
            r'- Priority: (.*?)\s*'                           # Priority
            r'- Tags: (.*?)$',                               # Tags
            re.DOTALL
        )

    match = story_pattern.search(story_text)
    if match:
        return {
            'as_a': match.group(1).strip(),
            'i_want': match.group(2).strip(),
            'so_that': match.group(3).strip(),
            'points': match.group(4).strip(),
            'priority': match.group(5).strip(),
            'tags': match.group(6).strip()
        }
    return None

def generate_ado_story(title, as_a, i_want, so_that, points, priority, tags, ac_list):
    return (
        f"# {title}\n\n"
        f"## Description\n"
        f"As a {as_a}\n"
        f"I want to {i_want}\n"
        f"So that {so_that}\n\n"
        f"## Acceptance Criteria\n"
        + "".join(f"- [ ] {ac}\n" for ac in ac_list) +
        f"\n## Details\n"
        f"- Story Points: {points}\n"
        f"- Priority: {priority}\n"
        f"- Tags: {tags}"
    )
