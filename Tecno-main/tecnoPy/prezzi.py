class prezzo:
    """A class representing a single record in the CSV file."""

    def __init__(self, id_impianto, desc_carburante, prezzo, is_self, dt_comu):
        self.id_impianto = id_impianto
        self.desc_carburante = desc_carburante
        self.prezzo = prezzo
        self.is_self = is_self
        self.dt_comu = dt_comu

    def __str__(self):
        """Return a string representation of the record."""
        return f"{self.id_impianto}, {self.desc_carburante}, {self.prezzo}, {self.is_self}, {self.dt_comu}"
