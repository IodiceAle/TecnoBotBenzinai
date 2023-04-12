class Impianto:
    """A class representing a single gas station."""

    def __init__(self, id_impianto, gestore, bandiera, tipo_impianto, nome_impianto, indirizzo, comune, provincia, latitudine, longitudine):
        self.id_impianto = id_impianto
        self.gestore = gestore
        self.bandiera = bandiera
        self.tipo_impianto = tipo_impianto
        self.nome_impianto = nome_impianto
        self.indirizzo = indirizzo
        self.comune = comune
        self.provincia = provincia
        self.latitudine = latitudine
        self.longitudine = longitudine

    def __str__(self):
        """Return a string representation of the gas station."""
        return f"{self.id_impianto}, {self.gestore}, {self.bandiera}, {self.tipo_impianto}, {self.nome_impianto}, {self.indirizzo}, {self.comune}, {self.provincia}, {self.latitudine}, {self.longitudine}"
