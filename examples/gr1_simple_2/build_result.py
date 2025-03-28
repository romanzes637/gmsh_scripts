import yaml
import sys

#env.yaml
def resize_trunch(tranch_length: float,
                  env_X: float,
                  env_Y_up: float,
                  env_Y_down: float,
                  quality: float,
                  quality_env: float):
    with open('env.yaml') as f0:
        environment = yaml.full_load(f0)
    with open('edz.yaml') as f1:
        edz = yaml.full_load(f1)
    with open('bent_box_low.yaml') as f2:
        bent_box_low = yaml.full_load(f2)
    with open('simple_RW.yaml') as f3:
        simple_RW = yaml.full_load(f3)
    with open('simple_RW_stack.yaml') as f4:
        simple_RW_stack = yaml.full_load(f4)
    with open('simple_RW_main.yaml') as f5:
        simple_RW_main = yaml.full_load(f5)
    with open('bent_box_up.yaml') as f6:
        bent_box_up = yaml.full_load(f6)

    #workaround environment file
    #X
    environment["data"]["matrix"][0][0] = str(0) + str(";") + str(quality_env)
    environment["data"]["matrix"][0][1] = str(1.42 + env_X * 2) + str(";") + str(quality_env)

    #Y
    environment["data"]["matrix"][1][0] = str(0) + str(";") + str(quality_env)
    environment["data"]["matrix"][1][1] = str(env_Y_up + env_Y_down + 1.42) + str(";") + str(quality_env)

    #Z
    environment["data"]["matrix"][2][0] = str(0) + str(";") + str(quality_env)
    environment["data"]["matrix"][2][1] = str(tranch_length) + str(";") + str(quality_env)

    #environment["data"]["children_transforms"][0][0][2] = env #Z
    environment["data"]["children_transforms"][0][0][1] = 0.71 + env_Y_down
    environment["data"]["children_transforms"][0][0][0] = 0.71 + env_X#X

    #workaround edz file
    edz["data"]["layer"][0][0] = str(0.71) + str(";") + str(quality)
    edz["data"]["layer"][1][0] = str(tranch_length) + str(";") + str(quality)

    #workaround bent_box_low
    bent_box_low["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    bent_box_low["data"]["matrix"][0][1] = str(0.245) + str(";") + str(quality)

    bent_box_low["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    bent_box_low["data"]["matrix"][1][1] = str(0.24) + str(";") + str(quality)

    bent_box_low["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    bent_box_low["data"]["matrix"][2][1] = str(tranch_length) + str(";") + str(quality)

    #workaround simple_RW
    simple_RW["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    simple_RW["data"]["matrix"][0][1] = str(0.165) + str(";") + str(quality)

    simple_RW["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    simple_RW["data"]["matrix"][1][1] = str(0.1375) + str(";") + str(quality)

    simple_RW["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    simple_RW["data"]["matrix"][2][1] = str(tranch_length) + str(";") + str(quality)

    #workaround simple_RW_stack
    simple_RW_stack["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    simple_RW_stack["data"]["matrix"][0][1] = str(1.015) + str(";") + str(quality)

    simple_RW_stack["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    simple_RW_stack["data"]["matrix"][1][1] = str(0.1375) + str(";") + str(quality)

    simple_RW_stack["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    simple_RW_stack["data"]["matrix"][2][1] = str(tranch_length) + str(";") + str(quality)

    #workaround simple_RW_main

    simple_RW_main["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    simple_RW_main["data"]["matrix"][0][1] = str(1.185) + str(";") + str(quality)

    simple_RW_main["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    simple_RW_main["data"]["matrix"][1][1] = str(0.55) + str(";") + str(quality)

    simple_RW_main["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    simple_RW_main["data"]["matrix"][2][1] = str(tranch_length) + str(";") + str(quality)

    #workaround bent_box_up
    bent_box_up["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    bent_box_up["data"]["matrix"][0][1] = str(1.015) + str(";") + str(quality)

    bent_box_up["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    bent_box_up["data"]["matrix"][1][1] = str(0.1375) + str(";") + str(quality)

    bent_box_up["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    bent_box_up["data"]["matrix"][2][1] = str(tranch_length) + str(";") + str(quality)


    with open('env.yaml', 'w') as outfile:
        yaml.dump(environment, outfile)
    with open('edz.yaml', 'w') as outfile:
        yaml.dump(edz, outfile)
    with open('bent_box_low.yaml', 'w') as outfile:
        yaml.dump(bent_box_low, outfile)
    with open('simple_RW.yaml', 'w') as outfile:
        yaml.dump(simple_RW, outfile)
    with open('simple_RW_stack.yaml', 'w') as outfile:
        yaml.dump(simple_RW_stack, outfile)
    with open('simple_RW_main.yaml', 'w') as outfile:
        yaml.dump(simple_RW_main, outfile)
    with open('bent_box_up.yaml', 'w') as outfile:
        yaml.dump(bent_box_up, outfile)

if __name__ == "__main__":
    '''The goal is to rescale the length of resulting mesh. We change ENV in +X -X simultaneously,
     ENV in +Y -Y separately, rescaling tube with ENV in Z. Changing mesh quality for ENV separately from the main mesh'''
    #sys.argv[0] is a script name
    # To call python ./build_result.py with parameters:
    #1 tranch_length - length of tube in Z
    #2 env_X - environment in +X -X
    #3 env_Y_up - environment in +Y
    #4 env_Y_down - environment in -Y
    #4 quality
    #5 quality_env
    #python. / build_result.py tranch_length env_X env_Y_up env_Y_down quality quality_env
    tranch_length = int(sys.argv[1])
    env_X = float(sys.argv[2])
    env_Y_up = float(sys.argv[3])
    env_Y_down = float(sys.argv[4])
    quality = float(sys.argv[5])
    quality_env = float(sys.argv[6])
    resize_trunch(tranch_length, env_X, env_Y_up, env_Y_down, quality, quality_env)
