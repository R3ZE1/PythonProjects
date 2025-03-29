import math
import re

def read_hailstone_data(file_path):
    """Reads hailstone detection data from the file and returns a list of (frame, x, y, radius)."""
    hailstones = []
    pattern = r"Frame (\d+): X=(\d+), Y=(\d+), Radius=(\d+)"

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            match = re.match(pattern, line)

            if not match:
                print(f"Skipping malformed line: {line}")
                continue  # Skip incorrect lines

            try:
                frame = int(match.group(1))
                x = int(match.group(2))
                y = int(match.group(3))
                radius = int(match.group(4))
                hailstones.append([frame, x, y, radius])
                #print(f"Parsed: Frame={frame}, X={x}, Y={y}, Radius={radius}")  # Debugging output

            except ValueError as e:
                print(f"Skipping invalid line: {line} - Error: {e}")

    return hailstones


def velocity(p1, p2):
    """Calculates velocity between two points."""
    frame_diff = p2[0] - p1[0]
    if frame_diff == 0:
        return None  # Avoid division by zero
    distance = math.sqrt((p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)

    #time = (frame diff) / (fps)

    return distance / frame_diff


def filter_hailstones(hailstones, max_radius_diff=2, max_velocity_deviation=2.0):
    """Filters hailstones by ensuring consistent motion and radius."""
    filtered_hailstones = []
    n = len(hailstones)
    detectionNum = 0

    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                d1, d2, d3 = hailstones[i], hailstones[j], hailstones[k]

                buffer = 0
                if(d1[1] == 936 and d2[1] == 864 and d1[3] == 60 and d2[3] == 60 and d3[3] == 60 and d3[1] == 792 and buffer == 0):
                    print(f"{d1}\n{d2}\n{d3}")
                    buffer = 1


                if(d1[2] > d2[2] or d2[2] > d3[2] or d1[2] > d3[2]):
                    #Movement does not make sense
                    continue

                # Ensure frames are increasing (no duplicate-frame detections)
                if not (d1[0] < d2[0] < d3[0]):
                    continue

                if(d2[0] - d1[0] < 5 or d3[0] - d2[0] < 5):
                    #Frames are too far apart, even if this is a valid detection (Which it most likely istn't it would not be accurate enougth to track anyways)
                    continue

                # Check radius consistency
                if abs(d1[3] - d2[3]) > max_radius_diff or abs(d2[3] - d3[3]) > max_radius_diff:
                    continue

                # Check velocity consistency
                v1 = velocity(d1, d2)
                v2 = velocity(d2, d3)

                if v1 is None or v2 is None:
                    continue

                if abs(v1 - v2) > max_velocity_deviation:
                    continue

                #At this point we have passed all of the checks we need, this is a valid detection

                #Get velocity in pixels per second
                #Take average between the two

                vel = round(((v1 + v2) / 2), 2)


                # If all tests pass, consider this a valid hailstone
                filtered_hailstones.append(d1 + [vel, detectionNum])
                filtered_hailstones.append(d2 + [vel, detectionNum])
                filtered_hailstones.append(d3 + [vel, detectionNum])

                detectionNum += 1

    return filtered_hailstones


def save_filtered_hailstones(file_path, hailstones):
    """Saves filtered hailstones to a file."""
    with open(file_path, "w") as file:  # Clears the file before writing
        for hailstone in hailstones:
            frame, x, y, radius, velocity, detectionNum = hailstone
            file.write(f"Frame {frame}: X={x}, Y={y}, Radius={radius}, Velocity={velocity}, DetectionNum={detectionNum}\n")


def main():
    """Main execution function."""
    hailstones = read_hailstone_data("hailstoneData.txt")

    if not hailstones:
        print("No valid hailstones found. Check input formatting.")
        return

    filtered_hailstones = filter_hailstones(hailstones)
    save_filtered_hailstones("filteredHailstones.txt", filtered_hailstones)

    if filtered_hailstones:
        print(f"Filtered hailstones saved: {len(filtered_hailstones)} entries.")
    else:
        print("No hailstones passed the filtering criteria.")


if __name__ == "__main__":
    main()
