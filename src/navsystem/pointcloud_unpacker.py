import sys
import numpy as np
import msgpack
from scipy.spatial.transform import Rotation as R



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

    # Save keyframe positions (world coordinates!)
    with open(dest_keyframes_file, "w") as f:
        for kf_id, keyframe in keyframes.items():
            t_cw = np.array(keyframe.get("trans_cw", [0, 0, 0]))

            rot_cw_raw = keyframe.get("rot_cw", [0, 0, 0, 1])  # quaternion: (qx, qy, qz, qw)
            if len(rot_cw_raw) != 4:
                print(f"Warning: Keyframe {kf_id} has invalid rotation data: {rot_cw_raw}")
                continue

            R_cw = R.from_quat(rot_cw_raw).as_matrix()  # convert quaternion to rotation matrix

            # Invert the pose: T_cw → T_wc
            R_wc = R_cw.T
            t_wc = -R_wc @ t_cw

            quat_wc = R.from_matrix(R_wc).as_quat()  # get world-facing quaternion

            timestamp = keyframe.get("ts", 0)
            f.write(f"{kf_id}, {timestamp}, {t_wc[0]}, {t_wc[1]}, {t_wc[2]}, ({quat_wc[0]}, {quat_wc[1]}, {quat_wc[2]}, {quat_wc[3]})\n")

    print(f"Finished writing to {dest_keyframes_file}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python pointcloud_unpacker.py [map file] [csv landmarks destination] [csv keyframes destination]")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])




