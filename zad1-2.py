import random


def random_boolean_function(k, parent_names):
    """
    Generuje jedną, stałą funkcję Boolean dla pojedynczego węzła.

    Parametry:
    k : int
        Liczba rodziców węzła.
    parent_names : list[str]
        Nazwy węzłów-rodziców używane do budowy zapisu logicznego.

    Zwraca:
    f : callable
        Funkcja aktualizacji węzła.
    expr : str
        Czytelny zapis logiczny funkcji aktualizacji węzła.
    """
    if k == 0:
        value = random.randint(0, 1)
        return (
            lambda bits, v=value: v,
            str(value)
        )

    ops = [random.choice(["AND", "OR"]) for _ in range(k - 1)]
    negate = random.choice([True, False])

    def f(bits, ops=ops, negate=negate):
        """
        Oblicza wartość funkcji Boolean dla danego wektora stanów rodziców.

        Parametry:
        bits : list[int]
            Aktualne stany rodziców węzła.

        Zwraca:
        int
            Nowy stan węzła.
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
    Generuje losową sieć Boolean.

    Parametry:
    n : int
        Liczba węzłów w sieci.
    max_parents : int
        Maksymalna liczba rodziców jednego węzła.

    Zwraca:
    parents : dict[int, list[int]]
        lista indeksów węzłów-rodziców.
    functions : dict[int, callable]
        funkcja aktualizacji.
    expressions : dict[int, str]
       zapis logiczny funkcji aktualizacji.
    """
    parents = {}
    functions = {}
    expressions = {}

    for i in range(n):
        k = random.randint(0, max_parents)

        # TODO
        # Czy należy wykluczyć samozależności węzłów, ponieważ program BNFinder2 ich nie obsługuje?
        possible = [j for j in range(n)]
        ps = random.sample(possible, k)

        parent_names = [f"X{p}" for p in ps]
        func, expr = random_boolean_function(len(ps), parent_names)

        parents[i] = ps
        functions[i] = func
        expressions[i] = expr

    return parents, functions, expressions


def print_network(parents, expressions):
    """
    Wypisuje strukturę sieci Boolean oraz funkcje aktualizacji węzłów.

    Parametry:
    parents : dict
        Struktura zależności w sieci.
    expressions : dict
        Zapisy logiczne funkcji aktualizacji.
    """
    for i in parents:
        ps = parents[i]
        ps_str = ", ".join(f"X{p}" for p in ps) if ps else "NONE"
        print(f"X{i} <- {ps_str}")
        print(f"   f{i} = {expressions[i]}")


def update_sync(state, parents, functions):
    """
    Wykonuje jeden synchroniczny krok aktualizacji sieci.

    Parametry:
    state : list[int]
        Aktualny stan całej sieci.
    parents : dict
        Struktura zależności między węzłami.
    functions : dict
        Funkcje aktualizacji węzłów.

    Zwraca:
    list[int]
        Nowy stan sieci po aktualizacji synchronicznej.
    """
    new = state[:]
    for i in range(len(state)):
        ps = parents[i]
        if ps:
            bits = [state[p] for p in ps]
            new[i] = functions[i](bits)
    return new


def update_async(state, parents, functions):
    """
    Wykonuje jeden asynchroniczny krok aktualizacji sieci.

    Parametry:
    state : list[int]
        Aktualny stan całej sieci.
    parents : dict
        Struktura zależności między węzłami.
    functions : dict
        Funkcje aktualizacji węzłów.

    Zwraca:
    list[int]
        Nowy stan sieci po aktualizacji jednego losowego węzła.
    """
    new = state[:]
    i = random.randrange(len(state))
    ps = parents[i]
    if ps:
        bits = [state[p] for p in ps]
        new[i] = functions[i](bits)
    return new


def simulate_sync(network, steps):
    """
    Symuluje dynamikę synchroniczną sieci Boolean.

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
    n = len(parents)
    state = [random.randint(0, 1) for _ in range(n)]
    traj = [state[:]]

    for _ in range(steps):
        state = update_sync(state, parents, functions)
        traj.append(state[:])

    return traj


def simulate_async(network, steps):
    """
    Symuluje dynamikę asynchroniczną sieci Boolean.

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
    n = len(parents)
    state = [random.randint(0, 1) for _ in range(n)]
    traj = [state[:]]

    for _ in range(steps):
        state = update_async(state, parents, functions)
        traj.append(state[:])

    return traj


def compute_proportions(traj):
    """
    Oblicza proporcję stanów przejściowych i atraktorowych w trajektorii.

    Parametry:
    traj : list[list[int]]
        Trajektoria stanów sieci.

    Zwraca:
    (float, float)
        Udział stanów przejściowych oraz atraktorowych.
    """
    seen = {}
    for t, state in enumerate(traj):
        key = tuple(state)
        if key in seen:
            transient = seen[key]
            attractor = len(traj) - seen[key]
            total = len(traj)
            return transient / total, attractor / total
        seen[key] = t

    return 1.0, 0.0


def save_bnf(filename, traj):
    """
    Zapisuje trajektorię do pliku w formacie zgodnym z BNFinder2.

    Parametry:
    filename : str
        Nazwa pliku wyjściowego.
    traj : list[list[int]]
        Trajektoria stanów sieci.
    """
    genes = len(traj[0])
    steps = len(traj)

    with open(filename, "w") as f:
        f.write("Gene")
        for t in range(steps):
            f.write(f"\tS{t}")
        f.write("\n")

        for g in range(genes):
            f.write(f"X{g}")
            for t in range(steps):
                f.write(f"\t{traj[t][g]}")
            f.write("\n")

    print("saved:", filename)


def run_experiment(name, nodes, steps, sample_every):
    """
    Generuje sieć Boolean, symuluje jej dynamikę
    oraz zapisuje dane przy unikalnych proporcjach atraktorów.

    Parametry:
    name : str
        Nazwa eksperymentu.
    nodes : int
        Liczba węzłów sieci.
    steps : int
        Liczba kroków symulacji.
    sample_every : int
        Częstotliwość próbkowania trajektorii.
    """
    attempt = 0

    while True:
        attempt += 1
        network = generate_network(nodes)
        parents, _, expressions = network

        # TODO
        # Czy trajektorie powinny być liczone dla jednego stanu początkowego, czy dla wielu lub wszystkich możliwych?
        sync = simulate_sync(network, steps)[::sample_every]
        async_traj = simulate_async(network, steps)[::sample_every]

        # TODO
        # Czy sprawdzać proporcjach stanów przejściowych i atraktorowych pomiędzy trajektoriami?
        p_sync = compute_proportions(sync)
        p_async = compute_proportions(async_traj)

        key = (round(p_sync[1], 3), round(p_async[1], 3))

        if key not in used_props:
            used_props.add(key)

            print(f"\nBOOLEAN NETWORK {name}")
            print_network(parents, expressions)
            print("\n")

            save_bnf(f"{name}_sync.data", sync)
            save_bnf(f"{name}_async.data", async_traj)

            print(f"{name} accepted after {attempt} attempts")
            print(f"sync  transient/attractor = {p_sync}")
            print(f"async transient/attractor = {p_async}")
            print("\n===========")
            break


if __name__ == "__main__":
    used_props = set()

    run_experiment("BN1", nodes=6,  steps=100, sample_every=1)
    run_experiment("BN2", nodes=10, steps=120, sample_every=3)
    run_experiment("BN3", nodes=14, steps=60,  sample_every=2)
