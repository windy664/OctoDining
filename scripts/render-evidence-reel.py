#!/usr/bin/env python3
"""Render an explicitly labeled screenshot reel from real OctoDining evidence.

This is a promotional edit of captured frames, not a live screen recording.
It uses a small original synthesized instrumental and no third-party song.
Requires ffmpeg and numpy. Generated intermediates stay in .local-state/.
"""

from pathlib import Path
import argparse
import subprocess
import wave

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence"
FONT = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
SCENES = [
    ("next-meal-170-20261005/zh/01-home-recommendation.png",
     "打开，就知道下一餐吃什么。", "原计划优先；没有计划，就给出一道可确认的推荐。", "1.7.0 card-host 实机截图剪辑"),
    ("next-meal-170-20261005/zh/00-first-run-setup.png",
     "饭钱，先留出来。", "生活费扣除必要开销，再估算每天能用于吃饭的钱。", "1.7.0 card-host 实机截图剪辑"),
    ("next-meal-170-20261005/zh/02-candidates.png",
     "每个选择，都有依据。", "真实菜单、标价、营业时段与预算一起呈现。", "1.7.0 card-host 实机截图剪辑"),
    ("next-meal-170-20261005/draft.png",
     "先看清一周，再决定。", "七日草案逐项核对；确认前不会写入餐表。", "1.7.0 card-host 实机截图剪辑"),
    ("next-meal-170-20261005/confirmed.png",
     "确认之后，结果可核验。", "保存并读回餐表；计划不等于订单。", "1.7.0 card-host 实机截图剪辑"),
    ("next-meal-170-20261005/meal-eaten.png",
     "吃过以后，预算继续更新。", "记录实际花费，也如实显示超支。", "1.7.0 card-host 实机截图剪辑"),
    ("shell-170-20261005/restarted.png",
     "在 OctoSense 中继续使用。", "原计划已恢复；模型建议待复验。", "1.7.0 Shell 局部联调画面 · 无模型成功建议"),
]
DURATION = 5
FPS = 30


def run(command):
    subprocess.run(command, check=True)


def soundtrack(path: Path):
    """A quiet, original seven-bar pad and bell motif; no sampled music."""
    rate = 44100
    length = len(SCENES) * DURATION
    audio = np.zeros(rate * length, dtype=np.float32)
    chords = [
        (220.00, 261.63, 329.63, 392.00),
        (174.61, 220.00, 261.63, 349.23),
        (196.00, 246.94, 293.66, 392.00),
        (164.81, 220.00, 261.63, 329.63),
    ]
    for scene in range(len(SCENES)):
        start = scene * DURATION * rate
        t = np.arange(DURATION * rate, dtype=np.float32) / rate
        envelope = np.minimum(1, t / .7) * np.minimum(1, (DURATION - t) / .9)
        for note in chords[scene % len(chords)]:
            audio[start:start + len(t)] += .025 * envelope * np.sin(2 * np.pi * note * t)
        for beat in range(5):
            begin = start + int((beat + .15) * rate)
            if begin >= start + len(t):
                continue
            size = min(int(.8 * rate), start + len(t) - begin)
            pulse = np.arange(size, dtype=np.float32) / rate
            note = chords[scene % len(chords)][(beat + 1) % 4] * 2
            audio[begin:begin + size] += .04 * np.exp(-5 * pulse) * np.sin(2 * np.pi * note * pulse)
    whole = np.arange(len(audio), dtype=np.float32) / rate
    audio *= np.minimum(1, whole / 1.2) * np.minimum(1, (length - whole) / 1.5)
    with wave.open(str(path), "wb") as result:
        result.setnchannels(1)
        result.setsampwidth(2)
        result.setframerate(rate)
        result.writeframes((np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/demo/octodining-170-evidence-reel.mp4")
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    work = ROOT / ".local-state/evidence-reel-build"
    work.mkdir(parents=True, exist_ok=True)
    if not FONT.is_file():
        parser.error(f"Chinese font not found: {FONT}")
    clips = []
    for index, (image, title, detail, footer) in enumerate(SCENES):
        source = EVIDENCE / image
        if not source.is_file():
            parser.error(f"Missing real evidence screenshot: {source}")
        title_file = work / f"title-{index}.txt"
        detail_file = work / f"detail-{index}.txt"
        footer_file = work / f"footer-{index}.txt"
        title_file.write_text(title, encoding="utf-8")
        detail_file.write_text(detail, encoding="utf-8")
        footer_file.write_text(footer, encoding="utf-8")
        clip = work / f"scene-{index:02d}.mp4"
        clips.append(clip)
        shell_frame = index == len(SCENES) - 1
        scale = "960:-1" if shell_frame else "-1:940"
        frame_box = "x=905:y=185:w=1000:h=710" if shell_frame else "x=1190:y=45:w=610:h=990"
        overlay_x = 925 if shell_frame else 1280
        graph = (
            f"[1:v]scale={scale}:flags=lanczos[shot];"
            f"[0:v]drawbox={frame_box}:color=0xe2e9df:t=fill[bg];"
            f"[bg][shot]overlay=x={overlay_x}:y=(H-h)/2:shortest=1,"
            "drawbox=x=120:y=210:w=950:h=3:color=0x81aa47:t=fill,"
            f"drawtext=fontfile={FONT}:textfile={title_file}:fontsize=64:fontcolor=0x203d32:x=120:y=270,"
            f"drawtext=fontfile={FONT}:textfile={detail_file}:fontsize=32:fontcolor=0x53645c:x=120:y=415,"
            f"drawtext=fontfile={FONT}:textfile={footer_file}:fontsize=24:fontcolor=0x73847c:x=120:y=930,"
            f"drawtext=fontfile={FONT}:text=OctoDining:fontsize=34:fontcolor=0x203d32:x=120:y=125,"
            f"fade=t=in:st=0:d=0.25,fade=t=out:st={DURATION - .25}:d=0.25[v]"
        )
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"color=c=0xf8f7f2:s=1920x1080:r={FPS}:d={DURATION}",
            "-loop", "1", "-framerate", str(FPS), "-i", str(source),
            "-filter_complex", graph, "-map", "[v]", "-t", str(DURATION),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-pix_fmt", "yuv420p", str(clip),
        ])
        print(f"Rendered scene {index + 1}/{len(SCENES)}: {title}", flush=True)
    playlist = work / "clips.txt"
    playlist.write_text("".join(f"file '{clip}'\n" for clip in clips), encoding="utf-8")
    wav = work / "original-instrumental.wav"
    soundtrack(wav)
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", str(playlist), "-i", str(wav),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-movflags", "+faststart", str(output),
    ])
    print(f"Wrote {output}; real screenshots edited into a video, not a live recording")


if __name__ == "__main__":
    main()
