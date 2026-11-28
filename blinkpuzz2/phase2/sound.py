"""Original modal synthesis. Each set has its own transients, rhythm and resolve."""

import math
import random
import wave
from array import array

RATE = 24000
# Base frequency, interval, damped harmonics, impact noise, decay and pitch sweep.
VOICES = {
    "laser": (590, 1.75, (1, 2.01, 3), 0.025, 0.16, 430),
    "maze": (208, 1.55, (1, 1.49, 2.05), 0.15, 0.24, -48),
    "search": (380, 2.13, (1, 2.85), 0.58, 0.07, -110),
    "mismatch": (260, 1.85, (1, 2, 3, 4), 0.06, 0.22, 15),
    "fit": (133, 1.6, (1, 2.72, 5.13), 0.55, 0.13, -35),
    "pipes": (355, 1.34, (1, 1.8), 0.12, 0.18, 320),
    "gears": (630, 0.81, (1, 3.21, 5.17), 0.65, 0.065, -180),
    "shadow": (282, 2.42, (1, 2.01, 4.16), 0.02, 0.52, 5),
}


def score(path, spec):
    base, interval, partials, noise, decay, sweep = VOICES[spec.family]
    rng = random.Random(spec.puzzle_id)
    duration = spec.solve_seconds + spec.reveal_seconds
    pcm = array("f", [0]) * (duration * RATE)

    def strike(start, freq, gain, length):
        offset = round(start * RATE)
        last = 0.0
        count = min(round(length * 6 * RATE), len(pcm) - offset)
        for i in range(count):
            t = i / RATE
            phase = math.tau * (freq * t + 0.5 * sweep * t * t)
            tone = sum(math.sin(phase * h) / (j + 1) for j, h in enumerate(partials)) / len(
                partials
            )
            last = 0.48 * last + 0.52 * rng.uniform(-1, 1)
            env = min(1, i / 72) * math.exp(-t / length)
            pcm[offset + i] += gain * env * ((1 - noise) * tone + noise * last)

    t = 0.16
    while t < spec.solve_seconds - 0.5:
        strike(t, base * rng.choice((1, 1, 1.25)), 0.22, decay)
        if spec.family in ("search", "maze", "gears"):
            strike(t + 0.14, base * 0.73, 0.12, decay * 0.65)
        t += interval
    for i, pitch in enumerate((1, 1.25, 1.5, 2)):
        strike(spec.solve_seconds + i * 0.72, base * pitch, 0.45, decay * 1.35)
    strike(duration - 0.8, base * 0.5, 0.39, min(0.15, decay))
    samples = array("h", (round(max(-0.92, min(0.92, x)) * 32767) for x in pcm))
    import sys

    if sys.byteorder != "little":
        samples.byteswap()
    with wave.open(str(path), "wb") as out:
        out.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        out.writeframes(samples.tobytes())
