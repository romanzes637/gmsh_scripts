import yaml
import sys

if __name__ == "__main__":
    #sys.argv[0] is a script name
    #To call python ./build_tranch.py quality_env quality_concrete size_in_Y
    quality_env_xy = int(sys.argv[1])
    quality_env_z = int(sys.argv[2])
    quality_radiant = int(sys.argv[3])
    radiant_points = int(sys.argv[4])
    size_xy = float(sys.argv[5])
    size_z = float(sys.argv[6])
    height_y = float(sys.argv[7])
    concrete_size = float(sys.argv[8])

    with open('tunnel.yaml') as f:
        tunnel = yaml.full_load(f)
    #modifying tunnel here
    # X
    # print(tunnel["data"]["layer"][0][1])
    #:0:1.5 - to manage quality
    tunnel["data"]["layer"][0][0] = str(2.925) + str(";;") + str(quality_radiant)
    tunnel["data"]["layer"][0][1] = str(2.925 + concrete_size) + str(";;") + str(radiant_points)
    tunnel["data"]["layer"][0][2] = str(size_xy / 2) + str(";;") + str(quality_env_xy) + str(":0:1.1")
    #     # Y
    # print(tunnel["data"]["layer"][1][1])
    tunnel["data"]["layer"][1][0] = str(height_y / 2) + str(";;") + str(quality_radiant)
    tunnel["data"]["layer"][1][1] = str(height_y / 2 + concrete_size) + str(";;") + str(radiant_points)
    tunnel["data"]["layer"][1][2] = str(size_xy / 2) + str(";;") + str(quality_env_xy) + str(":0:1.1")
    #     # -X
    # print(tunnel["data"]["layer"][2][1])
    tunnel["data"]["layer"][2][0] = str(2.925) + str(";;") + str(quality_radiant)
    tunnel["data"]["layer"][2][1] = str(2.925 + concrete_size) + str(";;") + str(radiant_points)
    tunnel["data"]["layer"][2][2] = str(size_xy / 2) + str(";;") + str(quality_env_xy) + str(":0:1.1")

    #     # -Y
    # print(tunnel["data"]["layer"][3][1])
    tunnel["data"]["layer"][3][0] = str(height_y / 2) + str(";;") + str(quality_radiant)
    tunnel["data"]["layer"][3][1] = str(height_y / 2 + 0.19) + str(";;") + str(radiant_points)
    tunnel["data"]["layer"][3][2] = str(size_xy / 2) + str(";;") + str(quality_env_xy) + str(":0:1.1")
    #     # Z
    # print(tunnel["data"]["layer"][4][0])
    tunnel["data"]["layer"][4][0] = str(size_z) + str(";;") + str(quality_env_z)

    with open('tunnel.yaml', 'w') as outfile:
        yaml.dump(tunnel, outfile)

    # resize_result(quality_env, quality_concrete, height_y)