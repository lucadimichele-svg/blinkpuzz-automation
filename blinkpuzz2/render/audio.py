"""Offline original score, written one phrase at a time as signed PCM."""

import math
import random
import sys
import wave
from array import array

VOICES = {
    "lab": (146.83, 0.17),
    "ruins": (174.61, 0.36),
    "desk": (130.81, 0.13),
    "workshop": (110, 0.27),
    "editorial": (196, 0.12),
    "arcade": (220, 0.31),
}


def synth(path, story, world, seed):
    rate = 24000
    root, brightness = VOICES[world]
    rng = random.Random(seed)
    scale = [1, 1.25, 1.5, 1.875]
    phrase = rng.sample(scale, len(scale))
    with wave.open(str(path), "wb") as w:
        w.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        cache = {}
        for sec in range(story.duration):
            reveal = sec >= story.solve_seconds
            note = phrase[sec % 4] if not reveal else [1, 1.25, 1.5][sec - story.solve_seconds]
            key = note, sec % 2, reveal
            if key not in cache:
                samples = array("h")
                freq = root * note * (2 if reveal else 1)
                for i in range(rate):
                    t = i / rate
                    angle = math.tau * freq * t
                    env = (
                        min(1, t * 52)
                        * min(1, (1 - t) * 16)
                        * math.exp(-t * (3.6 if reveal else 5.1))
                    )
                    signal = (
                        math.sin(angle)
                        + brightness * math.sin(angle * 2)
                        + 0.13 * math.sin(angle * 3)
                    )
                    if reveal:
                        signal += 0.4 * math.sin(1.5 * angle)
                    samples.append(
                        round(5000 * env * signal * (1 if reveal or sec % 2 == 0 else 0.56))
                    )
                if sys.byteorder != "little":
                    samples.byteswap()
                cache[key] = samples.tobytes()
            w.writeframes(cache[key])
