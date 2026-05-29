"""Shared data for the Assets tab"""

SHOT_HEADERS = ["Shot", "Department", "Status", "Due Date"]

DEPARTMENT_TREE = {
    "Rig": {
        "Lead":  ["Senior Rigger", "Junior Rigger"],
        "Tools": ["Pipeline TD", "Tech Animator"],
    },
    "FX": {
        "Simulation": ["Houdini Artist", "FX TD"],
        "Rendering":  ["Lighting TD", "Comp Artist"],
    },
    "Animation": {
        "Character": ["Lead Animator", "Animator"],
        "Crowd":     ["Crowd TD", "Animator"],
    },
    "Assets": {
        "Modeling":  ["Lead Modeler", "Modeler"],
        "Texturing": ["Lead Texture", "Texture Artist"],
    },
}
