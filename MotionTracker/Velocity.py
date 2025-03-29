import numpy as np

def load_hailstone_data(file):
    hailstones = {}

    with open(file, "r") as txtfile:
        for line in txtfile:
            try:
                parts = line.strip().split(": ", 1)  # Split first by ": "
                if len(parts) < 2:
                    print(f"Skipping malformed line: {line.strip()}")
                    continue

                frame_part, data_part = parts
                if not frame_part.startswith("Frame"):
                    print(f"Skipping malformed line: {line.strip()}")
                    continue

                frame_id = int(frame_part.split(" ")[1])  # Extract frame number
                
                # Now split remaining data by ", "
                data_parts = data_part.split(", ")
                obj_id = data_parts[0].split("=")[1]  # Extract object ID
                x = int(data_parts[1].split("=")[1])  # Extract X coordinate
                y = int(data_parts[2].split("=")[1])  # Extract Y coordinate
                radius = int(data_parts[3].split("=")[1])  # Extract radius

                if obj_id not in hailstones:
                    hailstones[obj_id] = []
                
                hailstones[obj_id].append((frame_id, x, y, radius))

            except (IndexError, ValueError) as e:
                print(f"Error parsing line: {line.strip()} - {e}")
                continue  # Skip problematic lines

    return hailstones

def filter_falling_hailstones(hailstones, min_detections=3, max_deviation=2):
    falling_hailstones = {}

    for obj_id, detections in hailstones.items():
        if len(detections) < min_detections:
            continue  # Ignore objects with too few detections
        
        velocities = []
        has_movement = False  # Track if the object has moved

        for i in range(1, len(detections)):
            frame1, x1, y1, r1 = detections[i - 1]
            frame2, x2, y2, r2 = detections[i]

            time_diff = frame2 - frame1  # Assumes constant frame intervals
            if time_diff == 0:
                continue  # Avoid division by zero

            velocity = (y2 - y1) / time_diff  # Vertical velocity
            velocities.append(velocity)

            # Check if the object has moved significantly
            if abs(y2 - y1) > max_deviation: # Ensure some vertical displacement
                has_movement = True

        # Ensure the object moved and the velocity is fairly stable
        if has_movement and len(velocities) >= 2 and all(abs(v2 - v1) <= max_deviation for v1, v2 in zip(velocities, velocities[1:])):
            falling_hailstones[obj_id] = detections

    return falling_hailstones

def save_filtered_hailstones(falling_hailstones, file):
    with open(file, "w") as txtfile:
        for obj_id, detections in falling_hailstones.items():
            for frame_id, x, y, radius in detections:
                txtfile.write(f"Frame {frame_id}: ID={obj_id}, X={x}, Y={y}, Radius={radius}\n")

def main():
    hailstones = load_hailstone_data("hailstoneData.txt")
    falling_hailstones = filter_falling_hailstones(hailstones)
    save_filtered_hailstones(falling_hailstones, "filteredHailstones.txt")
    print("Filtered hailstones saved to filteredHailstones.txt")

if __name__ == "__main__":
    print("This runs!")
    main()
