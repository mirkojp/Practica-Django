class EntityNotFoundError(Exception):
    """Excepción personalizada para entidades no encontradas."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
