import math

def read_hailstone_data(file_path):
    """Reads hailstone detection data from the file and returns a list of (frame, x, y, radius)."""
    hailstones = []
    with open(file_path, "r") as file:
        for line in file:
            try:
                # Clean up the string
                line = line.strip().replace(',', '')  # Remove commas to simplify splitting
                parts = line.split()  # Split by spaces
                
                # Ensure correct format
                if len(parts) < 7:
                    print(f"Skipping malformed line: {line}")
                    continue

                # Extract values
                frame = int(parts[1].replace(':', ''))  # Remove colon after Frame number
                x = int(parts[3].split('=')[1])
                y = int(parts[4].split('=')[1])
                radius = int(parts[6].split('=')[1])

                hailstones.append((frame, x, y, radius))

            except (ValueError, IndexError) as e:
                print(f"Skipping invalid line: {line} - Error: {e}")

    return hailstones

def velocity(p1, p2):
    """Calculates velocity between two points."""
    frame_diff = p2[0] - p1[0]
    if frame_diff == 0:
        return None  # Avoid division by zero
    distance = math.sqrt((p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)
    return distance / frame_diff

def filter_hailstones(hailstones, max_radius_diff=5, max_velocity_deviation=2.0):
    """Filters hailstones by ensuring consistent motion and radius."""
    filtered_hailstones = []
    n = len(hailstones)
    
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                h1, h2, h3 = hailstones[i], hailstones[j], hailstones[k]
                
                # Ensure frames are increasing (no duplicate-frame detections)
                if not (h1[0] < h2[0] < h3[0]):
                    continue
                
                # Check radius consistency
                if abs(h1[3] - h2[3]) > max_radius_diff or abs(h2[3] - h3[3]) > max_radius_diff:
                    continue
                
                # Check velocity consistency
                v1 = velocity(h1, h2)
                v2 = velocity(h2, h3)
                
                if v1 is None or v2 is None:
                    continue
                
                if abs(v1 - v2) > max_velocity_deviation:
                    continue
                
                # If all tests pass, consider this a valid hailstone
                filtered_hailstones.append(h1)
                filtered_hailstones.append(h2)
                filtered_hailstones.append(h3)
                
    return filtered_hailstones

def save_filtered_hailstones(file_path, hailstones):
    """Saves filtered hailstones to a file."""
    with open(file_path, "w") as file:  # Clears the file before writing
        for frame, x, y, radius in hailstones:
            file.write(f"Frame {frame}: X={x}, Y={y}, Radius={radius}\n")

def main():
    """Main execution function."""
    hailstones = read_hailstone_data("hailstoneData.txt")
    filtered_hailstones = filter_hailstones(hailstones)
    save_filtered_hailstones("filteredHailstones.txt", filtered_hailstones)

if __name__ == "__main__":
    main()
