import random
import os


def random_boolean_function(k, parent_names):
    """
    Generuje losową funkcję Boolean przypisaną do pojedynczego węzła sieci.

    Dla k = 0 tworzona jest funkcja stała (0 lub 1).
    Dla k > 0 funkcja jest losową kombinacją operatorów AND / OR
    pomiędzy stanami rodziców, z opcjonalną negacją całego wyrażenia.

    Parametry:
    k : int
        Liczba rodziców węzła.
    parent_names : list[str]
        Nazwy węzłów-rodziców używane do zapisu logicznego funkcji.

    Zwraca:
    f : callable
        Funkcja aktualizacji węzła, przyjmująca listę stanów rodziców.
    expr : str
        Czytelny zapis logiczny funkcji aktualizacji.
    """
    if k == 0:
        value = random.randint(0, 1)
        return (
            lambda bits, v=value: v,
            str(value)
        )

    ops = [random.choice(["AND", "OR"]) for _ in range(k - 1)]
    negate = random.choice([True, False])

    def f(bits):
        """
        Oblicza nowy stan węzła na podstawie aktualnych stanów jego rodziców.

        Parametry:
        bits : list[int]
            Aktualne stany węzłów-rodziców (0 lub 1).

        Zwraca:
        int
            Nowy stan węzła (0 lub 1).
        """
        out = bits[0]
        for b, op in zip(bits[1:], ops):
            if op == "AND":
                out = out and b
            else:
                out = out or b
        if negate:
            out = not out
        return int(out)

    expr = parent_names[0]
    for name, op in zip(parent_names[1:], ops):
        expr = f"({expr} ∧ {name})" if op == "AND" else f"({expr} ∨ {name})"
    if negate:
        expr = f"¬{expr}"

    return f, expr


def generate_network(n, max_parents=3):
    """
    Generuje losową sieć Boolean o zadanej liczbie węzłów.

    Każdy węzeł:
    - ma losową liczbę rodziców (od 0 do max_parents),
    - nie posiada samozależności (Xi nie zależy od Xi),
    - otrzymuje losową funkcję Boolean.

    Parametry:
    n : int
        Liczba węzłów w sieci.
    max_parents : int
        Maksymalna liczba rodziców jednego węzła.

    Zwraca:
    parents : dict[int, list[int]]
        Struktura zależności – lista rodziców dla każdego węzła.
    functions : dict[int, callable]
        Funkcje aktualizacji przypisane do węzłów.
    expressions : dict[int, str]
        Zapisy logiczne funkcji aktualizacji.
    """
    parents = {}
    functions = {}
    expressions = {}

    for i in range(n):
        possible = [j for j in range(n) if j != i]
        k = random.randint(1, min(max_parents, len(possible)))
        ps = random.sample(possible, k)

        func, expr = random_boolean_function(len(ps), [f"X{p}" for p in ps])

        parents[i] = ps
        functions[i] = func
        expressions[i] = expr

    return parents, functions, expressions


def print_network(parents, expressions):
    """
    Wypisuje strukturę sieci Boolean w postaci listy zależności
    oraz odpowiadające im funkcje aktualizacji.

    Parametry:
    parents : dict[int, list[int]]
        Struktura zależności w sieci.
    expressions : dict[int, str]
        Zapisy logiczne funkcji aktualizacji.
    """
    for i in parents:
        ps = parents[i]
        ps_str = ", ".join(f"X{p}" for p in ps) if ps else "NONE"
        print(f"X{i} <- {ps_str}")
        print(f"   f{i} = {expressions[i]}")


def update_sync(state, parents, functions):
    """
    Wykonuje jeden synchroniczny krok aktualizacji sieci Boolean.

    Wszystkie węzły są aktualizowane jednocześnie
    na podstawie stanu z poprzedniego kroku.

    Parametry:
    state : list[int]
        Aktualny stan całej sieci.
    parents : dict[int, list[int]]
        Struktura zależności w sieci.
    functions : dict[int, callable]
        Funkcje aktualizacji węzłów.

    Zwraca:
    list[int]
        Nowy stan sieci po aktualizacji synchronicznej.
    """
    new = state[:]
    for i in range(len(state)):
        if parents[i]:
            bits = [state[p] for p in parents[i]]
            new[i] = functions[i](bits)
    return new


def update_async(state, parents, functions):
    """
    Wykonuje jeden asynchroniczny krok aktualizacji sieci Boolean.

    W jednym kroku losowo wybierany jest jeden węzeł,
    którego stan zostaje zaktualizowany.

    Parametry:
    state : list[int]
        Aktualny stan całej sieci.
    parents : dict[int, list[int]]
        Struktura zależności w sieci.
    functions : dict[int, callable]
        Funkcje aktualizacji węzłów.

    Zwraca:
    list[int]
        Nowy stan sieci po aktualizacji jednego węzła.
    """
    new = state[:]
    i = random.randrange(len(state))
    if parents[i]:
        bits = [state[p] for p in parents[i]]
        new[i] = functions[i](bits)
    return new


def simulate_sync(network, steps):
    """
    Symuluje jedną trajektorię synchroniczną sieci Boolean.

    Trajektoria startuje z losowego stanu początkowego
    i rozwija się zgodnie z synchroniczną dynamiką sieci.

    Parametry:
    network : tuple
        Struktura sieci (parents, functions, expressions).
    steps : int
        Liczba kroków symulacji.

    Zwraca:
    list[list[int]]
        Trajektoria stanów sieci w czasie.
    """
    parents, functions, _ = network
    state = [random.randint(0, 1) for _ in parents]
    traj = [state[:]]

    for _ in range(steps):
        state = update_sync(state, parents, functions)
        traj.append(state[:])

    return traj


def simulate_async(network, steps):
    """
    Symuluje jedną trajektorię asynchroniczną sieci Boolean.

    Trajektoria startuje z losowego stanu początkowego
    i w każdym kroku aktualizowany jest jeden losowy węzeł.

    Parametry:
    network : tuple
        Struktura sieci (parents, functions, expressions).
    steps : int
        Liczba kroków symulacji.

    Zwraca:
    list[list[int]]
        Trajektoria stanów sieci w czasie.
    """
    parents, functions, _ = network
    state = [random.randint(0, 1) for _ in parents]
    traj = [state[:]]

    for _ in range(steps):
        state = update_async(state, parents, functions)
        traj.append(state[:])

    return traj


def save_bnf(filename, dataset):
    """
    Zapisuje zestaw trajektorii do pliku w formacie kompatybilnym
    z programem BNFinder2 w katalogu BN-data/.

    Parametry:
    filename : str
        Nazwa pliku (bez ścieżki).
    dataset : list[list[list[int]]]
        Zestaw trajektorii sieci Boolean.
    """
    genes = len(dataset[0][0])
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w") as f:
        for traj in dataset:
            f.write("Gene")
            for t in range(len(traj)):
                f.write(f"\tS{t}")
            f.write("\n")

            for g in range(genes):
                f.write(f"X{g}")
                for state in traj:
                    f.write(f"\t{state[g]}")
                f.write("\n")

            f.write("\n")

    print("saved:", path)


def run_trajektorie(network, nodes, steps, sample_every, n_traj):
    """
    Generuje i zapisuje zestaw trajektorii dla JEDNEJ konfiguracji
    parametrów trajektorii.

    Parametry:
    network : tuple
        Sieć Boolean.
    nodes : int
        Liczba węzłów (do nazwy pliku).
    steps : int
        Długość trajektorii.
    sample_every : int
        Częstotliwość próbkowania.
    n_traj : int
        Liczba trajektorii.
    """
    sync_data = []
    async_data = []

    for _ in range(n_traj):
        sync = simulate_sync(network, steps)[::sample_every]
        async_traj = simulate_async(network, steps)[::sample_every]
        sync_data.append(sync)
        async_data.append(async_traj)

    save_bnf(f"nodes{nodes}_steps{steps}_sample{sample_every}_ntraj{n_traj}_sync.data", sync_data)
    
    save_bnf(f"nodes{nodes}_steps{steps}_sample{sample_every}_ntraj{n_traj}_async.data", async_data)


def run_experiment(nodes, steps, sample_every, n_traj):
    """
    Przeprowadza eksperyment OFAT (one-factor-at-a-time).

    Dla każdej liczby węzłów:
    - generowana jest jedna sieć Boolean,
    - tworzonych jest kilka zestawów danych,
      z których każdy różni się TYLKO JEDNYM parametrem trajektorii.

    Parametry:
    nodes : list[int]
    steps : list[int]
    sample_every : list[int]
    n_traj : list[int]
    """
    for n in nodes:
        network = generate_network(n)
        parents, _, expressions = network

        print(f"\nBOOLEAN NETWORK (nodes = {n})")
        for i in parents:
            ps = ", ".join(f"X{p}" for p in parents[i]) if parents[i] else "NONE"
            print(f"X{i} <- {ps}")
            print(f"   f{i} = {expressions[i]}")
        print("")

        # zmieniamy TYLKO liczbę kroków
        for s in steps:
            run_trajektorie(network, n, s, sample_every[0], n_traj[0])

        # zmieniamy TYLKO próbkowanie
        for samp in sample_every:
            run_trajektorie(network, n, steps[0], samp, n_traj[0])

        # zmieniamy TYLKO liczbę trajektorii
        for nt in n_traj:
            run_trajektorie(network, n, steps[0], sample_every[0], nt)

        print("\n======================")
        
if __name__ == "__main__":
    OUTPUT_DIR = "BN_data"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    run_experiment( nodes=[8,15], steps=[20,30], sample_every=[1,2], n_traj=[10,20])

