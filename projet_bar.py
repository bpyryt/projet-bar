import sys
import time
import re


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
            postit = self.file.pop()
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
            commande = self.file.pop()
            return commande
        return None


class Clients:

    def __init__(self, fname):
        commandes = []

        start = time.time()
        fmt = re.compile(r"(\d+)\s+(.*)")

        with open(fname,"r") as f:
            for line in f:
                found = fmt.search(line)

                if found:
                    when = int(found.group(1))
                    what = found.group(2)

                    commandes.append(
                        (start + when, what.split(","))
                    )

        self.commandes = commandes[::-1]


    def commande(self):
            if len(self.commandes)>0:
              while True:
                if time.time()>self.commandes[-1][0]:
                    return self.commandes.pop()[1]
            else:
                return None


class Employe:
    """Classe mère des employés."""

    def __init__(self, nom, pic, bar, clients):
        self.nom = nom
        self.pic = pic
        self.bar = bar
        self.clients = clients

        self.afficher("prêt pour le service")

    def afficher(self, message):
        print(f"{self.nom}: {message}")

class Serveur(Employe):

    def __init__(self, pic, bar, clients):
        super().__init__("Serveur", pic, bar, clients)
        self.commandes_terminees = False

    def prendre_commande(self):
        """Prend une commande et embroche un post-it."""

        self.afficher("prêt pour prendre une commande :")

        commande = self.clients.commande()
        
        if commande is None:
            return False

        self.afficher(f"j'ai la commande '{commande}'")

        self.afficher(f"j'écris sur le post-it '{commande}'")

        self.pic.embrocher(commande)

        return True


    def servir(self):
        """Prend un plateau sur le bar et sert les clients."""

        commande = self.bar.evacuer()

        if commande is not None:
            self.afficher(f"j'apporte la commande' {commande}")

            for cocktail in commande:
                self.afficher(f"je sers {cocktail}")


    def run(self):
        """Serveur en action."""

        if not self.commandes_terminees:

            while self.prendre_commande():
                pass

            self.commandes_terminees = True

        else:

            while self.bar.file:
                self.servir()



class Bariste(Employe):

    def __init__(self, pic, bar, clients):
        super().__init__("Bariste", pic, bar, clients)

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


def usage():
    print(f"usage: {sys.argv[0]} fichier")
    sys.exit(1)

def main():

    if len(sys.argv) != 2:
        usage()

    fcommandes = sys.argv[1]

    le_pic = Pic()
    le_bar = Bar()

    les_clients = Clients(fcommandes)

    bob = Bariste(le_pic, le_bar, les_clients)
    alice = Serveur(le_pic, le_bar, les_clients)

    # 1. Le serveur prend les commandes
    alice.run()

    # 2. Le bariste prépare les commandes
    bob.run()

    # 3. Le serveur apporte les consommations
    alice.run()


if __name__ == "__main__":
    main()

