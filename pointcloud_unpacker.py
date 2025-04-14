import sys
import msgpack


def main(map_file, dest_landmarks_file, dest_keyframes_file):
    # Read file as binary and unpack data using MessagePack library
    with open(map_file, "rb") as f:
        data = msgpack.unpackb(f.read(), use_list=False, raw=False)

    # # The point data is tagged "landmarks"
    # landmarks = data["landmarks"]
    # print("Point cloud has {} points.".format(len(landmarks)))

    # # Write point coordinates into file, one point per line
    # with open(dest_landmarks_file, "w") as f:
    #     for id, point in landmarks.items():
    #         pos = point["pos_w"]
    #         f.write("{}, {}, {}\n".format(pos[0], pos[1], pos[2]))
    # print(f"Finished writing to {dest_landmarks_file}")

    # Get keyframes
    keyframes = data.get("keyframes", {})

    print(f"Extracted {len(keyframes)} keyframes.")

    # Save keyframe positions
    with open(dest_keyframes_file, "w") as f:
        for kf_id, keyframe in keyframes.items():
            position = keyframe.get("trans_cw", [0, 0, 0])  # Translation (x, y, z)
            rotation = keyframe.get("rot_cw", [[1, 0, 0], [0, 1, 0], [0, 0, 1]])  # Identity matrix if missing
            timestamp = keyframe.get("ts", 0)  # Timestamp

            # Convert rotation matrix to a single-line string

            f.write(f"{kf_id}, {timestamp}, {position[0]}, {position[1]}, {position[2]}, {rotation}\n")

    print(f"Saved keyframes to {dest_keyframes_file}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python pointcloud_unpacker.py [map file] [csv landmarks destination] [csv keyframes destination]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])




