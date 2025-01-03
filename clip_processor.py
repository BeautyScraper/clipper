import cv2
from pathlib import Path
from tqdm import tqdm
from moviepy.video.io.VideoFileClip import VideoFileClip
import pandas as pd
import re
from clip_extractor import extract_selected_clip


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

def process_clip(cap, output_folder, frames_per_clip, clip_num, video_name, total_frames, clip_duration_seconds, clip_data):
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
        clip_data.append({
            'Clip_number':clip_num,
            'StartFrameNumber': clip_num * total_clip_frames,
            'EndFrameNumber':  (clip_num + 1) * total_clip_frames,
            'clip_starttime' : clip_num * total_clip_frames / cap.get(cv2.CAP_PROP_FPS),
            'clip_endtime' : (clip_num + 1) * total_clip_frames / cap.get(cv2.CAP_PROP_FPS),
            'FramePath': Path(frame_path).name,
        })
        # Store clip information

    # Convert clip_data to a DataFrame and save it to a CSV file

def capture_frames(video_path, output_folder, clip_duration_seconds, frames_per_clip, records_file):
    cap = open_video(video_path)
    if cap is None:
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Ensure at least one clip is processed even when video duration is less than clip duration
    clips = max(1, 1 + int(total_frames / (clip_duration_seconds * fps)))
    csv_file = output_folder / f"{video_path.stem}_info.csv"
    clip_data = []
    for clip_num in range(clips):
        process_clip(cap, output_folder, frames_per_clip, clip_num, video_path.stem, total_frames, clip_duration_seconds, clip_data)
    clip_df = pd.DataFrame(clip_data)
    clip_df.to_csv(csv_file, index=False)

    cap.release()

    # Record the processed video
    with open(records_file, 'a') as file:
        file.write(f"{video_path.name}\n")


def match_regex_to_files(folder_path, regex_pattern):
    folder_path = Path(folder_path)
    
    if not folder_path.is_dir():
        print(f"Error: {folder_path} is not a valid directory.")
        return []
    
    regex = re.compile(regex_pattern)
    
    matching_files = [file for file in folder_path.glob('*') if regex.match(file.name)]
    
    return matching_files[:1]

def process_all_videos(input_folder, output_folder, clip_duration_seconds, frames_per_clip, records_file, selected_clip_folder, extracted_dir):
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    selected_clip_folder = Path(selected_clip_folder)
    extracted_dir = Path(extracted_dir)
    output_folder.mkdir(exist_ok=True)

    # Read processed video records
    processed_videos = set()
    if records_file.exists():
        with open(records_file, 'r') as file:
            processed_videos = set(line.strip() for line in file)

    for video_path in tqdm(input_folder.glob("*.mp4"), desc='Processing videos', unit='video'):
        if video_path.name not in processed_videos:
            capture_frames(video_path, output_folder, clip_duration_seconds, frames_per_clip, records_file)

def del_done_videos(input_folder, selected_clip_folder, output_folder):
    input_folder = Path(input_folder)
    selected_clip_folder = Path(selected_clip_folder)
    output_folder = Path(output_folder)

    for video_path in tqdm(input_folder.glob("*.mp4"), desc='Deleting videos', unit='video'):
        video_name = video_path.stem
        csv_file = output_folder / f"{video_name}_info.csv"

        if csv_file.exists():
            csv_data = pd.read_csv(csv_file)
            frames_exist = all((Path(output_folder) / frame_path).exists() or
                   (Path(selected_clip_folder) / frame_path).exists()
                   for frame_path in csv_data['FramePath'])

            if not frames_exist:
                print(f"Deleting {video_path} as frames do not exist.")
                video_path.unlink()
            else:
                print(f"Frames exist for {video_path}, keeping the video.")
        else:
            print(f"CSV file not found for {video_path}, keeping the video.")



def main():
    input_folder = Path(r"D:\paradise\stuff\new\to_be_clipped")
    output_folder = Path(r"C:\dumpinggrounds\clipper_data\Result")
    input_folder.mkdir(exist_ok=True,parents=True)
    output_folder.mkdir(exist_ok=True,parents=True)
    clip_duration_seconds = 30  # 3 minutes
    frames_per_clip = 1
    records_file = Path("processed_videos.txt")
    selected_clip_folder = Path(r"C:\dumpinggrounds\clipper_data\selected_clip")
    selected_clip_folder.mkdir(exist_ok=True)
    selected_clip_folder2 = Path(r"C:\dumpinggrounds\clipper_data\selected_clip2")
    selected_clip_folder2.mkdir(exist_ok=True)
    extracted_dir = Path(r"D:\paradise\stuff\new\clips")
    extracted_dir.mkdir(exist_ok=True)
    extracted_dir2 = Path(r"D:\paradise\stuff\new\pvd2\extractedVideo")
    extracted_dir2.mkdir(exist_ok=True)

    process_all_videos(input_folder, output_folder, clip_duration_seconds, frames_per_clip, records_file, selected_clip_folder, extracted_dir)
    extract_selected_clip(selected_clip_folder, extracted_dir, output_folder, input_folder) 
    extract_selected_clip(selected_clip_folder2, extracted_dir2, output_folder, input_folder) 
    del_done_videos(input_folder,selected_clip_folder,output_folder)


if __name__ == "__main__":
    main()
#complete the del_done_videos function which deletes the video files from "input_folder" if corresponding csv file does exist in "output_folder" but corresponding image files does not exist in neither "output_folder" nor "selected_clip_folder"
# complete extract_selected_clip function such that all the image files in selected_clip_folder it cut the clip from the original video file in input folder and put it in the extracted_dir using the corresponding csv file, use moviepy fir this clip extraction 
