# Subtitle Translator & Video Subtitle Embedder

## Overview

This project provides an automated pipeline for translating subtitles from Russian to Kazakh using DeepSeek API and embedding the translated subtitles into a video using FFmpeg.

## Features

- **Automatic Subtitle Translation**: Converts Russian `.vtt` subtitles to Kazakh while preserving timestamps.
- **Encoding Detection**: Automatically detects and handles different text encodings.
- **Batch Processing**: Efficient translation of subtitles in batches to optimize API calls.
- **Embedding Subtitles**: Uses FFmpeg to overlay subtitles onto a video.

## Prerequisites

Ensure you have the following installed:

1. **Python 3.8+**
2. **FFmpeg** (Required for adding subtitles to videos)
   - Install on macOS: `brew install ffmpeg`
   - Install on Ubuntu: `sudo apt install ffmpeg`
   - Install on Windows: Download from [FFmpeg Website](https://ffmpeg.org/download.html)

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/AmankeldinovaMadina/kaz_sub_deepseek.git
cd kaz_sub_deepseek
pip install -r requirements.txt
```

Create a `.env` file in the root directory and add your DeepSeek API key:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## Usage

### 1. Translate a Subtitle File

```bash
python script.py input_video.mp4 input_subtitles.vtt
```

### 2. Embed Translated Subtitles in Video

```bash
python script.py input_video.mp4 input_subtitles.vtt
```

## Code Explanation

### Main Functions

- **`read_vtt(input_vtt: str) -> List[str]`**: Reads `.vtt` subtitles and detects encoding.
- **`batch_translate(texts: List[str]) -> List[str]`**: Translates subtitle text using DeepSeek API.
- **`translate_vtt(input_vtt: str, output_vtt: str)`**: Processes and translates subtitle file.
- **`add_vtt_to_video(input_video: str, subtitle_file: str, output_video: str)`**: Embeds `.vtt` subtitles into a video.

## Troubleshooting

### 1. `UnicodeDecodeError: Could not decode file.`

Ensure the subtitle file encoding is supported. Try manually converting it to UTF-8:

```bash
iconv -f WINDOWS-1251 -t UTF-8 input.vtt -o output.vtt
```

### 2. FFmpeg Not Found

Make sure FFmpeg is installed and added to the system path.

### 3. API Key Not Found

Check your `.env` file and ensure the key is set correctly.

## License

This project is open-source and available under the MIT License.

