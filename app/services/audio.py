import subprocess
import os
from fastapi import HTTPException

def compress_audio(input_path: str) -> str:
    """
    Compresses an audio file to Opus, 16kHz, Mono at 32k bitrate.
    If the result is larger than 24MB (to respect Groq's 25MB limit),
    it recompresses aggressively at 16k bitrate.
    """
    output_path = input_path + "_compressed.ogg"
    
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-ac", "1", "-ar", "16000",
        "-c:a", "libopus", "-b:a", "32k",
        output_path
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Audio conversion failed: {e.stderr.decode('utf-8')}")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="ffmpeg is not installed on the system.")
    
    # Verify file size is under 24MB (Groq limit is 25MB)
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    if size_mb > 24:
        output_path_2 = input_path + "_compressed_16k.ogg"
        command[11] = "16k"
        command[12] = output_path_2
        subprocess.run(command, check=True)
        return output_path_2
        
    return output_path
