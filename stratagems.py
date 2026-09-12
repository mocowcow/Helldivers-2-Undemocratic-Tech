
class Stratagem:
    def __init__(self, name, sequence, category, subcategory, svg_name=""):
        self.name = name
        self.sequence = sequence
        self.category = category
        self.subcategory = subcategory
        self.svg_name = svg_name


# Source: https://helldivers.wiki.gg/wiki/Stratagems
# Retrieved 2026-09-10; entries follow the source HTML table order.
# Arrow image alt text is converted to up/down/left/right.
STRATAGEMS = {
    # Offensive Permit
    # Orbital Strikes
    "Orbital Precision Strike": Stratagem(
        name="Orbital Precision Strike", 
        svg_name="Orbital Precision Strike.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "right", "up"],
    ),
    "Orbital Gatling Barrage": Stratagem(
        name="Orbital Gatling Barrage", 
        svg_name="Orbital Gatling Barrage.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "down", "left", "up", "up"],
    ),
    "Orbital Gas Strike": Stratagem(
        name="Orbital Gas Strike", 
        svg_name="Orbital Gas Strike.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "right", "down", "right"],
    ),
    "Orbital 120mm HE Barrage": Stratagem(
        name="Orbital 120mm HE Barrage", 
        svg_name="Orbital 120MM HE Barrage.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "right", "down", "left", "right", "down"],
    ),
    "Orbital Airburst Strike": Stratagem(
        name="Orbital Airburst Strike", 
        svg_name="Orbital Airburst Strike.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "right", "right"],
    ),
    "Orbital Smoke Strike": Stratagem(
        name="Orbital Smoke Strike", 
        svg_name="Orbital Smoke Strike.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "right", "down", "up"],
    ),
    "Orbital EMS Strike": Stratagem(
        name="Orbital EMS Strike", 
        svg_name="Orbital EMS Strike.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "right", "left", "down"],
    ),
    "Orbital 380mm HE Barrage": Stratagem(
        name="Orbital 380mm HE Barrage", 
        svg_name="Orbital 380MM HE Barrage.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "down", "up", "up", "left", "down", "down"],
    ),
    "Orbital Walking Barrage": Stratagem(
        name="Orbital Walking Barrage", 
        svg_name="Orbital Walking Barrage.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "down", "right", "down", "right", "down"],
    ),
    "Orbital Laser": Stratagem(
        name="Orbital Laser", 
        svg_name="Orbital Laser.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "down", "up", "right", "down"],
    ),
    "Orbital Napalm Barrage": Stratagem(
        name="Orbital Napalm Barrage", 
        svg_name="Orbital Napalm Barrage.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "right", "down", "left", "right", "up"],
    ),
    "Orbital Railcannon Strike": Stratagem(
        name="Orbital Railcannon Strike", 
        svg_name="Orbital Railcannon Strike.svg",
        category="Offensive Permit", subcategory="Orbital Strikes",
        sequence=["right", "up", "down", "down", "right"],
    ),

    # Eagle Strikes
    "Eagle Gas Airstrike": Stratagem(
        name="Eagle Gas Airstrike", 
        svg_name="Eagle Gas Strike.svg",
        category="Offensive Permit", subcategory="Eagle Strikes",
        sequence=["up", "right", "left", "right"],
    ),
    "Eagle Strafing Run": Stratagem(
        name="Eagle Strafing Run", 
        svg_name="Eagle Strafing Run.svg",
        category="Offensive Permit", subcategory="Eagle Strikes",
        sequence=["up", "right", "right"],
    ),
    "Eagle Airstrike": Stratagem(
        name="Eagle Airstrike", 
        svg_name="Eagle Airstrike.svg",
        category="Offensive Permit", subcategory="Eagle Strikes",
        sequence=["up", "right", "down", "right"],
    ),
    "Eagle Cluster Bomb": Stratagem(
        name="Eagle Cluster Bomb", 
        svg_name="Eagle Cluster Bomb.svg",
        category="Offensive Permit", subcategory="Eagle Strikes",
        sequence=["up", "right", "down", "down", "right"],
    ),
    "Eagle Smoke Strike": Stratagem(
        name="Eagle Smoke Strike", 
        svg_name="Eagle Smoke Strike.svg",
        category="Offensive Permit", subcategory="Eagle Strikes",
        sequence=["up", "right", "up", "down"],
    ),
    "Eagle Napalm Airstrike": Stratagem(
        name="Eagle Napalm Airstrike", 
        svg_name="Eagle Napalm Airstrike.svg",
        category="Offensive Permit", subcategory="Eagle Strikes",
        sequence=["up", "right", "down", "up"],
    ),
    "Eagle 110mm Rocket Pods": Stratagem(
        name="Eagle 110mm Rocket Pods", 
        svg_name="Eagle 110MM Rocket Pods.svg",
        category="Offensive Permit", subcategory="Eagle Strikes",
        sequence=["up", "right", "up", "left"],
    ),
    "Eagle 500kg Bomb": Stratagem(
        name="Eagle 500kg Bomb", 
        svg_name="Eagle 500KG Bomb.svg",
        category="Offensive Permit", subcategory="Eagle Strikes",
        sequence=["up", "right", "down", "down", "down"],
    ),

    # Supply Permit
    # Support Weapons
    "MG-43 Machine Gun": Stratagem(
        name="MG-43 Machine Gun", 
        svg_name="Machine Gun.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "down", "up", "right"],
    ),
    "EAT-17 Expendable Anti-Tank": Stratagem(
        name="EAT-17 Expendable Anti-Tank", 
        svg_name="Expendable Anti-Tank.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "down", "left", "up", "right"],
    ),
    "M-105 Stalwart": Stratagem(
        name="M-105 Stalwart", 
        svg_name="Stalwart.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "down", "up", "up", "left"],
    ),
    "LAS-98 Laser Cannon": Stratagem(
        name="LAS-98 Laser Cannon", 
        svg_name="Laser Cannon.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "down", "up", "left"],
    ),
    "APW-1 Anti-Materiel Rifle": Stratagem(
        name="APW-1 Anti-Materiel Rifle", 
        svg_name="Anti-Materiel Rifle.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "right", "up", "down"],
    ),
    "GR-8 Recoilless Rifle": Stratagem(
        name="GR-8 Recoilless Rifle", 
        svg_name="Recoilless Rifle.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "right", "right", "left"],
    ),
    "GL-21 Grenade Launcher": Stratagem(
        name="GL-21 Grenade Launcher", 
        svg_name="Grenade Launcher.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "up", "left", "down"],
    ),
    "FLAM-40 Flamethrower": Stratagem(
        name="FLAM-40 Flamethrower", 
        svg_name="Flamethrower.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "up", "down", "up"],
    ),
    "MG-206 Heavy Machine Gun": Stratagem(
        name="MG-206 Heavy Machine Gun", 
        svg_name="Heavy Machine Gun.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "up", "down", "down"],
    ),
    "AC-8 Autocannon": Stratagem(
        name="AC-8 Autocannon", 
        svg_name="Autocannon.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "down", "up", "up", "right"],
    ),
    "ARC-3 Arc Thrower": Stratagem(
        name="ARC-3 Arc Thrower", 
        svg_name="Arc Thrower.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "right", "down", "up", "left", "left"],
    ),
    "LAS-99 Quasar Cannon": Stratagem(
        name="LAS-99 Quasar Cannon", 
        svg_name="Quasar Cannon.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "down", "up", "left", "right"],
    ),
    "RL-77 Airburst Rocket Launcher": Stratagem(
        name="RL-77 Airburst Rocket Launcher", 
        svg_name="Airburst Rocket Launcher.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "up", "up", "left", "right"],
    ),
    "MLS-4X Commando": Stratagem(
        name="MLS-4X Commando", 
        svg_name="Commando.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "up", "down", "right"],
    ),
    "FAF-14 Spear": Stratagem(
        name="FAF-14 Spear", 
        svg_name="Spear.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "down", "up", "down", "down"],
    ),
    "RS-422 Railgun": Stratagem(
        name="RS-422 Railgun", 
        svg_name="Railgun.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "right", "down", "up", "left", "right"],
    ),
    "StA-X3 W.A.S.P. Launcher": Stratagem(
        name="StA-X3 W.A.S.P. Launcher", 
        svg_name="StA-X3 W.A.S.P. Launcher.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "down", "up", "down", "right"],
    ),
    "CQC-20 Breaching Hammer": Stratagem(
        name="CQC-20 Breaching Hammer", 
        svg_name="CQC-20.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "right", "left", "up"],
    ),
    "PLAS-45 Epoch": Stratagem(
        name="PLAS-45 Epoch", 
        svg_name="Epoch.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "up", "left", "right"],
    ),
    "MGX-42 Bullet Storm": Stratagem(
        name="MGX-42 Bullet Storm", 
        svg_name="Bullet Storm.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "down", "right", "up", "left"],
    ),
    "S-11 Speargun": Stratagem(
        name="S-11 Speargun", 
        svg_name="Speargun.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "right", "down", "left", "up", "right"],
    ),
    "CQC-9 Defoliation Tool": Stratagem(
        name="CQC-9 Defoliation Tool", 
        svg_name="Defoliation Tool.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "right", "right", "down"],
    ),
    "GL-52 De-Escalator": Stratagem(
        name="GL-52 De-Escalator", 
        svg_name="GL-52 De-Escalator.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "right", "up", "left", "right"],
    ),
    "EAT-700 Expendable Napalm": Stratagem(
        name="EAT-700 Expendable Napalm", 
        svg_name="Expendable Napalm.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "down", "left", "up", "left"],
    ),
    "TX-41 Sterilizer": Stratagem(
        name="TX-41 Sterilizer", 
        svg_name="Sterilizer.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "up", "down", "left"],
    ),
    "EAT-411 Leveller": Stratagem(
        name="EAT-411 Leveller", 
        svg_name="EAT-411.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "down", "left", "up", "down"],
    ),
    "GL-28 Belt-Fed Grenade Launcher": Stratagem(
        name="GL-28 Belt-Fed Grenade Launcher", 
        svg_name="GL-28.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "up", "left", "up", "up"],
    ),
    "B/MD C4 Pack": Stratagem(
        name="B/MD C4 Pack", 
        svg_name="C4 Pack.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "right", "up", "up", "right", "up"],
    ),
    "MS-11 Solo Silo": Stratagem(
        name="MS-11 Solo Silo", 
        svg_name="Solo Silo.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "up", "right", "down", "down"],
    ),
    "B/FLAM-80 Cremator": Stratagem(
        name="B/FLAM-80 Cremator", 
        svg_name="Cremator.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "down", "right", "down", "up", "up"],
    ),
    "M-1000 Maxigun": Stratagem(
        name="M-1000 Maxigun", 
        svg_name="Maxigun.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "right", "down", "up", "up"],
    ),
    "CQC-1 One True Flag": Stratagem(
        name="CQC-1 One True Flag", 
        svg_name="One True Flag.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "right", "right", "up"],
    ),
    "40-K Meltagun": Stratagem(
        name="40-K Meltagun", 
        svg_name="40-K Meltagun.svg",
        category="Supply Permit", subcategory="Support Weapons",
        sequence=["down", "left", "up", "left", "left", "down"],
    ),

    # Backpacks
    "B-1 Supply Pack": Stratagem(
        name="B-1 Supply Pack", 
        svg_name="Supply Pack.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "left", "down", "up", "up", "down"],
    ),
    "LIFT-850 Jump Pack": Stratagem(
        name="LIFT-850 Jump Pack", 
        svg_name="Jump Pack.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "up", "up", "down", "up"],
    ),
    "SH-20 Ballistic Shield Backpack": Stratagem(
        name="SH-20 Ballistic Shield Backpack", 
        svg_name="Ballistic Shield Backpack.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "left", "down", "down", "up", "left"],
    ),
    "AX/AR-23 Guard Dog": Stratagem(
        name="AX/AR-23 Guard Dog", 
        svg_name="Guard Dog.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "up", "left", "up", "right", "down"],
    ),
    "AX/LAS-5 Rover": Stratagem(
        name="AX/LAS-5 Rover", 
        svg_name="Guard Dog Rover.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "up", "left", "up", "right", "right"],
    ),
    "SH-32 Shield Generator Pack": Stratagem(
        name="SH-32 Shield Generator Pack", 
        svg_name="Shield Generator Pack.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "up", "left", "right", "left", "right"],
    ),
    "SH-51 Directional Shield": Stratagem(
        name="SH-51 Directional Shield", 
        svg_name="Directional Shield.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "up", "left", "right", "up", "up"],
    ),
    "AX/FLAM-75 Hot Dog": Stratagem(
        name="AX/FLAM-75 Hot Dog", 
        svg_name="Guard Dog Hot Dog.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "up", "left", "up", "left", "left"],
    ),
    "B-100 Portable Hellbomb": Stratagem(
        name="B-100 Portable Hellbomb", 
        svg_name="Hellbomb Portable.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "right", "up", "up", "up"],
    ),
    "AX/ARC-3 K-9": Stratagem(
        name="AX/ARC-3 K-9", 
        svg_name="Guard Dog K-9.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "up", "left", "up", "right", "left"],
    ),
    "LIFT-860 Hover Pack": Stratagem(
        name="LIFT-860 Hover Pack", 
        svg_name="Hover Pack.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "up", "up", "down", "left", "right"],
    ),
    "AX/TX-13 Dog Breath": Stratagem(
        name="AX/TX-13 Dog Breath", 
        svg_name="Guard Dog Breath.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "up", "left", "up", "right", "up"],
    ),
    "LIFT-182 Warp Pack": Stratagem(
        name="LIFT-182 Warp Pack", 
        svg_name="Warp Pack.svg",
        category="Supply Permit", subcategory="Backpacks",
        sequence=["down", "left", "right", "down", "left", "right"],
    ),

    # Vehicles
    "M-103 Supply FRV": Stratagem(
        name="M-103 Supply FRV", 
        svg_name="Supply FRV.svg",
        category="Supply Permit", subcategory="Vehicles",
        sequence=["left", "down", "left", "left", "down", "up", "right"],
    ),
    "M-104 Incinerator FRV": Stratagem(
        name="M-104 Incinerator FRV", 
        svg_name="Incinerator FRV.svg",
        category="Supply Permit", subcategory="Vehicles",
        sequence=["left", "down", "right", "left", "down", "up", "up"],
    ),
    "EXO-49 Emancipator Exosuit": Stratagem(
        name="EXO-49 Emancipator Exosuit", 
        svg_name="Emancipator Exosuit.svg",
        category="Supply Permit", subcategory="Vehicles",
        sequence=["left", "down", "right", "up", "left", "down", "up"],
    ),
    "EXO-45 Patriot Exosuit": Stratagem(
        name="EXO-45 Patriot Exosuit", 
        svg_name="Patriot Exosuit.svg",
        category="Supply Permit", subcategory="Vehicles",
        sequence=["left", "down", "right", "up", "left", "down", "down"],
    ),
    "M-102 Gunner FRV": Stratagem(
        name="M-102 Gunner FRV", 
        svg_name="Fast Recon Vehicle.svg",
        category="Supply Permit", subcategory="Vehicles",
        sequence=["left", "down", "right", "down", "right", "down", "up"],
    ),
    "TD-220 Bastion MK XVI": Stratagem(
        name="TD-220 Bastion MK XVI", 
        svg_name="Bastion MK XVI.svg",
        category="Supply Permit", subcategory="Vehicles",
        sequence=["left", "down", "right", "down",
                  "left", "down", "up", "down", "up"],
    ),
    "EXO-55 Breakthrough Exosuit": Stratagem(
        name="EXO-55 Breakthrough Exosuit", 
        svg_name="Breakthrough Exosuit.svg",
        category="Supply Permit", subcategory="Vehicles",
        sequence=["left", "down", "right", "left", "right", "down", "up"],
    ),
    "EXO-51 Lumberer Exosuit": Stratagem(
        name="EXO-51 Lumberer Exosuit", 
        svg_name="Lumberer Exosuit.svg",
        category="Supply Permit", subcategory="Vehicles",
        sequence=["left", "down", "right", "up", "right", "left", "up"],
    ),

    # Defensive Permit
    # Sentries
    "A/MG-43 Machine Gun Sentry": Stratagem(
        name="A/MG-43 Machine Gun Sentry", 
        svg_name="Machine Gun Sentry.svg",
        category="Defensive Permit", subcategory="Sentries",
        sequence=["down", "up", "right", "right", "up"],
    ),
    "A/G-16 Gatling Sentry": Stratagem(
        name="A/G-16 Gatling Sentry", 
        svg_name="Gatling Sentry.svg",
        category="Defensive Permit", subcategory="Sentries",
        sequence=["down", "up", "right", "left"],
    ),
    "A/AC-8 Autocannon Sentry": Stratagem(
        name="A/AC-8 Autocannon Sentry", 
        svg_name="Autocannon Sentry.svg",
        category="Defensive Permit", subcategory="Sentries",
        sequence=["down", "up", "right", "up", "left", "up"],
    ),
    "A/M-12 Mortar Sentry": Stratagem(
        name="A/M-12 Mortar Sentry", 
        svg_name="Mortar Sentry.svg",
        category="Defensive Permit", subcategory="Sentries",
        sequence=["down", "up", "right", "right", "down"],
    ),
    "A/MLS-4X Rocket Sentry": Stratagem(
        name="A/MLS-4X Rocket Sentry", 
        svg_name="Rocket Sentry.svg",
        category="Defensive Permit", subcategory="Sentries",
        sequence=["down", "up", "right", "right", "left"],
    ),
    "A/ARC-3 Tesla Tower": Stratagem(
        name="A/ARC-3 Tesla Tower", 
        svg_name="Tesla Tower.svg",
        category="Defensive Permit", subcategory="Sentries",
        sequence=["down", "up", "right", "up", "left", "right"],
    ),
    "A/M-23 EMS Mortar Sentry": Stratagem(
        name="A/M-23 EMS Mortar Sentry", 
        svg_name="EMS Mortar Sentry.svg",
        category="Defensive Permit", subcategory="Sentries",
        sequence=["down", "up", "right", "down", "right"],
    ),
    "A/LAS-98 Laser Sentry": Stratagem(
        name="A/LAS-98 Laser Sentry", 
        svg_name="Laser Sentry.svg",
        category="Defensive Permit", subcategory="Sentries",
        sequence=["down", "up", "right", "down", "up", "right"],
    ),
    "A/FLAM-40 Flame Sentry": Stratagem(
        name="A/FLAM-40 Flame Sentry", 
        svg_name="Flame Sentry.svg",
        category="Defensive Permit", subcategory="Sentries",
        sequence=["down", "up", "right", "down", "up", "up"],
    ),
    "A/GM-17 Gas Mortar Sentry": Stratagem(
        name="A/GM-17 Gas Mortar Sentry", 
        svg_name="Gas Mortar Sentry.svg",
        category="Defensive Permit", subcategory="Sentries",
        sequence=["down", "up", "right", "down", "left"],
    ),

    # Emplacements
    "MD-6 Anti-Personnel Minefield": Stratagem(
        name="MD-6 Anti-Personnel Minefield", 
        svg_name="Anti-Personnel Minefield.svg",
        category="Defensive Permit", subcategory="Emplacements",
        sequence=["down", "left", "up", "right"],
    ),
    "MD-I4 Incendiary Mines": Stratagem(
        name="MD-I4 Incendiary Mines", 
        svg_name="Incendiary Mines.svg",
        category="Defensive Permit", subcategory="Emplacements",
        sequence=["down", "left", "left", "down"],
    ),
    "MD-17 Anti-Tank Mines": Stratagem(
        name="MD-17 Anti-Tank Mines", 
        svg_name="Anti-Tank Mines.svg",
        category="Defensive Permit", subcategory="Emplacements",
        sequence=["down", "left", "up", "up"],
    ),
    "FX-12 Shield Generator Relay": Stratagem(
        name="FX-12 Shield Generator Relay", 
        svg_name="Shield Generator Relay.svg",
        category="Defensive Permit", subcategory="Emplacements",
        sequence=["down", "down", "left", "right", "left", "right"],
    ),
    "E/MG-101 HMG Emplacement": Stratagem(
        name="E/MG-101 HMG Emplacement", 
        svg_name="HMG Emplacement.svg",
        category="Defensive Permit", subcategory="Emplacements",
        sequence=["down", "up", "left", "right", "right", "left"],
    ),
    "E/GL-21 Grenadier Battlement": Stratagem(
        name="E/GL-21 Grenadier Battlement", 
        svg_name="Grenadier Battlement.svg",
        category="Defensive Permit", subcategory="Emplacements",
        sequence=["down", "right", "down", "left", "right"],
    ),
    "MD-8 Gas Mines": Stratagem(
        name="MD-8 Gas Mines", 
        svg_name="Gas Mine.svg",
        category="Defensive Permit", subcategory="Emplacements",
        sequence=["down", "left", "left", "right"],
    ),
    "E/AT-12 Anti-Tank Emplacement": Stratagem(
        name="E/AT-12 Anti-Tank Emplacement", 
        svg_name="Anti-Tank Emplacement.svg",
        category="Defensive Permit", subcategory="Emplacements",
        sequence=["down", "up", "left", "right", "right", "right"],
    ),

    # Other
    # Mission Stratagems / Ship
    "Eagle Rearm": Stratagem(
        name="Eagle Rearm", 
        svg_name="Eagle Rearm.svg",
        category="Other", subcategory="Mission Stratagems / Ship",
        sequence=["up", "up", "left", "up", "right"],
    ),
    "Call In Super Destroyer": Stratagem(
        name="Call In Super Destroyer", 
        svg_name="Call In Super Destroyer.svg",
        category="Other", subcategory="Mission Stratagems / Ship",
        sequence=["up", "up", "down", "down",
                  "left", "right", "left", "right"],
    ),
    "Reinforce": Stratagem(
        name="Reinforce", 
        svg_name="Reinforce.svg",
        category="Other", subcategory="Mission Stratagems / Ship",
        sequence=["up", "down", "right", "left", "up"],
    ),
    "SoS Beacon": Stratagem(
        name="SoS Beacon", 
        svg_name="SOS Beacon.svg",
        category="Other", subcategory="Mission Stratagems / Ship",
        sequence=["up", "down", "right", "up"],
    ),
    "Resupply": Stratagem(
        name="Resupply", 
        svg_name="Resupply.svg",
        category="Other", subcategory="Mission Stratagems / Ship",
        sequence=["down", "down", "up", "right"],
    ),

    # Mission Stratagems / Objective
    "Cargo Container": Stratagem(
        name="Cargo Container", 
        svg_name="Cargo Container.svg",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["up", "up", "down", "down", "right", "down"],
    ),
    "NUX-223 Hellbomb": Stratagem(
        name="NUX-223 Hellbomb", 
        svg_name="Hellbomb.svg",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["down", "up", "left", "down", "up", "right", "down", "up"],
    ),
    "Seismic Probe": Stratagem(
        name="Seismic Probe", 
        svg_name="Seismic Probe.svg",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["up", "up", "left", "right", "down", "down"],
    ),
    "SSSD Delivery": Stratagem(
        name="SSSD Delivery", 
        svg_name="",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["down", "down", "down", "down", "down", "up", "up"],
    ),
    "Tectonic Drill": Stratagem(
        name="Tectonic Drill", 
        svg_name="Tectonic Drill.svg",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["up", "down", "up", "down", "up", "down"],
    ),
    "Upload Data": Stratagem(
        name="Upload Data", 
        svg_name="Upload Data.svg",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["left", "right", "up", "up", "up"],
    ),
    "Reinforcement Pods": Stratagem(
        name="Reinforcement Pods", 
        svg_name="",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["left", "right", "up", "up", "up"],
    ),
    "Tactical Video Camera": Stratagem(
        name="Tactical Video Camera", 
        svg_name="",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["right", "down", "down", "up", "left", "left", "up"],
    ),
    "Aquifer Drill": Stratagem(
        name="Aquifer Drill", 
        svg_name="",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["left", "left", "left", "up",
                  "down", "right", "down", "down"],
    ),
    "Portable Comms Relay": Stratagem(
        name="Portable Comms Relay", 
        svg_name="",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["up", "up", "down", "down", "left", "left", "down"],
    ),
    "Prospecting Drill": Stratagem(
        name="Prospecting Drill", 
        svg_name="Prospecting Drill.svg",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["down", "down", "left", "right", "down", "down"],
    ),
    "Hive Breaker Drill": Stratagem(
        name="Hive Breaker Drill", 
        svg_name="Hive Breaker Drill.svg",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["left", "up", "down", "right", "down", "down"],
    ),
    "Activate E-711 Extraction Drill": Stratagem(
        name="Activate E-711 Extraction Drill", 
        svg_name="",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["down", "down", "left", "left", "down", "down"],
    ),
    "Dark Fluid Vessel": Stratagem(
        name="Dark Fluid Vessel", 
        svg_name="Dark Fluid Vessel.svg",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["up", "left", "right", "down", "up", "up"],
    ),
    "Super Earth Flag": Stratagem(
        name="Super Earth Flag", 
        svg_name="Super Earth Flag.svg",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["down", "up", "down", "up"],
    ),
    "SEAF Artillery": Stratagem(
        name="SEAF Artillery", 
        svg_name="SEAF Artillery.svg",
        category="Other", subcategory="Mission Stratagems / Objective",
        sequence=["right", "up", "up", "down"],
    ),

    # Mission Stratagems / Unavailable
    "Orbital Illumination Flare": Stratagem(
        name="Orbital Illumination Flare", 
        svg_name="Orbital Illumination Flare.svg",
        category="Other", subcategory="Mission Stratagems / Unavailable",
        sequence=["right", "right", "left", "left"],
    ),
}
