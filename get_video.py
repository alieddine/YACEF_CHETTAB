import cv2
import pygame


def save_frames(input_video_path, output_folder_path):
    # Open the video file
    cap = cv2.VideoCapture(input_video_path)

    # Get the frames per second (fps) of the input video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Calculate the interval to capture frames
    interval = int(fps / 10)

    # Initialize frame counter
    frame_count = 0

    while True:
        # Read a frame from the video
        # pygame.init()
        # screen_info = pygame.display.Info()
        # width, height = screen_info.current_w, screen_info.current_h
        ret, frame = cap.read()
        # Break the loop if the video is over
        if not ret:
            break
        frame = cv2.resize(frame, (1920, 1080))

        # Save frames at the specified interval
        if frame_count % interval == 0:
            # Construct the output file name
            output_file_path = f"{output_folder_path}/frame_{frame_count // interval}.jpg"

            # Save the frame
            cv2.imwrite(output_file_path, frame)

        # Increment frame counter
        frame_count += 1
        print(frame_count)

    # Release the video capture object
    cap.release()

if __name__ == "__main__":
    input_video_path = "gif.gif"
    output_folder_path = "background3"

    import os
    os.makedirs(output_folder_path, exist_ok=True)

    save_frames(input_video_path, output_folder_path)
