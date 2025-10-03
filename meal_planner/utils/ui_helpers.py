"""
UI Helpers - Utilitaires pour l'interface utilisateur PyQt6
"""

from pathlib import Path
from PyQt6.QtWidgets import QLabel, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from meal_planner.config import BASE_DIR

# Chemin vers les icônes
ICONS_DIR = BASE_DIR / "meal_planner" / "data" / "icons"


def load_icon(icon_name: str) -> QPixmap:
    """
    Charge une icône depuis le répertoire des icônes.

    Args:
        icon_name: Nom de l'icône (sans extension)

    Returns:
        QPixmap de l'icône ou QPixmap vide si non trouvée
    """
    icon_path = ICONS_DIR / f"{icon_name}.png"
    if icon_path.exists():
        return QPixmap(str(icon_path))
    return QPixmap()


def create_icon_label(icon_name: str, size: int = 20) -> QLabel:
    """
    Crée un QLabel contenant une icône redimensionnée.

    Args:
        icon_name: Nom de l'icône (sans extension)
        size: Taille en pixels (carré)

    Returns:
        QLabel avec l'icône
    """
    label = QLabel()
    pixmap = load_icon(icon_name)
    if not pixmap.isNull():
        label.setPixmap(pixmap.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
    return label


def create_shadow_effect(blur_radius: int = 10, opacity: float = 0.2) -> QGraphicsDropShadowEffect:
    """
    Crée un effet d'ombre portée Material Design.

    Args:
        blur_radius: Rayon de flou de l'ombre
        opacity: Opacité de l'ombre (0.0 à 1.0)

    Returns:
        QGraphicsDropShadowEffect configuré
    """
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(QColor(0, 0, 0, int(255 * opacity)))
    shadow.setOffset(0, blur_radius // 4)
    return shadow
