class DocumentLegislatifIntrouvableException(Exception):
    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class ActeurIntrouvableException(Exception):
    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)