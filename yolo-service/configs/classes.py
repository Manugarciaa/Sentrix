"""
Dengue breeding site detection classes configuration
"""

# Class mapping for dengue breeding sites
DENGUE_CLASSES = {
    0: "huecos",
    1: "charcos_cumulos_agua",
    2: "calles_rotas_mal_hechas",
    3: "basura_basurales"
}

# Reverse mapping for LabelStudio conversion
CLASS_NAME_TO_ID = {name: idx for idx, name in DENGUE_CLASSES.items()}

# Risk levels
HIGH_RISK_CLASSES = ["huecos", "charcos_cumulos_agua", "calles_rotas_mal_hechas"]
MEDIUM_RISK_CLASSES = ["basura_basurales"]