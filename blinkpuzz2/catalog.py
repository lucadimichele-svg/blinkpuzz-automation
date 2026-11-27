from .engines import (
    balance,
    circuit,
    gears,
    laser,
    lock,
    maze,
    nonogram,
    pattern,
    pipes,
    routes,
)

# Adjacent pilots visit different sets, including across the second cycle.
ENGINES = {
    module.ENGINE.key: module.ENGINE
    for module in (laser, maze, lock, pipes, pattern, nonogram, circuit, routes, balance, gears)
}
