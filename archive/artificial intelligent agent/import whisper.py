import whisper
import os

def transcribe_audio_to_text(audio_file_path):
    """
    Transcribes Kannada/Kanglish audio using OpenAI's Whisper model.
    """
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Could not find the audio file at: {C:\Users\SHRIDHAR\OneDrive - Anjuman Hami-e-Muslimeen\Documents\Project Netra (Cyber Eye)\artificial intelligent agent}")

    # Using the 'small' model. It is fast enough to run locally but accurate enough for regional accents. 
    # If it struggles with Kanglish, you can upgrade to "medium".
    print("Loading Whisper NLP model (this may take a few seconds)...")
    model = whisper.load_model("small")
    
    print("Transcribing audio file...")
    # We allow Whisper to auto-detect the language to better handle code-mixed Kanglish
    result = model.transcribe(audio_file_path)
    
    raw_transcript = result["text"].strip()
    print(f"\n[RAW TRANSCRIPT] -> {raw_transcript}")
    
    return raw_transcript

# Example usage:
my_text = transcribe_audio_to_text("test_audio.wav")