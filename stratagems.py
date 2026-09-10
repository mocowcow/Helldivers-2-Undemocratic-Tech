
class Stratagem:
    def __init__(self, name, name_cn, sequence):
        self.name = name
        self.name_cn = name_cn
        self.sequence = sequence


# Source: https://helldivers.wiki.gg/wiki/Stratagems
# Retrieved 2026-09-10; entries follow the source HTML table order.
# Arrow image alt text is converted to up/down/left/right.
STRATAGEMS = {
    # Offensive Permit
    # Orbital Strikes
    "Orbital Precision Strike": Stratagem(
        name="Orbital Precision Strike", name_cn="",
        sequence=["right", "right", "up"],
    ),
    "Orbital Gatling Barrage": Stratagem(
        name="Orbital Gatling Barrage", name_cn="",
        sequence=["right", "down", "left", "up", "up"],
    ),
    "Orbital Gas Strike": Stratagem(
        name="Orbital Gas Strike", name_cn="",
        sequence=["right", "right", "down", "right"],
    ),
    "Orbital 120mm HE Barrage": Stratagem(
        name="Orbital 120mm HE Barrage", name_cn="",
        sequence=["right", "right", "down", "left", "right", "down"],
    ),
    "Orbital Airburst Strike": Stratagem(
        name="Orbital Airburst Strike", name_cn="",
        sequence=["right", "right", "right"],
    ),
    "Orbital Smoke Strike": Stratagem(
        name="Orbital Smoke Strike", name_cn="",
        sequence=["right", "right", "down", "up"],
    ),
    "Orbital EMS Strike": Stratagem(
        name="Orbital EMS Strike", name_cn="",
        sequence=["right", "right", "left", "down"],
    ),
    "Orbital 380mm HE Barrage": Stratagem(
        name="Orbital 380mm HE Barrage", name_cn="",
        sequence=["right", "down", "up", "up", "left", "down", "down"],
    ),
    "Orbital Walking Barrage": Stratagem(
        name="Orbital Walking Barrage", name_cn="",
        sequence=["right", "down", "right", "down", "right", "down"],
    ),
    "Orbital Laser": Stratagem(
        name="Orbital Laser", name_cn="",
        sequence=["right", "down", "up", "right", "down"],
    ),
    "Orbital Napalm Barrage": Stratagem(
        name="Orbital Napalm Barrage", name_cn="",
        sequence=["right", "right", "down", "left", "right", "up"],
    ),
    "Orbital Railcannon Strike": Stratagem(
        name="Orbital Railcannon Strike", name_cn="",
        sequence=["right", "up", "down", "down", "right"],
    ),

    # Eagle Strikes
    "Eagle Gas Airstrike": Stratagem(
        name="Eagle Gas Airstrike", name_cn="",
        sequence=["up", "right", "left", "right"],
    ),
    "Eagle Strafing Run": Stratagem(
        name="Eagle Strafing Run", name_cn="",
        sequence=["up", "right", "right"],
    ),
    "Eagle Airstrike": Stratagem(
        name="Eagle Airstrike", name_cn="",
        sequence=["up", "right", "down", "right"],
    ),
    "Eagle Cluster Bomb": Stratagem(
        name="Eagle Cluster Bomb", name_cn="",
        sequence=["up", "right", "down", "down", "right"],
    ),
    "Eagle Smoke Strike": Stratagem(
        name="Eagle Smoke Strike", name_cn="",
        sequence=["up", "right", "up", "down"],
    ),
    "Eagle Napalm Airstrike": Stratagem(
        name="Eagle Napalm Airstrike", name_cn="",
        sequence=["up", "right", "down", "up"],
    ),
    "Eagle 110mm Rocket Pods": Stratagem(
        name="Eagle 110mm Rocket Pods", name_cn="",
        sequence=["up", "right", "up", "left"],
    ),
    "Eagle 500kg Bomb": Stratagem(
        name="Eagle 500kg Bomb", name_cn="",
        sequence=["up", "right", "down", "down", "down"],
    ),

    # Supply Permit
    # Support Weapons
    "MG-43 Machine Gun": Stratagem(
        name="MG-43 Machine Gun", name_cn="",
        sequence=["down", "left", "down", "up", "right"],
    ),
    "EAT-17 Expendable Anti-Tank": Stratagem(
        name="EAT-17 Expendable Anti-Tank", name_cn="",
        sequence=["down", "down", "left", "up", "right"],
    ),
    "M-105 Stalwart": Stratagem(
        name="M-105 Stalwart", name_cn="",
        sequence=["down", "left", "down", "up", "up", "left"],
    ),
    "LAS-98 Laser Cannon": Stratagem(
        name="LAS-98 Laser Cannon", name_cn="",
        sequence=["down", "left", "down", "up", "left"],
    ),
    "APW-1 Anti-Materiel Rifle": Stratagem(
        name="APW-1 Anti-Materiel Rifle", name_cn="",
        sequence=["down", "left", "right", "up", "down"],
    ),
    "GR-8 Recoilless Rifle": Stratagem(
        name="GR-8 Recoilless Rifle", name_cn="",
        sequence=["down", "left", "right", "right", "left"],
    ),
    "GL-21 Grenade Launcher": Stratagem(
        name="GL-21 Grenade Launcher", name_cn="",
        sequence=["down", "left", "up", "left", "down"],
    ),
    "FLAM-40 Flamethrower": Stratagem(
        name="FLAM-40 Flamethrower", name_cn="",
        sequence=["down", "left", "up", "down", "up"],
    ),
    "MG-206 Heavy Machine Gun": Stratagem(
        name="MG-206 Heavy Machine Gun", name_cn="",
        sequence=["down", "left", "up", "down", "down"],
    ),
    "AC-8 Autocannon": Stratagem(
        name="AC-8 Autocannon", name_cn="",
        sequence=["down", "left", "down", "up", "up", "right"],
    ),
    "ARC-3 Arc Thrower": Stratagem(
        name="ARC-3 Arc Thrower", name_cn="",
        sequence=["down", "right", "down", "up", "left", "left"],
    ),
    "LAS-99 Quasar Cannon": Stratagem(
        name="LAS-99 Quasar Cannon", name_cn="",
        sequence=["down", "down", "up", "left", "right"],
    ),
    "RL-77 Airburst Rocket Launcher": Stratagem(
        name="RL-77 Airburst Rocket Launcher", name_cn="",
        sequence=["down", "up", "up", "left", "right"],
    ),
    "MLS-4X Commando": Stratagem(
        name="MLS-4X Commando", name_cn="",
        sequence=["down", "left", "up", "down", "right"],
    ),
    "FAF-14 Spear": Stratagem(
        name="FAF-14 Spear", name_cn="",
        sequence=["down", "down", "up", "down", "down"],
    ),
    "RS-422 Railgun": Stratagem(
        name="RS-422 Railgun", name_cn="",
        sequence=["down", "right", "down", "up", "left", "right"],
    ),
    "StA-X3 W.A.S.P. Launcher": Stratagem(
        name="StA-X3 W.A.S.P. Launcher", name_cn="",
        sequence=["down", "down", "up", "down", "right"],
    ),
    "CQC-20 Breaching Hammer": Stratagem(
        name="CQC-20 Breaching Hammer", name_cn="",
        sequence=["down", "left", "right", "left", "up"],
    ),
    "PLAS-45 Epoch": Stratagem(
        name="PLAS-45 Epoch", name_cn="",
        sequence=["down", "left", "up", "left", "right"],
    ),
    "MGX-42 Bullet Storm": Stratagem(
        name="MGX-42 Bullet Storm", name_cn="",
        sequence=["down", "left", "down", "right", "up", "left"],
    ),
    "S-11 Speargun": Stratagem(
        name="S-11 Speargun", name_cn="",
        sequence=["down", "right", "down", "left", "up", "right"],
    ),
    "CQC-9 Defoliation Tool": Stratagem(
        name="CQC-9 Defoliation Tool", name_cn="",
        sequence=["down", "left", "right", "right", "down"],
    ),
    "GL-52 De-Escalator": Stratagem(
        name="GL-52 De-Escalator", name_cn="",
        sequence=["down", "right", "up", "left", "right"],
    ),
    "EAT-700 Expendable Napalm": Stratagem(
        name="EAT-700 Expendable Napalm", name_cn="",
        sequence=["down", "down", "left", "up", "left"],
    ),
    "TX-41 Sterilizer": Stratagem(
        name="TX-41 Sterilizer", name_cn="",
        sequence=["down", "left", "up", "down", "left"],
    ),
    "EAT-411 Leveller": Stratagem(
        name="EAT-411 Leveller", name_cn="",
        sequence=["down", "down", "left", "up", "down"],
    ),
    "GL-28 Belt-Fed Grenade Launcher": Stratagem(
        name="GL-28 Belt-Fed Grenade Launcher", name_cn="",
        sequence=["down", "left", "up", "left", "up", "up"],
    ),
    "B/MD C4 Pack": Stratagem(
        name="B/MD C4 Pack", name_cn="",
        sequence=["down", "right", "up", "up", "right", "up"],
    ),
    "MS-11 Solo Silo": Stratagem(
        name="MS-11 Solo Silo", name_cn="",
        sequence=["down", "up", "right", "down", "down"],
    ),
    "B/FLAM-80 Cremator": Stratagem(
        name="B/FLAM-80 Cremator", name_cn="",
        sequence=["down", "down", "right", "down", "up", "up"],
    ),
    "M-1000 Maxigun": Stratagem(
        name="M-1000 Maxigun", name_cn="",
        sequence=["down", "left", "right", "down", "up", "up"],
    ),
    "CQC-1 One True Flag": Stratagem(
        name="CQC-1 One True Flag", name_cn="",
        sequence=["down", "left", "right", "right", "up"],
    ),
    "40-K Meltagun": Stratagem(
        name="40-K Meltagun", name_cn="",
        sequence=["down", "left", "up", "left", "left", "down"],
    ),

    # Backpacks
    "B-1 Supply Pack": Stratagem(
        name="B-1 Supply Pack", name_cn="",
        sequence=["down", "left", "down", "up", "up", "down"],
    ),
    "LIFT-850 Jump Pack": Stratagem(
        name="LIFT-850 Jump Pack", name_cn="",
        sequence=["down", "up", "up", "down", "up"],
    ),
    "SH-20 Ballistic Shield Backpack": Stratagem(
        name="SH-20 Ballistic Shield Backpack", name_cn="",
        sequence=["down", "left", "down", "down", "up", "left"],
    ),
    "AX/AR-23 Guard Dog": Stratagem(
        name="AX/AR-23 Guard Dog", name_cn="",
        sequence=["down", "up", "left", "up", "right", "down"],
    ),
    "AX/LAS-5 Rover": Stratagem(
        name="AX/LAS-5 Rover", name_cn="",
        sequence=["down", "up", "left", "up", "right", "right"],
    ),
    "SH-32 Shield Generator Pack": Stratagem(
        name="SH-32 Shield Generator Pack", name_cn="",
        sequence=["down", "up", "left", "right", "left", "right"],
    ),
    "SH-51 Directional Shield": Stratagem(
        name="SH-51 Directional Shield", name_cn="",
        sequence=["down", "up", "left", "right", "up", "up"],
    ),
    "AX/FLAM-75 Hot Dog": Stratagem(
        name="AX/FLAM-75 Hot Dog", name_cn="",
        sequence=["down", "up", "left", "up", "left", "left"],
    ),
    "B-100 Portable Hellbomb": Stratagem(
        name="B-100 Portable Hellbomb", name_cn="",
        sequence=["down", "right", "up", "up", "up"],
    ),
    "AX/ARC-3 K-9": Stratagem(
        name="AX/ARC-3 K-9", name_cn="",
        sequence=["down", "up", "left", "up", "right", "left"],
    ),
    "LIFT-860 Hover Pack": Stratagem(
        name="LIFT-860 Hover Pack", name_cn="",
        sequence=["down", "up", "up", "down", "left", "right"],
    ),
    "AX/TX-13 Dog Breath": Stratagem(
        name="AX/TX-13 Dog Breath", name_cn="",
        sequence=["down", "up", "left", "up", "right", "up"],
    ),
    "LIFT-182 Warp Pack": Stratagem(
        name="LIFT-182 Warp Pack", name_cn="",
        sequence=["down", "left", "right", "down", "left", "right"],
    ),

    # Vehicles
    "M-103 Supply FRV": Stratagem(
        name="M-103 Supply FRV", name_cn="",
        sequence=["left", "down", "left", "left", "down", "up", "right"],
    ),
    "M-104 Incinerator FRV": Stratagem(
        name="M-104 Incinerator FRV", name_cn="",
        sequence=["left", "down", "right", "left", "down", "up", "up"],
    ),
    "EXO-49 Emancipator Exosuit": Stratagem(
        name="EXO-49 Emancipator Exosuit", name_cn="",
        sequence=["left", "down", "right", "up", "left", "down", "up"],
    ),
    "EXO-45 Patriot Exosuit": Stratagem(
        name="EXO-45 Patriot Exosuit", name_cn="",
        sequence=["left", "down", "right", "up", "left", "down", "down"],
    ),
    "M-102 Gunner FRV": Stratagem(
        name="M-102 Gunner FRV", name_cn="",
        sequence=["left", "down", "right", "down", "right", "down", "up"],
    ),
    "TD-220 Bastion MK XVI": Stratagem(
        name="TD-220 Bastion MK XVI", name_cn="",
        sequence=["left", "down", "right", "down",
                  "left", "down", "up", "down", "up"],
    ),
    "EXO-55 Breakthrough Exosuit": Stratagem(
        name="EXO-55 Breakthrough Exosuit", name_cn="",
        sequence=["left", "down", "right", "left", "right", "down", "up"],
    ),
    "EXO-51 Lumberer Exosuit": Stratagem(
        name="EXO-51 Lumberer Exosuit", name_cn="",
        sequence=["left", "down", "right", "up", "right", "left", "up"],
    ),

    # Defensive Permit
    # Sentries
    "A/MG-43 Machine Gun Sentry": Stratagem(
        name="A/MG-43 Machine Gun Sentry", name_cn="",
        sequence=["down", "up", "right", "right", "up"],
    ),
    "A/G-16 Gatling Sentry": Stratagem(
        name="A/G-16 Gatling Sentry", name_cn="",
        sequence=["down", "up", "right", "left"],
    ),
    "A/AC-8 Autocannon Sentry": Stratagem(
        name="A/AC-8 Autocannon Sentry", name_cn="",
        sequence=["down", "up", "right", "up", "left", "up"],
    ),
    "A/M-12 Mortar Sentry": Stratagem(
        name="A/M-12 Mortar Sentry", name_cn="",
        sequence=["down", "up", "right", "right", "down"],
    ),
    "A/MLS-4X Rocket Sentry": Stratagem(
        name="A/MLS-4X Rocket Sentry", name_cn="",
        sequence=["down", "up", "right", "right", "left"],
    ),
    "A/ARC-3 Tesla Tower": Stratagem(
        name="A/ARC-3 Tesla Tower", name_cn="",
        sequence=["down", "up", "right", "up", "left", "right"],
    ),
    "A/M-23 EMS Mortar Sentry": Stratagem(
        name="A/M-23 EMS Mortar Sentry", name_cn="",
        sequence=["down", "up", "right", "down", "right"],
    ),
    "A/LAS-98 Laser Sentry": Stratagem(
        name="A/LAS-98 Laser Sentry", name_cn="",
        sequence=["down", "up", "right", "down", "up", "right"],
    ),
    "A/FLAM-40 Flame Sentry": Stratagem(
        name="A/FLAM-40 Flame Sentry", name_cn="",
        sequence=["down", "up", "right", "down", "up", "up"],
    ),
    "A/GM-17 Gas Mortar Sentry": Stratagem(
        name="A/GM-17 Gas Mortar Sentry", name_cn="",
        sequence=["down", "up", "right", "down", "left"],
    ),

    # Emplacements
    "MD-6 Anti-Personnel Minefield": Stratagem(
        name="MD-6 Anti-Personnel Minefield", name_cn="",
        sequence=["down", "left", "up", "right"],
    ),
    "MD-I4 Incendiary Mines": Stratagem(
        name="MD-I4 Incendiary Mines", name_cn="",
        sequence=["down", "left", "left", "down"],
    ),
    "MD-17 Anti-Tank Mines": Stratagem(
        name="MD-17 Anti-Tank Mines", name_cn="",
        sequence=["down", "left", "up", "up"],
    ),
    "FX-12 Shield Generator Relay": Stratagem(
        name="FX-12 Shield Generator Relay", name_cn="",
        sequence=["down", "down", "left", "right", "left", "right"],
    ),
    "E/MG-101 HMG Emplacement": Stratagem(
        name="E/MG-101 HMG Emplacement", name_cn="",
        sequence=["down", "up", "left", "right", "right", "left"],
    ),
    "E/GL-21 Grenadier Battlement": Stratagem(
        name="E/GL-21 Grenadier Battlement", name_cn="",
        sequence=["down", "right", "down", "left", "right"],
    ),
    "MD-8 Gas Mines": Stratagem(
        name="MD-8 Gas Mines", name_cn="",
        sequence=["down", "left", "left", "right"],
    ),
    "E/AT-12 Anti-Tank Emplacement": Stratagem(
        name="E/AT-12 Anti-Tank Emplacement", name_cn="",
        sequence=["down", "up", "left", "right", "right", "right"],
    ),

    # Other
    # Mission Stratagems / Ship
    "Eagle Rearm": Stratagem(
        name="Eagle Rearm", name_cn="",
        sequence=["up", "up", "left", "up", "right"],
    ),
    "Call In Super Destroyer": Stratagem(
        name="Call In Super Destroyer", name_cn="",
        sequence=["up", "up", "down", "down",
                  "left", "right", "left", "right"],
    ),
    "Reinforce": Stratagem(
        name="Reinforce", name_cn="",
        sequence=["up", "down", "right", "left", "up"],
    ),
    "SoS Beacon": Stratagem(
        name="SoS Beacon", name_cn="",
        sequence=["up", "down", "right", "up"],
    ),
    "Resupply": Stratagem(
        name="Resupply", name_cn="",
        sequence=["down", "down", "up", "right"],
    ),

    # Mission Stratagems / Objective
    "Cargo Container": Stratagem(
        name="Cargo Container", name_cn="",
        sequence=["up", "up", "down", "down", "right", "down"],
    ),
    "NUX-223 Hellbomb": Stratagem(
        name="NUX-223 Hellbomb", name_cn="",
        sequence=["down", "up", "left", "down", "up", "right", "down", "up"],
    ),
    "Seismic Probe": Stratagem(
        name="Seismic Probe", name_cn="",
        sequence=["up", "up", "left", "right", "down", "down"],
    ),
    "SSSD Delivery": Stratagem(
        name="SSSD Delivery", name_cn="",
        sequence=["down", "down", "down", "down", "down", "up", "up"],
    ),
    "Tectonic Drill": Stratagem(
        name="Tectonic Drill", name_cn="",
        sequence=["up", "down", "up", "down", "up", "down"],
    ),
    "Upload Data": Stratagem(
        name="Upload Data", name_cn="",
        sequence=["left", "right", "up", "up", "up"],
    ),
    "Reinforcement Pods": Stratagem(
        name="Reinforcement Pods", name_cn="",
        sequence=["left", "right", "up", "up", "up"],
    ),
    "Tactical Video Camera": Stratagem(
        name="Tactical Video Camera", name_cn="",
        sequence=["right", "down", "down", "up", "left", "left", "up"],
    ),
    "Aquifer Drill": Stratagem(
        name="Aquifer Drill", name_cn="",
        sequence=["left", "left", "left", "up",
                  "down", "right", "down", "down"],
    ),
    "Portable Comms Relay": Stratagem(
        name="Portable Comms Relay", name_cn="",
        sequence=["up", "up", "down", "down", "left", "left", "down"],
    ),
    "Prospecting Drill": Stratagem(
        name="Prospecting Drill", name_cn="",
        sequence=["down", "down", "left", "right", "down", "down"],
    ),
    "Hive Breaker Drill": Stratagem(
        name="Hive Breaker Drill", name_cn="",
        sequence=["left", "up", "down", "right", "down", "down"],
    ),
    "Activate E-711 Extraction Drill": Stratagem(
        name="Activate E-711 Extraction Drill", name_cn="",
        sequence=["down", "down", "left", "left", "down", "down"],
    ),
    "Dark Fluid Vessel": Stratagem(
        name="Dark Fluid Vessel", name_cn="",
        sequence=["up", "left", "right", "down", "up", "up"],
    ),
    "Super Earth Flag": Stratagem(
        name="Super Earth Flag", name_cn="",
        sequence=["down", "up", "down", "up"],
    ),
    "SEAF Artillery": Stratagem(
        name="SEAF Artillery", name_cn="",
        sequence=["right", "up", "up", "down"],
    ),

    # Mission Stratagems / Unavailable
    "Orbital Illumination Flare": Stratagem(
        name="Orbital Illumination Flare", name_cn="",
        sequence=["right", "right", "left", "left"],
    ),
}
