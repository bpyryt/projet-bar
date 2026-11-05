import sys
import time
import re
from pathlib import Path
import asyncio

logf = None

class Logable:
    """
    Classe de base pour disposer d'une méthode log.
    """

    def __init__(self, name, verbose):
        self.name = name
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(f"[{self.name}] {msg}", file=logf, flush=True)


class Accessoire(Logable):
    """Classe mère des accessoires du bar."""

    def __init__(self, name, verbose):
        super().__init__(name, verbose)
        self.file = asyncio.Queue()


class Pic(Accessoire):
    """
    Un pic contient les commandes à fabriquer.
    """

    def __init__(self, name, verbose):
        super().__init__(name, verbose)

    async def embrocher(self, postit):
        """Ajoute un post-it à la file."""

        await self.file.put(postit)

        self.log(
            f"post-it '{postit}' embroché, "
            f"{self.file.qsize()} post-it(s) à traiter"
        )


    async def liberer(self):
        """Attend et récupère le premier post-it disponible."""

        postit = await self.file.get()

        self.log(
            f"post-it '{postit}' libéré, "
            f"{self.file.qsize()} post-it(s) à traiter"
        )

        return postit

class Bar(Accessoire):
    """
    Un bar peut recevoir des commandes,
    en attente d'être servies.
    """

    def __init__(self, name, verbose):
        super().__init__(name, verbose)

    async def recevoir(self, commande):
        """Dépose un plateau sur le bar."""

        await self.file.put(commande)

        self.log(
            f"'{commande}' posée, "
            f"{self.file.qsize()} commande(s) à servir"
        )


    async def evacuer(self):
        """Attend et récupère le premier plateau disponible."""

        commande = await self.file.get()

        self.log(
            f"'{commande}' évacuée, "
            f"{self.file.qsize()} commande(s) à servir"
        )

        return commande


class Clients:

    def __init__(self, fname):
        commandes = []

        start = time.time()
        delai_total = 0
        fmt = re.compile(r"(\d+)\s+(.*)")

        with open(fname, "r", encoding="utf-8") as f:
            for line in f:
                found = fmt.search(line)

                if found:
                    when = int(found.group(1))
                    what = found.group(2)
                    delai_total += when

                    commandes.append(
                        (start + delai_total, what.split(","))
                    )

        self.commandes = commandes[::-1]


    def commande(self):
            if len(self.commandes)>0:
              while True:
                if time.time()>self.commandes[-1][0]:
                    return self.commandes.pop()[1]
            else:
                return None


class Employe(Logable):
    """Classe mère modélisant un employé."""

    def __init__(self, pic, bar, clients, name, verbose):

        super().__init__(name, verbose)

        self.pic = pic
        self.bar = bar
        self.clients = clients

        self.step = 0

        self.log("prêt pour le service")

class Serveur(Employe):

    def __init__(self, pic, bar, clients, name, verbose):
        super().__init__(pic, bar, clients, name, verbose)


    async def prendre_commande(self):
        """Prend une commande et embroche un post-it."""

        self.log("prêt pour prendre une nouvelle commande...")

        commande = self.clients.commande()

        if commande is None:
            return False

        self.log(f"j'ai la commande '{commande}'")
        self.log(f"j'écris sur le post-it '{commande}'")

        await self.pic.embrocher(commande)

        return True

    async def servir(self):
        """Prend un plateau sur le bar et sert les clients."""

        commande = await self.bar.evacuer()

        if commande is not None:

            self.log(f"j'apporte la commande '{commande}'")

            for cocktail in commande:
                self.log(f"je sers '{cocktail}'")


    async def prendre_les_commandes(self):
        """Prend successivement les commandes des clients."""

        while await self.prendre_commande():
            await asyncio.sleep(0)


    async def servir_les_commandes(self):
        """Sert les commandes déposées sur le bar."""

        while not self.bar.file.empty():
            await self.servir()
            await asyncio.sleep(0)


class Bariste(Employe):

    def __init__(self, pic, bar, clients, name, verbose):
        super().__init__(pic, bar, clients, name, verbose)

    async def preparer(self):
        """Prépare une commande et la dépose sur le bar."""

        commande = await self.pic.liberer()

        if commande is None:
            return

        self.log(f"je commence la fabrication de '{commande}'")

        for cocktail in commande:
            self.log(f"je prépare '{cocktail}'")

        self.log(f"la commande {commande} est prête")

        await self.bar.recevoir(commande)

    async def run(self):
        """Bariste en action."""

        while not self.pic.file.empty():
            await self.preparer()
            await asyncio.sleep(0)


def usage():
    print(f"usage: {sys.argv[0]} fichier")
    sys.exit(1)



async def service(alice, bob):
    """Organise les activités concurrentes du bar."""

    await asyncio.gather(
        alice.prendre_les_commandes(),
        bob.run(),
        alice.servir_les_commandes()
    )

def main():

    global logf

    if len(sys.argv) != 2:
        usage()

    fcommandes = sys.argv[1]

    logfile = Path(__file__).resolve().parent / "borabora.log"

    print(f"Logging in {logfile}...")

    logf = open(logfile, "a", encoding="utf-8")

    print("\n---", file=logf, flush=True)

    try:

        les_clients = Clients(fcommandes)

        le_pic = Pic(name="le_pic", verbose=True)
        le_bar = Bar(name="le_bar", verbose=True)

        bob = Bariste(
            le_pic, le_bar, les_clients,
            name="bob", verbose=True
        )

        alice = Serveur(
            le_pic, le_bar, les_clients,
            name="alice", verbose=True
        )

        asyncio.run(service(alice, bob))


    finally:
        logf.close()


if __name__ == "__main__":
    main()

