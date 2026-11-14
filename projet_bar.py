import sys
import time
import re
from pathlib import Path
import asyncio

logf = None

class Logable:

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

    def __init__(self, name, verbose):
        super().__init__(name, verbose)

    async def embrocher(self, postit):

        await self.file.put(postit)

        self.log(
            f"post-it '{postit}' embroché, "
            f"{self.file.qsize()} post-it(s) à traiter"
        )


    async def liberer(self):

        postit = await self.file.get()

        if postit is None:
            self.log("fin des commandes à préparer")
            return None

        self.log(
            f"post-it '{postit}' libéré, "
            f"{self.file.qsize()} élément(s) en attente"
        )

        return postit

class Bar(Accessoire):

    def __init__(self, name, verbose):
        super().__init__(name, verbose)

    async def recevoir(self, commande):

        await self.file.put(commande)

        self.log(
            f"'{commande}' posée, "
            f"{self.file.qsize()} commande(s) à servir"
        )


    async def evacuer(self):

        commande = await self.file.get()

        if commande is None:
            self.log("signal de fin de service reçu")
            return None

        self.log(
            f"'{commande}' évacuée, "
            f"{self.file.qsize()} élément(s) en attente"
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
        self.verrou = asyncio.Lock()


    def commande(self):
            if len(self.commandes)>0:
              while True:
                if time.time()>self.commandes[-1][0]:
                    return self.commandes.pop()[1]
            else:
                return None

    async def commande_async(self):

        while True:
            async with self.verrou:
                if not self.commandes:
                    return None

                instant = self.commandes[-1][0]
                attente = instant - time.time()

                if attente <= 0:
                    return self.commandes.pop()[1]

            await asyncio.sleep(attente)

    async def commande_si_disponible(self):

        async with self.verrou:
            if self.commandes and self.commandes[-1][0] <= time.time():
                return self.commandes.pop()[1]

        return None

class Employe(Logable):

    def __init__(self, pic, bar, clients, name, verbose, productivite):

        super().__init__(name, verbose)

        self.pic = pic
        self.bar = bar
        self.clients = clients

        self.step = 0
        self.verrou = asyncio.Lock()

        self.productivite = productivite

        self.log("prêt pour le service")

class Serveur(Employe):

    def __init__(self, pic, bar, clients, name, verbose, productivite):
        super().__init__(pic, bar, clients, name, verbose, productivite)


    async def servir(self):

        commande = await self.bar.evacuer()

        if commande is None:
            return False

        async with self.verrou:
            self.log(f"j'apporte la commande '{commande}'")

            for cocktail in commande:
                self.log(f"je sers '{cocktail}'")

                await asyncio.sleep(self.productivite)

        return True


    async def prendre_commande(self):

        self.log("prêt pour prendre une nouvelle commande...")

        commande = await self.clients.commande_async()

        if commande is None:
            return False

        async with self.verrou:

            self.log(f"j'ai la commande '{commande}'")

            await asyncio.sleep(self.productivite)

            self.log(f"j'écris sur le post-it '{commande}'")

            await self.pic.embrocher(commande)

        return True


    async def prendre_les_commandes(self):

        while await self.prendre_commande():
            await asyncio.sleep(0)

    async def servir_les_commandes(self):

        while True:
            commande_servie = await self.servir()

            if not commande_servie:
                break

            await asyncio.sleep(0)


class Bariste(Employe):

    def __init__(self, pic, bar, clients, name, verbose, productivite):
        super().__init__(pic, bar, clients, name, verbose, productivite)

    async def preparer_commande(self, commande):

        self.log(f"je commence la fabrication de '{commande}'")

        for cocktail in commande:
            self.log(f"je prépare '{cocktail}'")
            await asyncio.sleep(self.productivite)

        self.log(f"la commande {commande} est prête")
        await self.bar.recevoir(commande)

    async def servir_directement(self, commande):

        self.log(f"je prends directement la commande '{commande}'")

        for cocktail in commande:
            self.log(f"je prépare directement '{cocktail}'")
            await asyncio.sleep(self.productivite)

        for cocktail in commande:
            self.log(f"je sers directement '{cocktail}'")
            await asyncio.sleep(self.productivite)


    async def run(self, prises_terminees):

        while True:

            if not self.pic.file.empty():
                commande = await self.pic.liberer()

                if commande is None:
                    break

                await self.preparer_commande(commande)
                continue

            commande = await self.clients.commande_si_disponible()

            if commande is not None:
                await self.servir_directement(commande)
                continue

            if prises_terminees.is_set():
                break

            await asyncio.sleep(0.05)


def usage():
    print(f"usage: {sys.argv[0]} fichier")
    sys.exit(1)



async def service(alice, bob, joeffrey):

    prises_terminees = asyncio.Event()

    preparation = asyncio.create_task(bob.run(prises_terminees))

    services = [
        asyncio.create_task(alice.servir_les_commandes()),
        asyncio.create_task(joeffrey.servir_les_commandes())
    ]

    await asyncio.gather(
        alice.prendre_les_commandes(),
        joeffrey.prendre_les_commandes()
    )

    prises_terminees.set()

    await preparation

    await alice.bar.file.put(None)
    await joeffrey.bar.file.put(None)

    await asyncio.gather(*services)


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
            name="bob",
            verbose=True,
            productivite=0.8
        )

        alice = Serveur(
            le_pic, le_bar, les_clients,
            name="alice",
            verbose=True,
            productivite=0.2
        )

        joeffrey = Serveur(
            le_pic, le_bar, les_clients,
            name="joeffrey",
            verbose=True,
            productivite=0.5
        )
        asyncio.run(service(alice, bob, joeffrey))


    finally:
        logf.close()


if __name__ == "__main__":
    main()

