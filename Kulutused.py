class Kulud:
    
    def __init__(self, nimi, liik, kogus, hind, kuupaev):
        self.nimi = nimi
        self.liik = liik
        self.kogus = kogus
        self.hind = hind
        self.kuupaev = kuupaev
        
    def __repr__(self): # Esitab mäluaadressi stringina
        return f"<Kulud: {self.nimi}, {self.liik}, {self.kogus}, {self.hind:.3f}€ >"
