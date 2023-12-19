import cv2
from pathlib import Path
from tqdm import tqdm
from moviepy.video.io.VideoFileClip import VideoFileClip

def open_video(video_path):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}.")
        return None
    return cap

def capture_frame(cap, frame_path):
    ret, frame = cap.read()
    if not ret:
        return None
    cv2.imwrite(str(frame_path), frame)
    return frame

def process_clip(cap, output_folder, frames_per_clip, clip_num, video_name, total_frames, clip_duration_seconds):
    if total_frames == 0:
        return
    total_clip_frames = int(clip_duration_seconds * cap.get(cv2.CAP_PROP_FPS))
    frame_positions = [x for x in range(clip_num * total_clip_frames, (clip_num + 1) * total_clip_frames, total_clip_frames // frames_per_clip)]

    for i, frame_pos in tqdm(enumerate(frame_positions), desc=f'Processing clip {clip_num + 1}', total=len(frame_positions)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        frame_path = output_folder / f"{video_name}_clip_{clip_num + 1}_frame_{i + 1}.jpg"
        captured_frame = capture_frame(cap, frame_path)
        if captured_frame is None:
            break

def capture_frames(video_path, output_folder, clip_duration_seconds, frames_per_clip, records_file):
    cap = open_video(video_path)
    if cap is None:
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Ensure at least one clip is processed even when video duration is less than clip duration
    clips = max(1, int(total_frames / (clip_duration_seconds * fps)))

    for clip_num in range(clips):
        process_clip(cap, output_folder, frames_per_clip, clip_num, video_path.stem, total_frames, clip_duration_seconds)

    cap.release()

    # Record the processed video
    with open(records_file, 'a') as file:
        file.write(f"{video_path.name}\n")

def extract_selected_clip(video_path, selected_clip_folder, extracted_dir):
    video_name = video_path.stem
    selected_clip_path = selected_clip_folder / f"{video_name}_selected_clip.mp4"
    
    if selected_clip_path.exists():
        clip = VideoFileClip(str(selected_clip_path))
        clip.write_videofile(str(extracted_dir / f"{video_name}_extracted_clip.mp4"))
        clip.close()

def process_all_videos(input_folder, output_folder, clip_duration_seconds, frames_per_clip, records_file, selected_clip_folder, extracted_dir):
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    selected_clip_folder = Path(selected_clip_folder)
    extracted_dir = Path(extracted_dir)

    # Read processed video records
    processed_videos = set()
    if records_file.exists():
        with open(records_file, 'r') as file:
            processed_videos = set(line.strip() for line in file)

    for video_path in tqdm(input_folder.glob("*.mp4"), desc='Processing videos', unit='video'):
        if video_path.name not in processed_videos:
            capture_frames(video_path, output_folder, clip_duration_seconds, frames_per_clip, records_file)
        extract_selected_clip(video_path, selected_clip_folder, extracted_dir)

def main():
    input_folder = Path(r"C:\Personal\Games\Fapelo\test\videos")
    output_folder = Path(r"C:\Personal\Games\Fapelo\test\Result")
    clip_duration_seconds = 180  # 3 minutes
    frames_per_clip = 3
    records_file = Path("processed_videos.txt")
    selected_clip_folder = Path(r"C:\Personal\Games\Fapelo\test\selected_clip")
    selected_clip_folder.mkdir(exist_ok=True)
    extracted_dir = Path(r"C:\Personal\Games\Fapelo\test\extracted_dir")
    extracted_dir.mkdir(exist_ok=True)

    process_all_videos(input_folder, output_folder, clip_duration_seconds, frames_per_clip, records_file, selected_clip_folder, extracted_dir)

if __name__ == "__main__":
    main()
