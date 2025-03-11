import os
import subprocess
import asyncio
import aiofiles
import chardet
from dotenv import load_dotenv
from typing import List
from openai import OpenAI

# Load environment variables from the .env file
load_dotenv()

# Set DeepSeek API key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("API key not found. Ensure it is defined in the .env file.")

# Initialize DeepSeek client
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

async def read_vtt(input_vtt: str) -> List[str]:
    """Read a VTT file and detect encoding automatically."""
    # Read the file as binary to detect encoding
    with open(input_vtt, "rb") as f:
        raw_data = f.read()
        encoding_detected = chardet.detect(raw_data)["encoding"]

    print(f"🔍 Detected encoding for {input_vtt}: {encoding_detected}")

    # Try reading the file with the detected encoding, fallback to UTF-8 & Windows-1251
    encodings_to_try = [encoding_detected, "utf-8", "windows-1251", "latin1"]
    
    for enc in encodings_to_try:
        try:
            async with aiofiles.open(input_vtt, "r", encoding=enc) as file:
                lines = await file.readlines()
            print(f"✅ Successfully read file with encoding: {enc}")
            return lines
        except (UnicodeDecodeError, TypeError):
            print(f"⚠️ Failed with encoding: {enc}, trying next...")

    raise UnicodeDecodeError("❌ Could not decode file. Check file encoding manually.")

async def write_vtt(output_vtt: str, lines: List[str]):
    """Write lines to a VTT file."""
    async with aiofiles.open(output_vtt, "w", encoding="utf-8") as file:
        await file.write("".join(lines))

def is_translatable(line: str) -> bool:
    """Determine if a line should be translated."""
    return not (("-->" in line) or line.strip() == "" or line.startswith("WEBVTT") or line.strip().isdigit())

async def batch_translate(texts: List[str], max_retries: int = 3) -> List[str]:
    """Translate a batch of texts using DeepSeek API."""
    prompt = (
        "Translate the following Russian subtitles into Kazakh while preserving timing and formatting:\n\n" +
        "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts)])
    )

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2048
            )
            translated_text = response.choices[0].message.content.strip()
            translated_lines = [line.partition('. ')[2] if '. ' in line else line for line in translated_text.split('\n')]
            return translated_lines
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            await asyncio.sleep(2 ** attempt)
    print("All translation attempts failed. Returning original texts.")
    return texts


async def translate_vtt(input_vtt: str, output_vtt: str, batch_size: int = 10):
    """Translate the text in a VTT file."""
    lines = await read_vtt(input_vtt)
    translated_lines = []
    batch = []
    batch_indices = []
    for idx, line in enumerate(lines):
        stripped_line = line.strip()
        if is_translatable(stripped_line):
            batch.append(stripped_line)
            batch_indices.append(idx)
            if len(batch) == batch_size:
                translated_batch = await batch_translate(batch)
                for i, translated_line in zip(batch_indices, translated_batch):
                    lines[i] = translated_line + '\n'
                batch = []
                batch_indices = []
        else:
            translated_lines.append((idx, stripped_line))
    
    if batch:
        translated_batch = await batch_translate(batch)
        for i, translated_line in zip(batch_indices, translated_batch):
            lines[i] = translated_line + '\n'
    
    await write_vtt(output_vtt, lines)
    print(f"Translated VTT saved as {output_vtt}")

def add_vtt_to_video(input_video: str, subtitle_file: str, output_video: str):
    """Embed VTT subtitles into a video using FFmpeg."""
    try:
        command = [
            "ffmpeg",
            "-i", input_video,
            "-vf", f"subtitles={subtitle_file}",
            "-c:a", "copy",
            output_video
        ]
        subprocess.run(command, check=True)
        print(f"Subtitles successfully added to {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error adding subtitles to video: {e}")

async def main(input_video: str, input_vtt: str):
    """Main function to translate subtitles and add them to a video."""
    output_vtt = input_vtt.replace(".vtt", "_translated.vtt")
    output_video = input_video.replace(".mp4", "_with_subtitles.mp4")

    print("Translating subtitles...")
    await translate_vtt(input_vtt, output_vtt)

    print("Adding subtitles to video...")
    add_vtt_to_video(input_video, output_vtt, output_video)

    print(f"Process complete. Video with subtitles saved as {output_video}")

if name == "__main__":
    # Define your video and subtitle file names here
    input_video_file = "GMT20250130-140356_Recording_1920x1080.mp4"
    input_vtt_file = "GMT20250130-140356_Recording.transcript.vtt"

    asyncio.run(main(input_video_file, input_vtt_file))