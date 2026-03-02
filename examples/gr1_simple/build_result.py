import yaml
import sys

# def edit_rao_quality(quality_rao: float):
#     with open('RW_in_bent.yaml') as f:
#         RW = yaml.full_load(f)
#     # do smth here
#     RW["data"]["layer"][0][0] = str(0.3) + str(";") + str(quality_rao)
#     RW["data"]["layer"][0][1] = str(0.35) + str(";") + str(quality_rao)
#     RW["data"]["layer"][0][2] = str(0.85) + str(";") + str(quality_rao)
#
#     RW["data"]["layer"][1][0] = str(0.5) + str(";") + str(quality_rao)
#     RW["data"]["layer"][1][1] = str(0.55) + str(";") + str(quality_rao)
#     RW["data"]["layer"][1][2] = str(3.81) + str(";") + str(quality_rao)
#     RW["data"]["layer"][1][3] = str(3.86) + str(";") + str(quality_rao)
#     RW["data"]["layer"][1][4] = str(4.36) + str(";") + str(quality_rao)
#
#
#     with open('RW_in_bent.yaml', 'w') as outfile:
#         yaml.dump(RW, outfile)

#env.yaml
def resize_trunch(tranch_length: float, env: float, quality: float, quality_env: float):
    with open('env.yaml') as f:
        environment = yaml.full_load(f)

    #do smth with yml file
    #X
    environment["data"]["matrix"][0][0] = str(0) + str(";") + str(quality_env)
    environment["data"]["matrix"][0][1] = str(1.42 + env * 2) + str(";") + str(quality_env)

    #Y
    environment["data"]["matrix"][1][0] = str(0) + str(";") + str(quality_env)
    environment["data"]["matrix"][1][1] = str(3.21) + str(";") + str(quality_env)

    #Z
    environment["data"]["matrix"][2][0] = str(0) + str(";") + str(quality_env)
    environment["data"]["matrix"][2][1] = str(tranch_length + env * 2) + str(";") + str(quality_env)

    environment["data"]["children_transforms"][0][0][2] = env #Z
    environment["data"]["children_transforms"][0][0][1] = (2.5 + 1.42) / 2#Y
    environment["data"]["children_transforms"][0][0][0] = env#X

    with open('env.yaml', 'w') as outfile:
        yaml.dump(environment, outfile)

    #edz.yaml\bent.yaml\RW_old.yaml
    with open('edz.yaml') as f1:
        edz = yaml.full_load(f1)
    with open('bent.yaml') as f2:
        bent = yaml.full_load(f2)
    with open('RW.yaml') as f3:
        RW = yaml.full_load(f3)

    #do smth here
    edz["data"]["layer"][0][0] = str(0.71) + str(";") + str(quality)
    #print(edz["data"]["layer"][1])
    edz["data"]["layer"][1][0] = str(tranch_length) + str(";") + str(quality)
    # RW_concrete_bent["data"]["layer"][0][0] = str(0.125) + str(";") + str(quality)
    # RW_concrete_bent["data"]["layer"][0][1] = str(0.35) + str(";") + str(quality)

    bent["data"]["layer"][0][0] = str(0.575) + str(";") + str(quality)
    bent["data"]["layer"][1][0] = str(tranch_length) + str(";") + str(quality)

    RW["data"]["layer"][0][0] = str(0.48125) + str(";") + str(quality)
    RW["data"]["layer"][1][0] = str(tranch_length) + str(";") + str(quality)


    with open('edz.yaml', 'w') as outfile:
        yaml.dump(edz, outfile)
    with open('bent.yaml', 'w') as outfile:
        yaml.dump(bent, outfile)
    with open('RW.yaml', 'w') as outfile:
        yaml.dump(RW, outfile)

if __name__ == "__main__":
    '''The goal is to rescale the length of resulting tranch 
    and the size of a bent_buffer. Modifying the bent_buff in R_bent_sides.yaml
    and the length in R_edz.yaml, R_edz_left.yaml, R_edz_right, R_edz_trunch.yaml.yaml,
    T_edz_trunch.yaml, T_edz.yaml, T_edz_left.yaml, T_edz_right.yaml, Plug_tranch.yaml'''
    #sys.argv[0] is a script name
    # To call python ./build_result.py with parameters:
    #1 N_of_rao
    #2 env_Y
    #3 env_Z_bottom
    #4 env_Z_top
    #4 rao_quality
    #5 env_quality
    #6 distanse between wells
    #python. / build_result.py N_of_rao env_Y env_Z rao_quality env_quality distance
    tranch_length = int(sys.argv[1])
    env = float(sys.argv[2])
    quality = float(sys.argv[3])
    quality_env = float(sys.argv[4])
    #resize_trunch(tranch_length: float, env_Z: float, quality: float, quality_env: float)
    resize_trunch(tranch_length, env, quality, quality_env)
