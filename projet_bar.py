class Accessoire:
    """Classe mère des accessoires du bar"""

    def __init__(self):
        self.file = []


class Pic(Accessoire):
    """
    Un pic contient les commandes à fabriquer.
    Il peut embrocher un post-it contenant une commande
    (une liste de consommations) par-dessus les post-it
    déjà présents et libérer le premier embroché.
    """

    def embrocher(self, postit):
        """Ajoute un post-it à la file."""
        self.file.append(postit)

    def liberer(self):
        """Récupère le plus ancien post-it."""
        if self.file:
            postit = self.file.pop(0)
            return postit
        return None

class Bar(Accessoire):
    """
    Un bar peut recevoir des commandes (composées de consommations),
    en attente d'être servies (évacuées).
    """

    def recevoir(self, commande):
        """Dépose un plateau sur le bar."""
        self.file.append(commande)

    def evacuer(self):
        """Récupère le plus ancien plateau."""
        if self.file:
            commande = self.file.pop(0)
            return commande
        return None

class Employe:
    """Classe mère des employés."""

    def __init__(self, nom, pic, bar):
        self.nom = nom
        self.pic = pic
        self.bar = bar

    def afficher(self, message):
        print(f"{self.nom}: {message}")

class Serveur(Employe):

    def __init__(self, pic, bar, commandes):
        super().__init__("Serveur", pic, bar)
        self.commandes = commandes.copy()

    def prendre_commande(self):
        """Prend une commande et embroche un post-it."""

        if not self.commandes:
            return

        self.afficher("prêt pour prendre une commande :")

        commande = self.commandes.pop(0)

        self.afficher(f"j'ai la commande '{','.join(commande)}'")

        self.afficher(f"j'écris sur le post-it '{commande}'")

        self.pic.embrocher(commande)


    def servir(self):
        """Prend un plateau sur le bar et sert les clients."""

        commande = self.bar.evacuer()

        if commande is not None:
            self.afficher(f"j'apporte la commande' {commande}")

            for cocktail in commande:
                self.afficher(f"je sers {cocktail}")


    def run(self):
        """Serveur en action."""

        if self.commandes:
            while self.commandes:
                self.prendre_commande()

        elif self.bar.file:
            while self.bar.file:
                self.servir()


class Bariste(Employe):

    def __init__(self, pic, bar):
        super().__init__("Bariste", pic, bar)

    def preparer(self):
        """Prépare une commande et la dépose sur le bar."""

        commande = self.pic.liberer()

        if commande is None:
            return

        self.afficher(f"je commence la fabrication de {commande}")

        for cocktail in commande:
            self.afficher(f"je prépare '{cocktail}'")

        self.afficher(f"la commande {commande} est prête")

        self.bar.recevoir(commande)

    def run(self):
        """Bariste en action."""

        while self.pic.file:
            self.preparer()


def main():

    commandes = [
        ["planteur", "piña colada"],
        ["tequila sunrise", "margarita"]
    ]

    pic = Pic()
    bar = Bar()

    serveur = Serveur(pic, bar, commandes)
    bariste = Bariste(pic, bar)

    bariste.afficher("prêt pour le service")
    serveur.afficher("prêt pour le service")

    serveur.run()

    bariste.run()

    serveur.run()


if __name__ == "__main__":
    main()
