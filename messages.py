"""Keep error identity separate from its translated UI message."""

from localization import DEFAULT_LANGUAGE, tr


class UserFacingError(ValueError):
    def __init__(self, message_key, **values):
        self.message_key = message_key
        self.values = values
        # Logs and failure screenshot filenames stay in the default language.
        super().__init__(tr(message_key, locale=DEFAULT_LANGUAGE, **values))
