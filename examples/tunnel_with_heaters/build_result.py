import yaml
import sys

def resize_result(quality_env: float, quality_concrete: int, height_y: int):
    #in result calculate shift of tunnel
    with open('result.yaml') as f:
        res = yaml.full_load(f)

    #in env manage quality of rock formation
    with open('env_compose.yaml') as f2:
        env_c = yaml.full_load(f2)

    #in concrete manage quality and height of tunnel
    with open('concrete.yaml') as f3:
        concrete = yaml.full_load(f3)

    # in body manage quality and height of tunnel
    with open('body.yaml') as f4:
        body = yaml.full_load(f4)

    #work with quality of environment here
    env_c["data"]["matrix"][0][0] = str(0) + str(";") + str(quality_env)
    env_c["data"]["matrix"][0][1] = str(400) + str(";") + str(quality_env)
    #Y
    env_c["data"]["matrix"][1][0] = str(0) + str(";") + str(quality_env)
    env_c["data"]["matrix"][1][1] = str(200) + str(";") + str(quality_env)
    env_c["data"]["matrix"][1][2] = str(400) + str(";") + str(quality_env)
    #Z
    env_c["data"]["matrix"][2][0] = str(0) + str(";") + str(quality_env)
    env_c["data"]["matrix"][2][1] = str(400) + str(";") + str(quality_env)

    #work with body here
    #X
    body["data"]["layer"][0][0] = str(0.1) + str(";") + str(quality_concrete) + str(";")
    body["data"]["layer"][0][1] = str(29.25) + str(";") + str(quality_concrete) + str(";")
    #Y
    body["data"]["layer"][1][0] = str(0.1) + str(";") + str(quality_concrete) + str(";")
    body["data"]["layer"][1][1] = str(height_y / 2) + str(";") + str(quality_concrete) + str(";")
    #-X
    body["data"]["layer"][2][0] = str(0.1) + str(";") + str(quality_concrete) + str(";")
    body["data"]["layer"][2][1] = str(29.25) + str(";") + str(quality_concrete) + str(";")
    #-Y
    body["data"]["layer"][3][0] = str(0.1) + str(";") + str(quality_concrete) + str(";")
    body["data"]["layer"][3][1] = str(height_y / 2) + str(";") + str(quality_concrete) + str(";")
    #Z
    body["data"]["layer"][4][0] = str(400) + str(";") + str(quality_concrete) + str(";")

    #work with concrete here
    # X
    concrete["data"]["layer"][0][0] = str(0.1) + str(";") + str(quality_concrete) + str(";")
    concrete["data"]["layer"][0][1] = str(30.05) + str(";") + str(quality_concrete) + str(";")
    # Y
    concrete["data"]["layer"][1][0] = str(0.1) + str(";") + str(quality_concrete) + str(";")
    #with correction +3 for curve to be
    concrete["data"]["layer"][1][1] = str(height_y / 2 + 3) + str(";") + str(quality_concrete) + str(";")
    # -X
    concrete["data"]["layer"][2][0] = str(0.1) + str(";") + str(quality_concrete) + str(";")
    concrete["data"]["layer"][2][1] = str(30.05) + str(";") + str(quality_concrete) + str(";")
    # -Y
    concrete["data"]["layer"][3][0] = str(0.1) + str(";") + str(quality_concrete) + str(";")
    # with correction for curve ?
    concrete["data"]["layer"][3][1] = str(height_y / 2) + str(";") + str(quality_concrete) + str(";")
    # Z
    concrete["data"]["layer"][4][0] = str(400) + str(";") + str(quality_concrete) + str(";")


    #calc shift in result
    res["data"]["children_transforms"][1][0][1] = float((400 / 2) - int(height_y / 2))
    res["data"]["children_transforms"][2][0][1] = float((400 / 2) - int(height_y / 2) + 1.9)

    with open('env_compose.yaml', 'w') as outfile:
        yaml.dump(env_c, outfile)

    with open('result.yaml', 'w') as outfile:
        yaml.dump(res, outfile)

    with open('concrete.yaml', 'w') as outfile:
        yaml.dump(concrete, outfile)

    with open('body.yaml', 'w') as outfile:
        yaml.dump(body, outfile)



if __name__ == "__main__":
    #sys.argv[0] is a script name
    #To call python ./build_tranch.py quality_env quality_concrete size_in_Y
    quality_env = float(sys.argv[1])
    quality_concrete = int(sys.argv[2])
    height_y = float(sys.argv[3])

    resize_result(quality_env, quality_concrete, height_y)