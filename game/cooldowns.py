"""Multiplicative cooldown modifiers from upgrades and operation effects."""

from dataclasses import dataclass


CALL_IN_TIME = 10


@dataclass(frozen=True)
class CooldownModifier:
    key: str
    name: str
    description: str
    percent: int  # Positive reduces cooldown; negative increases it.
    subcategories: tuple = ()
    names: tuple = ()
    all_stratagems: bool = False
    default_enabled: bool = True

    def applies_to(self, stratagem):
        return (
            self.all_stratagems
            or stratagem.subcategory in self.subcategories
            or stratagem.name in self.names
        )


COOLDOWN_UPGRADES = (
    CooldownModifier(
        "orbital_fluctuations", "Orbital Fluctuations",
        "軌道震盪：全戰備冷卻 +25%", -25, all_stratagems=True, default_enabled=False,
    ),
    CooldownModifier(
        "streamlined_request_process", "Streamlined Request Process",
        "升級：支援武器冷卻 -10%", 10, subcategories=("Support Weapons",),
    ),
    CooldownModifier(
        "hand_carts", "Hand Carts",
        "升級：背包冷卻 -10%", 10,
        subcategories=("Backpacks",),
    ),
    CooldownModifier(
        "zero_g_breech_loading", "Zero-G Breech Loading",
        "升級：軌道冷卻 -10%", 10, subcategories=("Orbital Strikes",),
    ),
    CooldownModifier(
        "liquid_ventilated_cockpit", "Liquid-Ventilated Cockpit",
        "升級：飛鷹冷卻 -50%", 50,
        subcategories=("Eagle Strikes",),
    ),
    CooldownModifier(
        "morale_augmentation", "Morale Augmentation",
        "升級：全戰備冷卻 -5%", 5, all_stratagems=True,
    ),
    CooldownModifier(
        "synthetic_supplementation", "Synthetic Supplementation",
        "升級：砲塔、陣地與補給冷卻 -10%", 10,
        subcategories=("Sentries", "Emplacements"), names=("Resupply",),
    ),
)


def calculate_cooldown(stratagem, enabled_upgrades):
    cooldown = stratagem.cooldown
    for modifier in COOLDOWN_UPGRADES:
        if modifier.key in enabled_upgrades and modifier.applies_to(stratagem):
            cooldown *= (100 - modifier.percent) / 100
            cooldown = round(cooldown)
    return cooldown + CALL_IN_TIME
