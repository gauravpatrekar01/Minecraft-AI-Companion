import math
import struct
import pygame
import random

# Global state
_sounds = {}
_muted = False
_mixer_initialized = False

def init_sounds():
    """Initializes the pygame mixer and generates retro sound effects."""
    global _mixer_initialized, _sounds
    
    try:
        # Check if already initialized
        if pygame.mixer.get_init():
            _mixer_initialized = True
        else:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
            _mixer_initialized = True
    except Exception as e:
        print(f"Warning: Could not initialize sound mixer ({e}). Companion will run in silent mode.")
        _mixer_initialized = False
        return

    if _mixer_initialized:
        try:
            # Generate sounds
            _sounds["dig"] = _generate_synth(80, 40, 0.15, "noise", volume=0.25)
            _sounds["hit"] = _generate_synth(220, 80, 0.2, "sawtooth", volume=0.35)
            _sounds["eat"] = _generate_eat()
            _sounds["levelup"] = _generate_levelup()
            _sounds["fuse"] = _generate_synth(100, 100, 1.2, "noise", volume=0.2)
            _sounds["explode"] = _generate_synth(60, 30, 0.8, "noise", volume=0.5)
            _sounds["tame"] = _generate_synth(600, 900, 0.3, "sine", volume=0.25)
            _sounds["click"] = _generate_synth(880, 880, 0.05, "square", volume=0.25)
            print("Procedural audio synthesized successfully.")
        except Exception as e:
            print(f"Warning: Failed to synthesize procedural audio ({e}). Running silently.")
            _sounds = {}

def toggle_mute():
    global _muted
    _muted = not _muted
    return _muted

def is_muted():
    return _muted

def play_sound(name):
    """Plays the specified sound if not muted and mixer is initialized."""
    if _muted or not _mixer_initialized or name not in _sounds:
        return
    try:
        _sounds[name].play()
    except Exception:
        pass  # Fail silently if playback encounters issues

def _generate_synth(freq_start, freq_end, duration, wave_type="square", volume=0.3):
    """Generates a mathematical frequency-sweep wave."""
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    buffer = bytearray()
    
    phase = 0.0
    for i in range(num_samples):
        t = i / sample_rate
        freq = freq_start + (freq_end - freq_start) * (t / duration)
        phase += 2.0 * math.pi * freq / sample_rate
        
        if wave_type == "square":
            val = 1.0 if math.sin(phase) > 0 else -1.0
        elif wave_type == "sine":
            val = math.sin(phase)
        elif wave_type == "sawtooth":
            val = 2.0 * (phase / (2.0 * math.pi) - math.floor(phase / (2.0 * math.pi) + 0.5))
        elif wave_type == "noise":
            val = random.uniform(-1.0, 1.0)
        else:
            val = 0.0
            
        # Linear fade out (volume envelope)
        envelope = 1.0 - (t / duration)
        sample = int(val * volume * envelope * 32767)
        buffer.extend(struct.pack('<h', sample))
        
    return pygame.mixer.Sound(buffer=bytes(buffer))

def _generate_eat():
    """Generates a sequential crunching sound."""
    sample_rate = 22050
    buffer = bytearray()
    
    # 3 bites
    for bite in range(3):
        # Noise burst (crunch)
        num_samples = int(sample_rate * 0.07)
        for i in range(num_samples):
            val = random.uniform(-1.0, 1.0)
            sample = int(val * 0.25 * 32767)
            buffer.extend(struct.pack('<h', sample))
            
        # Brief silence
        num_samples_silence = int(sample_rate * 0.04)
        for i in range(num_samples_silence):
            buffer.extend(struct.pack('<h', 0))
            
    return pygame.mixer.Sound(buffer=bytes(buffer))

def _generate_levelup():
    """Generates a standard rising arpeggio."""
    sample_rate = 22050
    notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
    note_dur = 0.12
    buffer = bytearray()
    
    for note in notes:
        num_samples = int(sample_rate * note_dur)
        phase = 0.0
        for i in range(num_samples):
            t = i / sample_rate
            phase += 2.0 * math.pi * note / sample_rate
            val = 1.0 if math.sin(phase) > 0 else -1.0
            # Fade out each note slightly at the end
            envelope = 1.0 if t < note_dur - 0.02 else (note_dur - t) / 0.02
            sample = int(val * 0.2 * envelope * 32767)
            buffer.extend(struct.pack('<h', sample))
            
    return pygame.mixer.Sound(buffer=bytes(buffer))
