"""Encode the edit, then audit the actual decoded film and derive its review stills."""

import hashlib
import io
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

from blinkpuzz2.core import require
from blinkpuzz2.render.media import CHECK_SIZE, checked_image, probe

from .experience import SAFE
from .sound import score

POSE_RATE = 12


def reference(frame):
    return frame.convert("L").resize(CHECK_SIZE, Image.Resampling.BOX)


def still(path, frame):
    frame.save(path, quality=94, subsampling=0, optimize=True)
    checked_image(path, frame)


def jpeg(frame):
    buf = io.BytesIO()
    frame.save(buf, "JPEG", quality=94, subsampling=0)
    return buf.getvalue()


def compare_decoded(video, refs, solve_frames):
    width, height = CHECK_SIZE
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
        f"scale={width}:{height}:flags=area,format=gray",
        "-f",
        "rawvideo",
        "-",
    ]
    worst_mean = worst_local = 0
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
        try:
            for i, ref in enumerate(refs):
                buf = proc.stdout.read(width * height)
                require(len(buf) == width * height, "Missing decoded video frame")
                diff = ImageChops.difference(Image.frombytes("L", CHECK_SIZE, buf), ref)
                mean = ImageStat.Stat(diff).mean[0]
                local = diff.resize((27, 48), Image.Resampling.BOX).getextrema()[1]
                require(
                    mean < 3 and local < 30,
                    f"Frame {i} deviates from authored pose: {mean:.2f}, {local}",
                )
                worst_mean = max(worst_mean, mean)
                worst_local = max(worst_local, local)
            require(not proc.stdout.read(1) and proc.wait() == 0, "Unexpected decoded frame count")
        finally:
            if proc.poll() is None:
                proc.kill()
    return {
        "decoded_frames": len(refs),
        "simultaneous_solve_frames": solve_frames,
        "sample_grid": list(CHECK_SIZE),
        "worst_luma_mae": round(worst_mean, 3),
        "worst_40px_patch_mae": worst_local,
    }


def extract(video, path, time):
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-threads",
            "2",
            "-ss",
            str(time),
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            "-threads",
            "1",
            "-y",
            str(path),
        ],
        check=True,
    )


def render(shot, folder):
    s = shot.s
    cover, cover_type = shot.cover()
    still(folder / "cover.jpg", cover)
    del cover
    duration = s.solve_seconds + s.reveal_seconds
    video = folder / "reel.mp4"
    refs = []
    poses = set()
    solve_crop = shot.static.crop(SAFE)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "sound.wav"
        score(wav, s)
        cmd = [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-threads",
            "1",
            "-f",
            "image2pipe",
            "-framerate",
            str(POSE_RATE),
            "-vcodec",
            "mjpeg",
            "-i",
            "pipe:0",
            "-i",
            str(wav),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-filter_threads",
            "1",
            "-vf",
            "fps=24,scale=in_range=pc:out_range=tv,format=yuv420p",
            "-color_range",
            "tv",
            "-threads",
            "2",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
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
        with subprocess.Popen(cmd, stdin=subprocess.PIPE) as proc:
            try:
                loop = []
                for i in range(POSE_RATE):
                    frame = shot.frame(i / POSE_RATE, False)
                    require(
                        ImageChops.difference(frame.crop(SAFE), solve_crop).getbbox() is None,
                        "Solve evidence changes",
                    )
                    loop.append((jpeg(frame), reference(frame)))
                for _ in range(s.solve_seconds):
                    for data, ref in loop:
                        proc.stdin.write(data)
                        refs.extend([ref] * 2)
                count = s.reveal_seconds * POSE_RATE
                for i in range(count):
                    frame = shot.frame(i / (count - 1), True)
                    ref = reference(frame)
                    poses.add(hashlib.sha256(ref.tobytes()).digest())
                    proc.stdin.write(jpeg(frame))
                    refs.extend([ref] * 2)
                proc.stdin.close()
                require(proc.wait() == 0, "Video encoder failed")
            finally:
                if proc.poll() is None:
                    proc.kill()
    require(len(poses) >= 12, "Insufficient distinct reveal poses")
    info = probe(video, duration)
    info.update(compare_decoded(video, refs, s.solve_seconds * 24))
    for name, time, frame in [
        ("gameplay", 0, shot.frame(0, False)),
        ("reveal", duration - 1 / 24, shot.frame(1, True)),
    ]:
        path = folder / (name + ".jpg")
        extract(video, path, time)
        checked_image(path, frame)
    info.update(
        {
            "distinct_reveal_poses": len(poses),
            "pose_rate": POSE_RATE,
            "cover_type": cover_type,
            "persistent_type": shot.type_audit + shot.fitting_audit,
        }
    )
    return info
