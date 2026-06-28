#!/usr/bin/env python3
"""Generate a looping background music WAV for the Snake game."""
import wave, struct, math, os
import numpy as np

SAMPLE_RATE = 44100
BPM = 140
BEAT = 60.0 / BPM
STEP = BEAT / 4.0  # 16th note duration in seconds
N_STEPS = 32        # melody loop length in 16th notes
N_LOOPS = 8         # total loops in the WAV (~27s)

# G minor pentatonic, 32 steps = 2 bars, loops seamlessly
# (midi_note, duration_in_steps) — None = rest
MELODY = [
    (67, 1), (None, 1), (65, 1), (None, 1),
    (64, 1), (None, 1), (62, 1), (None, 1),
    (60, 1), (None, 1), (58, 1), (None, 1),
    (55, 1), (None, 1), (53, 1), (None, 1),
    (58, 1), (None, 1), (55, 1), (None, 1),
    (53, 1), (None, 1), (52, 1), (None, 1),
    (55, 1), (None, 1), (58, 1), (None, 1),
    (60, 1), (None, 1), (62, 1), (None, 1),
]

def midi_to_hz(n):
    return 440.0 * (2 ** ((n - 69) / 12.0))

def render_note(hz, duration_samples, amp=0.2, attack_s=264, decay_s=2646):
    """Sine-wave note with ADSR envelope using numpy."""
    t = np.arange(duration_samples, dtype=np.float64) / SAMPLE_RATE
    envelope = np.ones(duration_samples)
    envelope[:attack_s] = np.linspace(0, 1, attack_s)
    envelope[attack_s:] *= np.exp(-3.0 * (t[attack_s:] - t[attack_s]))
    return amp * envelope * np.sin(2 * np.pi * hz * t)

# Total output
samples_per_melody_loop = int(STEP * SAMPLE_RATE) * N_STEPS
total_samples = samples_per_melody_loop * N_LOOPS
mix = np.zeros(total_samples, dtype=np.float64)

# Melody layer
step_samples = int(STEP * SAMPLE_RATE)
for loop in range(N_LOOPS):
    offset = loop * samples_per_melody_loop
    for step_idx, (note, _) in enumerate(MELODY):
        if note is not None:
            start = offset + step_idx * step_samples
            nb = render_note(midi_to_hz(note), step_samples)
            mix[start:start + step_samples] += nb * 0.6

# Bass layer (8th notes)
BASS = [
    (55, 2), (None, 2), (58, 2), (None, 2),
    (60, 2), (None, 2), (65, 2), (None, 2),
    (55, 2), (None, 2), (58, 2), (None, 2),
    (60, 2), (62, 2), (65, 2), (None, 2),
]
bass_step = int(BEAT * 0.5 * SAMPLE_RATE)
bass_loop_samples = bass_step * len(BASS)

for loop in range(N_LOOPS):
    offset = loop * bass_loop_samples
    for step_idx, (note, dur) in enumerate(BASS):
        if note is not None:
            note_len = dur * bass_step
            start = offset + step_idx * bass_step
            t = np.arange(note_len, dtype=np.float64) / SAMPLE_RATE
            hz = midi_to_hz(note)
            decay = np.exp(-3.0 * t)
            bass_sig = decay * (
                0.5 * np.sin(2 * np.pi * hz * t)
                + 0.3 * np.sin(2 * np.pi * hz * 0.5 * t)
                + 0.2 * np.sin(2 * np.pi * hz * 2 * t)
            )
            mix[start:start + note_len] += bass_sig * 0.4

# Normalise & write WAV
mix /= max(0.001, np.max(np.abs(mix))) * 1.18
pcm = np.int16(np.clip(mix, -1.0, 1.0) * 32767).tobytes()

wav_path = '/root/workspace/snake/music.wav'
with wave.open(wav_path, 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SAMPLE_RATE)
    w.writeframes(pcm)

size_kb = os.path.getsize(wav_path) / 1024
duration = total_samples / SAMPLE_RATE
print(f"WAV: {wav_path}")
print(f"Size: {size_kb:.1f} KB | Duration: {total_samples / SAMPLE_RATE:.1f}s | Loop: {samples_per_melody_loop / SAMPLE_RATE:.2f}s")
