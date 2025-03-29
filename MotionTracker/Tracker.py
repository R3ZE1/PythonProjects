import cv2
import numpy as np
import csv

def preprocess_frame(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply edge detection (Canny)
    edges = cv2.Canny(blurred, 50, 150)
    return edges

def detect_hailstones(frame):
    processed = preprocess_frame(frame)
    
    # Find contours
    contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter based on size
    hailstones = [cnt for cnt in contours if cv2.contourArea(cnt) > 50]
    
    return hailstones

def track_motion(prev_gray, curr_gray):
    flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    
    # Compute magnitude and angle of motion
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    
    # Threshold to highlight significant motion
    motion_mask = (mag > 2).astype(np.uint8) * 255  # Adjust threshold if needed
    return motion_mask



prev_positions = {}  # Stores previous (x, y) positions

def log_hailstone_data(hailstones, frame_id, motion_mask, file):
    global prev_positions
    falling_threshold = 1  # Minimum downward movement to count as falling
    
    new_positions = {}  # Store positions for this frame
    wrote_data = False  # Track if anything gets logged
    
    with open(file, "a") as txtfile:
        for cnt in hailstones:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])  # X-coordinate
                cy = int(M["m01"] / M["m00"])  # Y-coordinate
                area = cv2.contourArea(cnt)  # Object size
                
                # Ensure (cx, cy) are within bounds
                if 0 <= cy < motion_mask.shape[0] and 0 <= cx < motion_mask.shape[1]:
                    if motion_mask[cy, cx] == 255:  # Check if inside motion region
                        prev_y = prev_positions.get(cx)  # Only track by X

                        # Print for debugging
                        print(f"Frame {frame_id}: Detected object at ({cx}, {cy}), previous Y: {prev_y}")

                        # Check if falling (Y increasing)
                        if prev_y is not None and (cy - prev_y) >= falling_threshold:
                            txtfile.write(f"Frame {frame_id}: X={cx}, Y={cy}, Area={area}\n")
                            wrote_data = True  # Mark that data was written
                        
                        # Store new position for tracking in the next frame
                        new_positions[cx] = cy  

        # Flush file after writing
        if wrote_data:
            txtfile.flush()
    
    prev_positions = new_positions  # Update positions for the next frame




def main():
    cap = cv2.VideoCapture("/users/lucst/videos/captures/hailstoneTest.mp4")  # Change to video file path if needed
    ret, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        
    frame_id = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        motion_mask = track_motion(prev_gray, curr_gray)
        hailstones = detect_hailstones(frame)
        
        # Log hailstone data
        log_hailstone_data(hailstones, frame_id, motion_mask, "hailstoneData.txt")
        frame_id += 1
        
        # Highlight motion
        frame[motion_mask == 255] = [0, 0, 255]  # Red overlay for motion areas
        
        # Draw contours on the original frame
        cv2.drawContours(frame, hailstones, -1, (0, 255, 0), 2)
        
        cv2.imshow('Hailstone Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        prev_gray = curr_gray  # Update for next iteration
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
