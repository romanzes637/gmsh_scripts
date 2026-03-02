import yaml
import sys

def edit_rao_quality(quality_rao: float):
    with open('RW_in_bent.yaml') as f:
        RW = yaml.full_load(f)
    # do smth here
    RW["data"]["layer"][0][0] = str(0.3) + str(";") + str(quality_rao)
    RW["data"]["layer"][0][1] = str(0.35) + str(";") + str(quality_rao)
    RW["data"]["layer"][0][2] = str(0.85) + str(";") + str(quality_rao)

    RW["data"]["layer"][1][0] = str(0.5) + str(";") + str(quality_rao)
    RW["data"]["layer"][1][1] = str(0.55) + str(";") + str(quality_rao)
    RW["data"]["layer"][1][2] = str(3.81) + str(";") + str(quality_rao)
    RW["data"]["layer"][1][3] = str(3.86) + str(";") + str(quality_rao)
    RW["data"]["layer"][1][4] = str(4.36) + str(";") + str(quality_rao)


    with open('RW_in_bent.yaml', 'w') as outfile:
        yaml.dump(RW, outfile)

#trunch.yaml
def resize_trunch(n_of_rao: int, env_Y: float, env_Z_bottom: float, env_Z_top: float, quality_env: float, distance: float):
#def resize_result(env_X: float, env_Y: float, env_Z: float, tranch: float, env_quality: float):
    with open('tranch.yaml') as f:
        tranch = yaml.full_load(f)

    #do smth with yml file
    #X
    tranch["data"]["matrix"][0][0] = str(0) + str(";") + str(quality_env)
    tranch["data"]["matrix"][0][1] = str(distance + 1.7) + str(";") + str(quality_env)
    tranch["data"]["matrix"][0][2] = str((distance + 1.7) * n_of_rao) + str(":") + str(n_of_rao) + str(";") + str(quality_env)

    #Y
    tranch["data"]["matrix"][1][0] = str(0) + str(";") + str(quality_env)
    tranch["data"]["matrix"][1][1] = str(1.7 + env_Y) + str(";") + str(quality_env)

    #Z
    z_all = env_Z_top + env_Z_bottom + 13.08
    z_curr_top = z_all / 2 - 7.71
    z_curr_bottom = z_all / 2 - 5.3
    delta_z_bottom = abs(env_Z_bottom - z_curr_bottom)
    delta_z_top = abs(env_Z_top - z_curr_top)
    #print(delta_z_top, delta_z_bottom)
    if env_Z_bottom < env_Z_top:
        shift = 0 - delta_z_top
    else: shift = delta_z_top
    tranch["data"]["matrix"][2][0] = str(0) + str(";") + str(quality_env)
    tranch["data"]["matrix"][2][1] = str(z_all) + str(";") + str(quality_env)
    tranch["data"]["items_children_transforms"][0][0][0][2] = shift#- 13.01 / 2
    #result["data"]["matrix"][2][1] = str(env_Z_bottom) + str(";") + str(env_quality)
    #result["data"]["matrix"][2][2] = str(float(result["data"]["matrix"][2][1].split(";")[0]) + 12.2) + str(";") + str(env_quality)
    #result["data"]["matrix"][2][3] = str(float(result["data"]["matrix"][2][2].split(";")[0]) + env_Z_top) + str(";") + str(env_quality)

    #shifting tranch inside env
    #X
    #tranch["data"]["items_children_transforms"][0][0][0][0] = 0 - tranch / 2
    #Y
    #tranch["data"]["items_children_transforms"][0][0][0][1] = 0 - 6.45 / 2
    #Z

    #tranch["data"]["items_children_transforms"][0][0][0][2] = shift#- 13.01 / 2
    #set quality
    #result["metadata"]["options"]["Mesh.MeshSizeFactor"] = quality

    with open('tranch.yaml', 'w') as outfile:
        yaml.dump(tranch, outfile)

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
    n_of_rao = int(sys.argv[1])
    env_Y = float(sys.argv[2])
    env_Z_bottom = float(sys.argv[3])
    env_Z_top = float(sys.argv[4])
    quality_rao = float(sys.argv[5])
    quality_env = float(sys.argv[6])
    distance = float(sys.argv[7])
    edit_rao_quality(quality_rao)
    resize_trunch(n_of_rao, env_Y, env_Z_bottom, env_Z_top, quality_env, distance)


    #single_block_length = resizing_rao(concrete_X, bentonite_X, quality_rao)
    #block = resizing_buffer(buff_size, quality_rao, bentonite_X)
    #tranch = resizing_tranches(n_of_rao, block, quality_rao, concrete_X, bentonite_X)
    #if tranch > env_X or 5.6 > env_Y:
    #    print("Size of env cant be less than tranch size.")
    #    exit(1)
    #resize_result(env_X, env_Y, env_Z_bottom, env_Z_top, tranch, quality_env)
    #resize_result(env_X, env_Y, env_Z, tranch, quality_env)
