"""Multiplicative cooldown modifiers from upgrades and operation effects."""

from dataclasses import dataclass


CALL_IN_TIME = 10


@dataclass(frozen=True)
class CooldownModifier:
    key: str
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
        "orbital_fluctuations",
        -25, all_stratagems=True, default_enabled=False,
    ),
    CooldownModifier(
        "streamlined_request_process",
        10, subcategories=("Support Weapons",),
    ),
    CooldownModifier(
        "hand_carts",
        10,
        subcategories=("Backpacks",),
    ),
    CooldownModifier(
        "zero_g_breech_loading",
        10, subcategories=("Orbital Strikes",),
    ),
    CooldownModifier(
        "liquid_ventilated_cockpit",
        50,
        subcategories=("Eagle Strikes",),
    ),
    CooldownModifier(
        "morale_augmentation",
        5, all_stratagems=True,
    ),
    CooldownModifier(
        "synthetic_supplementation",
        10,
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
