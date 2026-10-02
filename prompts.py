"""
Prompts and Narration scripts for 'AI-Generated Journey of a Student'.
Contains exactly 5 scenes representing the student's progression from college entrance to a career.
"""

# Exactly 5 image generation prompts as specified in the assignment
IMAGE_PROMPTS = [
    # Scene 1: College entrance
    (
        "A young college student arriving at a modern engineering college campus "
        "on the first day, carrying a backpack, excited and hopeful, realistic photography style, "
        "professional academic environment, cinematic composition, 16:9"
    ),
    # Scene 2: Classroom
    (
        "The same young engineering student attending a modern computer science class, "
        "sitting in front of a computer with other students, learning programming, "
        "realistic photography style, professional academic environment, cinematic composition, 16:9"
    ),
    # Scene 3: Coding project
    (
        "The same young engineering student working on an innovative software project "
        "using a laptop, writing code in a modern computer laboratory, focused and motivated, "
        "realistic photography style, cinematic composition, 16:9"
    ),
    # Scene 4: Placement preparation
    (
        "The same young engineering student preparing for a technical job interview, "
        "sitting at a desk with a laptop and interview notes, practicing confidently, "
        "modern professional environment, realistic photography style, cinematic composition, 16:9"
    ),
    # Scene 5: Career
    (
        "The same young engineering student beginning a successful career as a software engineer "
        "in a modern technology company, professional workplace, confident and happy, "
        "hopeful career beginning, realistic photography style, cinematic composition, 16:9"
    )
]

# Scene titles for display and reporting
SCENE_TITLES = [
    "Scene 1: College Entrance",
    "Scene 2: Technology Classroom",
    "Scene 3: Hands-on Software Project",
    "Scene 4: Placement & Interview Prep",
    "Scene 5: Professional Career Beginning"
]

# Corresponding narration lines for each scene
NARRATION_SCRIPTS = [
    "Every journey begins with a first step. For a student, entering college marks the beginning of a new chapter.",
    "Through classrooms and practical learning, the student begins developing the technical knowledge needed for the future.",
    "By working on software projects, ideas become real solutions, and confidence grows through hands-on experience.",
    "With graduation approaching, the student prepares for technical interviews and the challenges of entering the professional world.",
    "After years of learning and preparation, the journey reaches a new beginning: a career in the technology industry."
]


def get_full_narration_text() -> str:
    """
    Returns the complete narration script formatted with natural pauses.
    """
    return "  ".join(NARRATION_SCRIPTS)


def get_scene_data():
    """
    Returns a list of dictionaries with full metadata for each of the 5 scenes.
    """
    scenes = []
    for idx, (title, prompt, narration) in enumerate(zip(SCENE_TITLES, IMAGE_PROMPTS, NARRATION_SCRIPTS), start=1):
        scenes.append({
            "index": idx,
            "title": title,
            "filename": f"scene_{idx:02d}.png",
            "prompt": prompt,
            "narration": narration
        })
    return scenes
