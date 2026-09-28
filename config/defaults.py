from hotkeys.models import Binding


INPUT_PAUSE = 0.017

DEFAULT_BINDINGS = (
    Binding("f1", "stratagem", "Reinforce"),
    Binding("f2", "stratagem", "Resupply"),
    Binding("f3", "stratagem", "NUX-223 Hellbomb"),
    Binding("f4", "stratagem", "SEAF Artillery"),

    Binding("f5", "stratagem", "A/MG-43 Machine Gun Sentry"),
    Binding("f6", "stratagem", "A/FLAM-40 Flame Sentry"),
    Binding("f7", "stratagem", "Orbital Napalm Barrage"),
    Binding("f8", "stratagem", "Orbital 120mm HE Barrage"),
    
    Binding("f9", "stratagem", "Orbital 380mm HE Barrage"),
    Binding("f10", "stratagem", "B-1 Supply Pack"),

    Binding("f12", "chat", "sorry"),

    Binding("page down", "open_chat"),

    Binding("n", "recognize_terminal"),
)
