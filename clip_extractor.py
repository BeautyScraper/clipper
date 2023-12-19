from pathlib import Path
from tqdm import tqdm
import pandas as pd
import re
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import ImageSequenceClip

def extract_selected_clip(selected_clip_folder, extracted_dir, output_folder, input_folder):
    selected_clip_folder = Path(selected_clip_folder)
    extracted_dir = Path(extracted_dir)
    output_folder = Path(output_folder)
    input_folder = Path(input_folder)

    for image_file_path in tqdm(selected_clip_folder.glob("*.jpg"), desc='Extracting selected clips', unit='image'):
        clip_number = int(re.search(r'_clip_(\d+)_', image_file_path.stem).group(1))

        csv_file_path = output_folder / f"{image_file_path.stem.split('_clip_')[0]}_info.csv"
        if not csv_file_path.exists():
            print(f"Error: Corresponding CSV file not found for {image_file_path}. Skipping.")
            continue

        clip_df = pd.read_csv(csv_file_path)

        video_name = clip_df['FramePath'][0].split('_clip_')[0]
        video_path = input_folder / f"{video_name}.mp4"
        output_clip_folder = extracted_dir / f"{video_name}_clips"
        output_clip_folder.mkdir(exist_ok=True)
        try:
            clip_info = clip_df[clip_df['Clip_number'] == clip_number-1].iloc[0]
        except:
            breakpoint()
        start_frame = int(clip_info['StartFrameNumber'])
        end_frame = int(clip_info['EndFrameNumber'])
        
        clip_output_path = extracted_dir / f"{video_name}_clip_{clip_number}.mp4"

        if not clip_output_path.exists():
            with VideoFileClip(str(video_path)) as video:
                clip_duration = video.duration
                start_time = max(0, start_frame / video.fps)
                end_time = min(clip_duration, end_frame / video.fps)
                clip = video.subclip(start_time, end_time)
                clip.write_videofile(str(clip_output_path), codec="libx264", audio_codec="aac")
        image_file_path.unlink()
    print("Clips extraction completed.")

# Add this function call in your main() function
# extract_selected_clip(selected_clip_folder, extracted_dir, output_folder, input_folder)
