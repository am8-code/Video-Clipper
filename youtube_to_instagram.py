
import os
import logging
import yt_dlp
import cv2
import numpy as np
import torch
import transformers
from moviepy import * 

class YouTubeMarketingGenerator:
    def __init__(self, clip_duration: int = 15, log_level: int = logging.INFO):
        """
        Initialize the YouTube Marketing Generator.
        
        Args:
            clip_duration (int): Desired length of the marketing clip in seconds.
            log_level (int): Logging level for debugging and monitoring.
        """
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize parameters
        self.clip_duration = clip_duration
        
        # Create downloads directory 
        os.makedirs('downloads', exist_ok=True)
        
        # Load text generation model
        try:
            self.text_generator = transformers.pipeline(
                'text-generation', 
                model='gpt2'  # Using a smaller model for easier installation
            )
        except Exception as e:
            self.logger.error(f"Failed to load text generation model: {e}")
            raise
    
    def download_youtube_video(self, url: str) -> str:
        """
        Download a YouTube video using yt-dlp.
        
        Args:
            url (str): YouTube video URL
        
        Returns:
            str: Path to downloaded video file
        """
        # Configuration for yt-dlp
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join('downloads', 'source_video.%(ext)s'),
            'nooverwrites': True,
            'no_color': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video information
                info_dict = ydl.extract_info(url, download=True)
                
                # Get the downloaded file path
                video_path = ydl.prepare_filename(info_dict)
                
                self.logger.info(f"Successfully downloaded video: {video_path}")
                return video_path
        
        except Exception as e:
            self.logger.error(f"Video download failed: {e}")
            raise
    
    def generate_marketing_caption(self) -> str:
        """
        Generate a creative marketing caption
        
        Returns:
            str: Generated marketing caption
        """
        try:
            prompt = "Create a catchy marketing caption for a viral video"
            caption = self.text_generator(
                prompt, 
                max_length=100, 
                num_return_sequences=1
            )[0]['generated_text']
            
            return caption.strip()
        except Exception as e:
            self.logger.warning(f"Caption generation failed: {e}")
            return "Check out this amazing video!"
    
    def export_instagram_video(self, video_path: str, start_time: float = 0) -> str:
        """
        Export video clip in Instagram-compatible format.
        
        Args:
            video_path (str): Source video path
            start_time (float): Start time of clip
        
        Returns:
            str: Path to exported Instagram video
        """
        try:
            # Ensure downloads directory exists
            os.makedirs('downloads', exist_ok=True)
            
            # Load video clip
            full_clip = VideoFileClip(video_path)

            # Calculate start time
            total_duration = full_clip.duration
            start_time = max(0, (total_duration - self.clip_duration) / 2)
    
            # Create subclip
            clip = full_clip.subclipped(start_time, start_time + self.clip_duration)
            
            # Resize to Instagram square format
            clip_resized = clip
            #clip_resized = clip.resize(height=1080, width=1080)
            #clip_resized = clip.fx( vfx.resize, height=1080, width = 1080) 
            
            # Output path
            output_path = os.path.join('downloads', 'instagram_clip.mp4')
            
            # Write video file
            clip_resized.write_videofile(
                output_path, 
                codec='libx264', 
                audio_codec='aac',
                fps=30
            )
            
            return output_path
        except Exception as e:
            self.logger.error(f"Video export failed: {e}")
            raise
    
    def process_video(self, youtube_url: str) -> dict:
        """
        Main method to process YouTube video into Instagram marketing content.
        
        Args:
            youtube_url (str): YouTube video URL
        
        Returns:
            dict: Generated marketing content details
        """
        try:
            # Download video
            video_path = self.download_youtube_video(youtube_url)
            
            # Generate marketing caption
            caption = self.generate_marketing_caption()
            
            # Export Instagram video (using start of video for simplicity)
            instagram_video = self.export_instagram_video(video_path)
            
            return {
                'video_path': instagram_video,
                'caption': caption
            }
        
        except Exception as e:
            self.logger.error(f"Video processing failed: {e}")
            raise

def main():
    """
    Main execution function for demonstrating the tool.
    """
    # An example video - replace with any YouTube URL you want
    youtube_url = "https://youtu.be/TLKxdTmk-zc?si=vHXFEtw68Rg6ZR7X"
    
    # Create generator instance
    generator = YouTubeMarketingGenerator()
    
    try:
        # Process the video
        result = generator.process_video(youtube_url)
        
        # Print results
        print(f"Instagram Video: {result['video_path']}")
        print(f"Marketing Caption: {result['caption']}")
    
    except Exception as e:
        print(f"Error processing video: {e}")

if __name__ == "__main__":
    main()
