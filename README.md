# Synesthesia

Converts WAV audio to PNG images and back, stores sample rate and width so the original sound can be reconstructed



# Audio ↔ Image Converter



A simple Python tool to convert WAV audio files into RGB PNG images and back, preserving sample rate and custom width for accurate reconstruction. Useful for experimentation, visualization, or encoding audio data in images.



## Features



- Convert WAV → PNG with sample rate metadata

- Convert PNG → WAV, restoring original audio

- Supports custom image width for layout control

- Works with mono or stereo WAV files (takes left channel if stereo)



## Requirements



- Python 3.7+

- NumPy

- Pillow

- SciPy



Install dependencies:

```pip install numpy pillow scipy```



