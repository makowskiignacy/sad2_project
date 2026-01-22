from pyboolnet.trap_spaces import compute_trap_spaces
from pyboolnet.repository import bnet2primes
import random
import os
import re


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
        return lambda bits, v=value: v, str(value)

    # losowe operatory między argumentami
    ops = [random.choice(["AND", "OR"]) for _ in range(k - 1)]

    # losowa negacja KAŻDEGO rodzica
    neg_args = [random.choice([True, False]) for _ in range(k)]

    # opcjonalna negacja całego wyrażenia
    negate_whole = random.choice([True, False])

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
        vals = [(not b if neg else b) for b, neg in zip(bits, neg_args)]

        out = vals[0]
        for b, op in zip(bits[1:], ops):
            if op == "AND":
                out = out and b
            else:
                out = out or b

        if negate_whole:
            out = not out
            
        return int(out)

    def arg_expr(name, neg):
        return f"¬{name}" if neg else name

    expr = arg_expr(parent_names[0], neg_args[0])

    for name, neg, op in zip(parent_names[1:], neg_args[1:], ops):
        right = arg_expr(name, neg)
        expr = f"({expr} ∧ {right})" if op == "AND" else f"({expr} ∨ {right})"

    if negate_whole:
        expr = f"¬({expr})"

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
        line1 = f"X{i} <- {ps_str}"
        print(line1)
        REPORT.write(line1 + "\n")

        line2 = f"   f{i} = {expressions[i]}"
        print(line2)
        REPORT.write(line2 + "\n")

def convert_to_pyboolnet(expressions):
    """
    Konwertuje funkcje aktualizacji sieci boolowskiej z wewnętrznej
    reprezentacji symbolicznej do formatu .bnet akceptowanego
    przez bibliotekę PyBoolNet.

    Parametry:
    expressions : dict[int, str]
        Słownik mapujący indeks węzła na wyrażenie logiczne.

    Zwraca:
    str
        Tekstowa reprezentacja sieci w formacie .bnet.
    """
    result = []

    for idx in sorted(expressions):
        expr = expressions[idx]

        # operatory logiczne
        expr = expr.replace("∧", "&").replace("∨", "|").replace("¬", "!")

        # Xi → vi
        expr = re.sub(r"X(\d+)", r"v\1", expr)

        result.append(f"v{idx},   {expr}")

    return "\n".join(result)



def find_sync_attractors(network):
    """
    Identyfikuje atraktory synchroniczne sieci boolowskiej.
    Atraktory synchroniczne (punkty stałe i cykle) są wyznaczane
    poprzez pełne przejście deterministycznego grafu stanów,
    co jest równoważne definicji atraktora w dynamice synchronicznej.

    Parametry
    network : tuple
        Krotka (parents, functions, expressions) opisująca sieć.


    Zwraca
    list[set[tuple[int]]]
        Lista atraktorów, z których każdy jest zbiorem stanów.
    """
    parents, functions, _ = network
    n = len(parents)

    visited = {}
    attractors = []

    for mask in range(2 ** n):
        state = [(mask >> i) & 1 for i in range(n)]
        path = []

        while tuple(state) not in visited:
            visited[tuple(state)] = len(path)
            path.append(tuple(state))
            state = update_sync(state, parents, functions)

        start = visited[tuple(state)]
        cycle = set(path[start:])
        if cycle not in attractors:
            attractors.append(cycle)

    return attractors


def find_async_attractors(expressions):
    """
    Identyfikuje atraktory asynchroniczne sieci boolowskiej.
    Atraktory asynchroniczne są definiowane jako minimalne trap spaces
    w grafie przejść asynchronicznych i wyznaczane przy użyciu PyBoolNet.

    Parametry
    expressions : dict[int, str]
        Zapisy logiczne funkcji aktualizacji.

    Zwraca
    list[set[tuple[int]]]
        Lista atraktorów asynchronicznych reprezentowanych jako zbiory stanów.
    """
    bnet = convert_to_pyboolnet(expressions)
    primes = bnet2primes(bnet)
    n = len(expressions)

    attractors = []
    trap_spaces = compute_trap_spaces(primes, "min")

    for ts in trap_spaces:
        fixed = {int(k[1:]): int(v) for k, v in ts.items() if v in (0, 1)}
        free = [i for i in range(n) if i not in fixed]

        states = set()
        for mask in range(2 ** len(free)):
            state = fixed.copy()
            for i, b in zip(free, format(mask, f"0{len(free)}b")):
                state[i] = int(b)
            states.add(tuple(state[i] for i in range(n)))

        attractors.append(states)

    return attractors


def compute_proportions(traj, attractors):
    """
    Oblicza proporcję stanów przejściowych (transient)
    oraz atraktorowych w trajektorii.

    Parametry:
    traj : list[list[int]]
        Jedna trajektoria sieci boolowskiej.
    attractors : list[set[tuple[int]]]
        Lista atraktorów (każdy jako zbiór stanów).

    Zwraca:
    tuple(float, float)
        (proportion_transient, proportion_attractor)
    """
    if not attractors:
        return 1.0, 0.0

    attractor_states = set().union(*attractors)
    total = len(traj)
    a = sum(tuple(state) in attractor_states for state in traj)

    return 1.0 - a / total, a / total

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
    Generuje trajektorie synchroniczne i asynchroniczne dla JEDNEJ
    konfiguracji parametrów, zapisuje je do plików BNFinder2
    ORAZ oblicza proporcje stanów transient / attractor
    na podstawie atraktorów wykrytych przez PyBoolNet.


    Parametry:
    network : tuple
        (parents, functions, expressions)
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

    parents, _, expressions = network

    # znajdź atraktory dla tej sieci
    sync_attr = find_sync_attractors(network)
    async_attr = find_async_attractors(expressions)

    header = f"[Attractors | nodes={nodes}, steps={steps}, sample={sample_every}, ntraj={n_traj}]"
    print("\n" + header)
    REPORT.write("\n"+header + "\n")

    line = f"  sync  attractors : {len(sync_attr)}"
    print(line)
    REPORT.write(line + "\n")

    line = f"  async attractors : {len(async_attr)}"
    print(line)
    REPORT.write(line + "\n")

    for i in range(n_traj):
        sync_traj = simulate_sync(network, (steps-1)*sample_every)[::sample_every]
        async_traj = simulate_async(network, (steps-1)*sample_every)[::sample_every]

        sync_data.append(sync_traj)
        async_data.append(async_traj)

        p_sync = compute_proportions(sync_traj, sync_attr)
        p_async = compute_proportions(async_traj, async_attr)

        line = f"  traj {i + 1:02d} | sync={p_sync[0]:.3f}, {p_sync[1]:.3f}) | async={p_async[0]:.3f}, {p_async[1]:.3f})"
        print(line)
        REPORT.write(line + "\n")

    save_bnf(f"nodes{nodes}_steps{steps}_sample{sample_every}_ntraj{n_traj}_sync.data", sync_data)

    save_bnf(f"nodes{nodes}_steps{steps}_sample{sample_every}_ntraj{n_traj}_async.data", async_data)


def run_experiment(nodes, steps, sample_every, n_traj):
    """
    Dla każdej liczby węzłów generowana jest jedna sieć boolowska,
    a następnie tworzone są zestawy danych różniące się pojedynczym
    parametrem (długość trajektorii, częstość próbkowania lub liczba
    trajektorii).

    Parametry:
    nodes : list[int]
        Lista rozmiarów sieci.
    steps : list[int]
        Lista długości trajektorii.
    sample_every : list[int]
        Lista częstości próbkowania.
    n_traj : list[int]
        Lista liczby trajektorii.
    """
    for n in nodes:
        network = generate_network(n)
        parents, _, expressions = network

        title = f"BOOLEAN NETWORK (nodes = {n})"
        print("\n" + title)
        REPORT.write(title + "\n\n")

        print_network(parents, expressions)


        # zmieniamy TYLKO liczbę kroków
        for s in steps:
            run_trajektorie(network, n, s, sample_every[0], n_traj[1])

        # zmieniamy TYLKO próbkowanie
        for samp in sample_every:
            run_trajektorie(network, n, steps[1], samp, n_traj[1])

        # zmieniamy TYLKO liczbę trajektorii
        for nt in n_traj:
            run_trajektorie(network, n, steps[1], sample_every[0], nt)

        print("\n======================")
        REPORT.write("\n======================\n\n")


if __name__ == "__main__":

    OUTPUT_DIR = "BN_data"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    REPORT = open("report.txt", "w", encoding="utf-8")
    run_experiment( nodes=[5,8,16], steps=[10,20,30], sample_every=[1,2,3], n_traj=[16,32,64])

