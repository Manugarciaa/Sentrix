DENGUE_CLASSES = {
    0: "Basura",
    1: "Calles mal hechas",
    2: "Charcos/Cumulo de agua",
    3: "Huecos"
}

HIGH_RISK_CLASSES = [
    "Calles mal hechas",
    "Charcos/Cumulo de agua", 
    "Huecos"
]

MEDIUM_RISK_CLASSES = [
    "Basura"
]

CLASS_TO_ID = {v: k for k, v in DENGUE_CLASSES.items()}

RISK_LEVEL_BY_ID = {}
for class_id, class_name in DENGUE_CLASSES.items():
    if class_name in HIGH_RISK_CLASSES:
        RISK_LEVEL_BY_ID[class_id] = "ALTO"
    elif class_name in MEDIUM_RISK_CLASSES:
        RISK_LEVEL_BY_ID[class_id] = "MEDIO"
    else:
        RISK_LEVEL_BY_ID[class_id] = "BAJO"

NUM_CLASSES = len(DENGUE_CLASSES)