import json
import subprocess
from array import array

from PIL import Image, ImageChops, ImageStat

from blinkpuzz2.core import require

from .audio import synth
from .frames import background, scene

FPS = 24
CHECK_SIZE = (135, 240)


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def compose(spec, world, story, backplate=None):
    bg = background(spec, world) if backplate is None else backplate
    cover, cover_audit = scene(spec, world, bg, "cover")
    sequence = [(*scene(spec, world, bg), story.solve_seconds)]
    for i in range(story.reveal_seconds):
        sequence.append((*scene(spec, world, bg, "proof", (i + 1) / story.reveal_seconds), 1))
    return cover, cover_audit, sequence


def encode(tmp, video, spec, world, story, sequence):
    concat = []
    for i, (im, audit, seconds) in enumerate(sequence):
        name = f"plate-{i}.png"
        im.save(tmp / name, compress_level=1)
        concat.extend([f"file '{name}'", f"duration {seconds}"])
    concat.append(f"file '{name}'")
    (tmp / "frames.txt").write_text("\n".join(concat) + "\n")
    synth(tmp / "score.wav", story, world, spec.seed)
    # The moving playhead is below the puzzle and rule surfaces in every set.
    width = 610
    filters = (
        f"[0:v]fps={FPS},drawbox=x=235:y=1611:w={width}:h=5:color=black@0.45:t=fill[plate];"
        f"[plate][2:v]overlay=x='235+{width}*min(t/{story.solve_seconds},1)':y=1607"
        f":enable='lt(t,{story.solve_seconds})'[v]"
    )
    run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-filter_complex_threads",
            "1",
            "-f",
            "concat",
            "-safe",
            "1",
            "-i",
            str(tmp / "frames.txt"),
            "-i",
            str(tmp / "score.wav"),
            "-f",
            "lavfi",
            "-i",
            "color=c=0xeac88d:s=14x12:r=24",
            "-filter_complex",
            filters,
            "-map",
            "[v]",
            "-map",
            "1:a:0",
            "-t",
            str(story.duration),
            "-threads",
            "2",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-tune",
            "stillimage",
            "-crf",
            "21",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            "-map_metadata",
            "-1",
            str(video),
        ]
    )


def probe(path, seconds):
    raw = json.loads(
        run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
            stdout=subprocess.PIPE,
        ).stdout
    )
    require(len(raw["streams"]) == 2, "Expected one video and one audio track")
    video, audio = raw["streams"]
    require(
        (video["codec_name"], video["width"], video["height"], video["pix_fmt"])
        == ("h264", 1080, 1920, "yuv420p")
        and audio["codec_name"] == "aac",
        "Invalid codecs or geometry",
    )
    require(
        video["avg_frame_rate"] == "24/1" and int(video["nb_frames"]) == seconds * FPS,
        "Frame count mismatch",
    )
    require(
        all(abs(float(s["duration"]) - seconds) < 0.06 for s in [video, audio, raw["format"]]),
        "Duration mismatch",
    )
    pcm = array("h")
    pcm.frombytes(
        run(
            [
                "ffmpeg",
                "-nostdin",
                "-v",
                "error",
                "-i",
                str(path),
                "-map",
                "0:a",
                "-ar",
                "8000",
                "-ac",
                "1",
                "-f",
                "s16le",
                "-",
            ],
            stdout=subprocess.PIPE,
        ).stdout
    )
    rms = round((sum(x * x for x in pcm) / len(pcm)) ** 0.5, 2)
    require(rms > 100 and max(abs(x) for x in pcm) < 32767, "Silent or clipped audio")
    return {
        "video": {
            k: video[k]
            for k in (
                "codec_name",
                "width",
                "height",
                "pix_fmt",
                "avg_frame_rate",
                "nb_frames",
                "duration",
            )
        },
        "audio": {k: audio[k] for k in ("codec_name", "sample_rate", "channels", "duration")},
        "duration": raw["format"]["duration"],
        "decoded_pcm_rms": rms,
    }


def checked_image(path, expected):
    with Image.open(path) as im:
        im.load()
        require(im.size == (1080, 1920) and im.format == "JPEG", "Invalid JPEG still")
        delta = ImageChops.difference(
            im.convert("RGB").resize(CHECK_SIZE), expected.resize(CHECK_SIZE)
        )
        require(
            max(ImageStat.Stat(delta).mean) < 3, "Still does not match the intended composition"
        )


def frame_check(video, sequence):
    # Compare every delivered frame against its independently recomposited phase.
    # Downsampling retains geometry and text lines. The narrow moving playhead is excluded.
    refs = []
    for im, audit, seconds in sequence:
        refs.extend([im.convert("L").resize(CHECK_SIZE, Image.Resampling.BOX)] * int(seconds * FPS))
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-v",
        "error",
        "-threads",
        "2",
        "-i",
        str(video),
        "-an",
        "-filter_threads",
        "1",
        "-vf",
        "scale=135:240:flags=area,format=gray",
        "-f",
        "rawvideo",
        "-",
    ]
    size = CHECK_SIZE[0] * CHECK_SIZE[1]
    worst_mean = worst_patch = 0
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
        try:
            for i, ref in enumerate(refs):
                buf = proc.stdout.read(size)
                require(len(buf) == size, "Missing decoded frame")
                delta = ImageChops.difference(Image.frombytes("L", CHECK_SIZE, buf), ref)
                delta.paste(0, (27, 199, 110, 204))
                mean = ImageStat.Stat(delta).mean[0]
                patch = delta.resize((27, 48), Image.Resampling.BOX).getextrema()[1]
                require(
                    mean < 3 and patch < 30,
                    f"Frame {i} differs from intended clues ({mean:.2f}/{patch})",
                )
                worst_mean, worst_patch = max(worst_mean, mean), max(worst_patch, patch)
            require(not proc.stdout.read(1) and proc.wait() == 0, "Extra or unreadable frames")
        finally:
            if proc.poll() is None:
                proc.kill()
    return {
        "frames_compared": len(refs),
        "largest_mean_error": round(worst_mean, 3),
        "largest_local_mean_error": worst_patch,
        "sample_grid": list(CHECK_SIZE),
    }
