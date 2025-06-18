"""
Whisper Speech-to-Text Module for Clinqo-June_Cohort_by Sujal

This module provides audio transcription functionality using OpenAI's Whisper model.
It takes audio files (.wav or .mp3) and converts them to text transcriptions.
"""

import os
import logging
from pathlib import Path
from typing import Optional

try:
    import whisper
except ImportError:
    raise ImportError(
        "whisper library not found. Install it with: pip install openai-whisper"
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhisperTranscriptionError(Exception):
    """Custom exception for transcription-related errors."""
    pass


def transcribe_audio(file_path: str, model_name: str = "base", save_to_file: bool = False, output_file: str = None) -> str:
    """
    Transcribe audio file to text using OpenAI Whisper.
    
    Args:
        file_path (str): Path to the audio file (.wav or .mp3)
        model_name (str): Whisper model to use (tiny, base, small, medium, large)
                         Default is 'base' for good balance of speed and accuracy
        save_to_file (bool): Whether to save transcription to a text file
        output_file (str): Custom output file path. If None, auto-generates filename
    
    Returns:
        str: Transcribed text from the audio file
        
    Raises:
        WhisperTranscriptionError: If transcription fails
        FileNotFoundError: If the audio file doesn't exist
        ValueError: If the file format is not supported
    """
    
    # Validate file path
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    # Check file extension
    supported_formats = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.wma'}
    if file_path.suffix.lower() not in supported_formats:
        raise ValueError(
            f"Unsupported file format: {file_path.suffix}. "
            f"Supported formats: {', '.join(supported_formats)}"
        )
    
    # Check file size (optional warning for very large files)
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 100:
        logger.warning(f"Large audio file detected: {file_size_mb:.1f}MB. Transcription may take longer.")
    
    try:
        logger.info(f"Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name)
        
        logger.info(f"Starting transcription of: {file_path.name}")
        result = model.transcribe(str(file_path))
        
        # Extract text from result
        transcribed_text = result.get("text", "").strip()
        
        if not transcribed_text:
            logger.warning("Transcription completed but no text was extracted")
            return ""
        
        logger.info(f"Transcription completed successfully. Text length: {len(transcribed_text)} characters")
        
        # Save to file if requested
        if save_to_file:
            if output_file is None:
                # Auto-generate filename based on input file
                output_file = file_path.with_suffix('.txt')
            else:
                output_file = Path(output_file)
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(transcribed_text)
                logger.info(f"Transcription saved to: {output_file}")
                print(f"Transcription saved to: {output_file}")
            except Exception as e:
                logger.error(f"Failed to save transcription to file: {e}")
                print(f"Warning: Failed to save to file: {e}")
        
        return transcribed_text
        
    except Exception as e:
        error_msg = f"Failed to transcribe audio file {file_path.name}: {str(e)}"
        logger.error(error_msg)
        raise WhisperTranscriptionError(error_msg) from e


def transcribe_audio_with_metadata(file_path: str, model_name: str = "base") -> dict:
    """
    Transcribe audio file and return detailed metadata along with text.
    
    Args:
        file_path (str): Path to the audio file
        model_name (str): Whisper model to use
    
    Returns:
        dict: Dictionary containing transcription text and metadata
        
    Raises:
        WhisperTranscriptionError: If transcription fails
        FileNotFoundError: If the audio file doesn't exist
    """
    
    # Validate inputs using the same logic as transcribe_audio
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    try:
        logger.info(f"Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name)
        
        logger.info(f"Starting detailed transcription of: {file_path.name}")
        result = model.transcribe(str(file_path))
        
        # Extract comprehensive information
        transcription_data = {
            "text": result.get("text", "").strip(),
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "file_path": str(file_path),
            "model_used": model_name,
            "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
        }
        
        logger.info(f"Detailed transcription completed. Language detected: {transcription_data['language']}")
        return transcription_data
        
    except Exception as e:
        error_msg = f"Failed to transcribe audio file {file_path.name}: {str(e)}"
        logger.error(error_msg)
        raise WhisperTranscriptionError(error_msg) from e


def get_available_models() -> list:
    """
    Get list of available Whisper models.
    
    Returns:
        list: List of available model names
    """
    return ["tiny", "base", "small", "medium", "large"]


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    sample_file = "/Users/sujalbist/clinqo-cohort/ai-engine/test-dataset/test_audio_2.mp3"  # Replace with actual file path
    
    try:
        # Basic transcription and save to file
        text = transcribe_audio(sample_file, save_to_file=True)
        print("Transcription:")
        print(text)
        
        # Alternative: Save to custom file location
        # text = transcribe_audio(sample_file, save_to_file=True, output_file="my_transcription.txt")
        
        # Detailed transcription with metadata
        detailed_result = transcribe_audio_with_metadata(sample_file)
        print(f"\nDetailed Results:")
        print(f"Language: {detailed_result['language']}")
        print(f"Text: {detailed_result['text']}")
        print(f"Number of segments: {len(detailed_result['segments'])}")
        
    except (FileNotFoundError, WhisperTranscriptionError, ValueError) as e:
        print(f"Error: {e}")
