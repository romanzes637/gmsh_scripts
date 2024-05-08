import yaml
import sys

def rebuild_t_edz(length: float, quality: float) -> float:
    with open('T_edz.yaml') as f:
        t_edz = yaml.full_load(f)

    #do smth with yml file
    #X
    t_edz["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    t_edz["data"]["matrix"][0][1] = str(length) + str(";") + str(quality)
    #Y
    t_edz["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    t_edz["data"]["matrix"][1][1] = str(0.3) + str(";") + str(quality)
    t_edz["data"]["matrix"][1][2] = str(6.15) + str(";") + str(quality)
    t_edz["data"]["matrix"][1][3] = str(6.45) + str(";") + str(quality)
    #Z
    t_edz["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    t_edz["data"]["matrix"][2][1] = str(6.81) + str(";") + str(quality)
    t_edz["data"]["matrix"][2][2] = str(7.11) + str(";") + str(quality)

    with open('T_edz.yaml', 'w') as outfile:
        yaml.dump(t_edz, outfile)

    with open('T_edz_basic.yaml') as f:
        t_edz_basic = yaml.full_load(f)

    #do smth with yml file
    #X
    t_edz_basic["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    t_edz_basic["data"]["matrix"][0][1] = str(3.6) + str(";") + str(quality)
    #Y
    t_edz_basic["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    t_edz_basic["data"]["matrix"][1][1] = str(0.3) + str(";") + str(quality)
    t_edz_basic["data"]["matrix"][1][2] = str(6.15) + str(";") + str(quality)
    t_edz_basic["data"]["matrix"][1][3] = str(6.45) + str(";") + str(quality)
    #Z
    t_edz_basic["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    t_edz_basic["data"]["matrix"][2][1] = str(6.81) + str(";") + str(quality)
    t_edz_basic["data"]["matrix"][2][2] = str(7.11) + str(";") + str(quality)

    with open('T_edz_basic.yaml', 'w') as outfile:
        yaml.dump(t_edz_basic, outfile)

    with open('T_edz_right.yaml') as f:
        t_edz_right = yaml.full_load(f)

    #do smth with yml file
    #X
    t_edz_right["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    t_edz_right["data"]["matrix"][0][1] = str(3.6) + str(";") + str(quality)
    t_edz_right["data"]["matrix"][0][2] = str(3.9) + str(";") + str(quality)
    #Y
    t_edz_right["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    t_edz_right["data"]["matrix"][1][1] = str(6.45) + str(";") + str(quality)
    #Z
    t_edz_right["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    t_edz_right["data"]["matrix"][2][1] = str(7.11) + str(";") + str(quality)

    with open('T_edz_right.yaml', 'w') as outfile:
        yaml.dump(t_edz_right, outfile)

    with open('T_edz_left.yaml') as f:
        t_edz_left = yaml.full_load(f)

    #do smth with yml file
    #X
    t_edz_left["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    t_edz_left["data"]["matrix"][0][1] = str(0.3) + str(";") + str(quality)
    t_edz_left["data"]["matrix"][0][2] = str(3.9) + str(";") + str(quality)
    #Y
    t_edz_left["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    t_edz_left["data"]["matrix"][1][1] = str(6.45) + str(";") + str(quality)
    #Z
    t_edz_left["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    t_edz_left["data"]["matrix"][2][1] = str(7.11) + str(";") + str(quality)

    with open('T_edz_left.yaml', 'w') as outfile:
        yaml.dump(t_edz_left, outfile)

    return length

def resizing_rao(concrete_X: float, bentonite_X: float, quality: float) -> float:
    # RW_concrete_bent.yaml
    with open('RW_concrete_bent_layers.yaml') as f:
        RW_concrete_bent = yaml.full_load(f)

    # do smth with yml file
    # X
    RW_concrete_bent["data"]["layer"][0][0] = str(0.125) + str(";") + str(quality)
    RW_concrete_bent["data"]["layer"][0][1] = str(0.35) + str(";") + str(quality)
    # resising concrete
    RW_concrete_bent["data"]["layer"][0][2] = str(concrete_X) + str(";") + str(quality)
    # resizing bentonite
    RW_concrete_bent["data"]["layer"][0][3] = str(bentonite_X) + str(";") + str(quality)
    # Y
    RW_concrete_bent["data"]["layer"][1][0] = str(0.125) + str(";") + str(quality)
    RW_concrete_bent["data"]["layer"][1][1] = str(0.35) + str(";") + str(quality)
    RW_concrete_bent["data"]["layer"][1][2] = str(0.6) + str(";") + str(quality)
    RW_concrete_bent["data"]["layer"][1][3] = str(1) + str(";") + str(quality)
    # Z
    # RW_concrete_bent["data"]["layer"][2][0] = str(0.5) + str(";") + str(quality)
    RW_concrete_bent["data"]["layer"][2][0] = str(0.55) + str(";") + str(quality)
    RW_concrete_bent["data"]["layer"][2][1] = str(3.91) + str(";") + str(quality)
    RW_concrete_bent["data"]["layer"][2][2] = str(4.5) + str(";") + str(quality)
    RW_concrete_bent["data"]["layer"][2][3] = str(5) + str(";") + str(quality)

    with open('RW_concrete_bent_layers.yaml', 'w') as outfile:
        yaml.dump(RW_concrete_bent, outfile)
    # end RW_concrete_bent.yaml
    block_of_rao = bentonite_X
    return block_of_rao

def resizing_buffer(buff: float, quality: float, length_X: float) -> float:
    '''size of bentonite buffer'''
    data_loaded = {}
    #R_bent_sides.yaml
    with open('R_bent_sides.yaml') as f:
        data_loaded = yaml.full_load(f)

    #creating bent_sides of buff
    #X
    data_loaded["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    data_loaded["data"]["matrix"][0][1] = str(buff) + str(";") + str(quality)
    data_loaded["data"]["matrix"][0][2] = str(length_X * 2 + buff) + str(";") + str(quality)
    data_loaded["data"]["matrix"][0][3] = str(length_X * 2 + 2 * buff) + str(";") + str(quality)
    #Y
    data_loaded["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    data_loaded["data"]["matrix"][1][1] = str(2) + str(";") + str(quality)
    #Z
    data_loaded["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    data_loaded["data"]["matrix"][2][1] = str(5.0) + str(";") + str(quality)

    block_length = length_X * 2 + 2 * buff# 3.6 via X
    with open('R_bent_sides.yaml', 'w') as outfile:
        yaml.dump(data_loaded, outfile)
    #end R_bent_sides.yaml
    return block_length

def resizing_tranches(n_RAO: int, block_length: float, quality: float, concrete_X: float, bentonite_X: float) -> float:
    '''length of tranches'''\
    #R_edz.yaml
    with open('R_edz.yaml') as f:
        r_edz = yaml.full_load(f)

    #do smth with yml file
    #X
    r_edz["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    r_edz["data"]["matrix"][0][1] = str(block_length) + str(";") + str(quality)
    #Y
    r_edz["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    r_edz["data"]["matrix"][1][1] = str(0.3) + str(";") + str(quality)
    r_edz["data"]["matrix"][1][2] = str(2.3) + str(";") + str(quality)
    r_edz["data"]["matrix"][1][3] = str(2.6) + str(";") + str(quality)
    #Z
    r_edz["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    r_edz["data"]["matrix"][2][1] = str(0.3) + str(";") + str(quality)
    r_edz["data"]["matrix"][2][2] = str(5.3) + str(";") + str(quality)
    r_edz["data"]["items_children_transforms"][0][0][0][0] = 0 - (block_length / 2)

    with open('R_edz.yaml', 'w') as outfile:
        yaml.dump(r_edz, outfile)
    #end R_edz.yaml

    #R_edz_left.yaml
    with open('R_edz_left.yaml') as f:
        r_edz_left = yaml.full_load(f)

    #do smth with yml file
    #X
    r_edz_left["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    r_edz_left["data"]["matrix"][0][1] = str(0.3) + str(";") + str(quality)
    r_edz_left["data"]["matrix"][0][2] = str(0.3 + block_length) + str(";") + str(quality)
    #Y
    r_edz_left["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    r_edz_left["data"]["matrix"][1][1] = str(2.6) + str(";") + str(quality)
    #Z
    r_edz_left["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    r_edz_left["data"]["matrix"][2][1] = str(5.3) + str(";") + str(quality)
    r_edz_left["data"]["items_children_transforms"][0][0][0][0] = 0 - (block_length / 2)

    with open('R_edz_left.yaml', 'w') as outfile:
        yaml.dump(r_edz_left, outfile)
    #end R_edz_left.yaml

    #R_edz_right.yaml
    with open('R_edz_right.yaml') as f:
        r_edz_right = yaml.full_load(f)

    #do smth with yml file
    #X
    r_edz_right["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    r_edz_right["data"]["matrix"][0][1] = str(block_length) + str(";") + str(quality)
    r_edz_right["data"]["matrix"][0][2] = str(block_length + 0.3) + str(";") + str(quality)
    #Y
    r_edz_right["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    r_edz_right["data"]["matrix"][1][1] = str(2.6) + str(";") + str(quality)
    #Z
    r_edz_right["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    r_edz_right["data"]["matrix"][2][1] = str(5.3) + str(";") + str(quality)
    r_edz_right["data"]["items_children_transforms"][0][0][0][0] = 0 - (block_length / 2)

    with open('R_edz_right.yaml', 'w') as outfile:
        yaml.dump(r_edz_right, outfile)
    #end R_edz_right.yaml

    #R_edz_tranch.yaml
    with open('R_edz_tranch.yaml') as f:
        r_edz_trunch = yaml.full_load(f)

    #do smth with yml file
    tmp = int(n_RAO) - 2
    tmp2 = block_length
    #X
    r_edz_trunch["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    r_edz_trunch["data"]["matrix"][0][1] = str(tmp2 + 0.3) + str(";") + str(quality)
    r_edz_trunch["data"]["matrix"][0][2] = str(tmp2 * tmp + float(str(r_edz_trunch["data"]["matrix"][0][1]).split(";")[0])) + \
                                           str(":") + str(tmp+1) + str(";") + str(quality)
    r_edz_trunch["data"]["matrix"][0][3] = str(float(r_edz_trunch["data"]["matrix"][0][1].split(";")[0]) + \
                                           (tmp2 * tmp + float(r_edz_trunch["data"]["matrix"][0][1].split(";")[0]))) + \
                                           str(";") + str(quality)

    tranch_r_length = float(str(r_edz_trunch["data"]["matrix"][0][3]).split(";")[0])
    #Y
    r_edz_trunch["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    r_edz_trunch["data"]["matrix"][1][1] = str(2.6) + str(";") + str(quality)
    #Z
    r_edz_trunch["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    r_edz_trunch["data"]["matrix"][2][1] = str(5.3) + str(";") + str(quality)
    #workaround transformations
    r_edz_trunch["data"]["items_children_transforms"][0][0][0][0] = 0 - (block_length / 2)
    r_edz_trunch["data"]["items_children_transforms"][1][0][0][0] = 0 - ((tmp2 + 0.3) / 2)

    with open('R_edz_tranch.yaml', 'w') as outfile:
        yaml.dump(r_edz_trunch, outfile)
    #end R_edz_tranch.yaml

    #T_edz_tranch.yaml
    with open('T_edz_tranch.yaml') as f:
        t_edz_tranch = yaml.full_load(f)

    middle = rebuild_t_edz((tranch_r_length - 3.9 * 2), quality)
    #do smth with yml file
    #X
    t_edz_tranch["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    t_edz_tranch["data"]["matrix"][0][1] = str(3.9) + str(";") + str(quality)
    t_edz_tranch["data"]["matrix"][0][2] = str(middle + 3.9) + str(";") + str(quality)
    t_edz_tranch["data"]["matrix"][0][3] = str(float(t_edz_tranch["data"]["matrix"][0][2].split(";")[0]) + 3.9) + \
                                           str(";") + str(quality)
    #Y
    t_edz_tranch["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    t_edz_tranch["data"]["matrix"][1][1] = str(6.45) + str(";") + str(quality)
    #Z
    t_edz_tranch["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    t_edz_tranch["data"]["matrix"][2][1] = str(7.11) + str(";") + str(quality)
    t_edz_tranch["data"]["items_children_transforms"][1][0][0][0] = 0 - middle / 2

    with open('T_edz_tranch.yaml', 'w') as outfile:
        yaml.dump(t_edz_tranch, outfile)
    #end T_edz_tranch.yaml

    #Plug_tranch.yaml
    with open('Plug_tranch.yaml') as f:
        plug_tranch = yaml.full_load(f)

    #do smth with yml file
    tranch_length = 3.6 * (tmp + 1)
    #X
    plug_tranch["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    plug_tranch["data"]["matrix"][0][1] = str(3.6) + str(";") + str(quality)
    plug_tranch["data"]["matrix"][0][2] = str(tranch_r_length) + str(";") + str(quality)
    #Y
    plug_tranch["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    plug_tranch["data"]["matrix"][1][1] = str(6.45) + str(";") + str(quality)
    #Z
    plug_tranch["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    plug_tranch["data"]["matrix"][2][1] = str(0.6) + str(";") + str(quality)

    with open('Plug_tranch.yaml', 'w') as outfile:
        yaml.dump(plug_tranch, outfile)
    #end Plug_tranch.yaml

    # RW_concrete_bent.yaml
    #with open('RW_concrete_bent_layers.yaml') as f:
    #    RW_concrete_bent = yaml.full_load(f)

    # do smth with yml file
    #X
    #RW_concrete_bent["data"]["layer"][0][0] = str(0.125) + str(";") + str(quality)
    #RW_concrete_bent["data"]["layer"][0][1] = str(0.35) + str(";") + str(quality)
    #resising concrete
    #RW_concrete_bent["data"]["layer"][0][2] = str(concrete_X) + str(";") + str(quality)
    #resizing bentonite
    #RW_concrete_bent["data"]["layer"][0][3] = str(bentonite_X) + str(";") + str(quality)
    #Y
    #RW_concrete_bent["data"]["layer"][1][0] = str(0.125) + str(";") + str(quality)
    #RW_concrete_bent["data"]["layer"][1][1] = str(0.35) + str(";") + str(quality)
    #RW_concrete_bent["data"]["layer"][1][2] = str(0.6) + str(";") + str(quality)
    #RW_concrete_bent["data"]["layer"][1][3] = str(1) + str(";") + str(quality)
    #Z
    ##RW_concrete_bent["data"]["layer"][2][0] = str(0.5) + str(";") + str(quality)
    #RW_concrete_bent["data"]["layer"][2][0] = str(0.55) + str(";") + str(quality)
    #RW_concrete_bent["data"]["layer"][2][1] = str(3.91) + str(";") + str(quality)
    #RW_concrete_bent["data"]["layer"][2][2] = str(4.5) + str(";") + str(quality)
    #RW_concrete_bent["data"]["layer"][2][3] = str(5) + str(";") + str(quality)

    #with open('RW_concrete_bent_layers.yaml', 'w') as outfile:
    #    yaml.dump(RW_concrete_bent, outfile)
    # end RW_concrete_bent.yaml
    return tranch_r_length

#result.yaml
def resize_result(env_X: float, env_Y: float, env_Z_bottom: float, env_Z_top: float, tranch: float, env_quality: float):
#def resize_result(env_X: float, env_Y: float, env_Z: float, tranch: float, env_quality: float):
    with open('result.yaml') as f:
        result = yaml.full_load(f)

    #do smth with yml file
    #X
    result["data"]["matrix"][0][0] = str(0) + str(";") + str(env_quality)
    result["data"]["matrix"][0][1] = str(env_X) + str(";") + str(env_quality)

    #Y
    result["data"]["matrix"][1][0] = str(0) + str(";") + str(env_quality)
    result["data"]["matrix"][1][1] = str(env_Y) + str(";") + str(env_quality)

    #Z
    result["data"]["matrix"][2][0] = str(0) + str(";") + str(env_quality)
    result["data"]["matrix"][2][1] = str(env_Z_bottom + env_Z_top + 13.01) + str(";") + str(env_quality)
    #result["data"]["matrix"][2][1] = str(env_Z_bottom) + str(";") + str(env_quality)
    #result["data"]["matrix"][2][2] = str(float(result["data"]["matrix"][2][1].split(";")[0]) + 12.2) + str(";") + str(env_quality)
    #result["data"]["matrix"][2][3] = str(float(result["data"]["matrix"][2][2].split(";")[0]) + env_Z_top) + str(";") + str(env_quality)

    #shifting tranch inside env
    #X
    result["data"]["items_children_transforms"][0][0][0][0] = 0 - tranch / 2
    #Y
    result["data"]["items_children_transforms"][0][0][0][1] = 0 - 6.45 / 2
    #Z
    z_all = env_Z_top + env_Z_bottom + 13.01
    z_curr_top = z_all / 2 - 7.71
    z_curr_bottom = z_all / 2 - 5.3
    delta_z_bottom = abs(env_Z_bottom - z_curr_bottom)
    delta_z_top = abs(env_Z_top - z_curr_top)
    #print(delta_z_top, delta_z_bottom)
    if env_Z_bottom < env_Z_top:
        shift = 0 - delta_z_top
    else: shift = delta_z_top
    result["data"]["items_children_transforms"][0][0][0][2] = shift#- 13.01 / 2
    #set quality
    #result["metadata"]["options"]["Mesh.MeshSizeFactor"] = quality

    with open('result.yaml', 'w') as outfile:
        yaml.dump(result, outfile)

if __name__ == "__main__":
    '''The goal is to rescale the length of resulting tranch 
    and the size of a bent_buffer. Modifying the bent_buff in R_bent_sides.yaml
    and the length in R_edz.yaml, R_edz_left.yaml, R_edz_right, R_edz_trunch.yaml.yaml,
    T_edz_trunch.yaml, T_edz.yaml, T_edz_left.yaml, T_edz_right.yaml, Plug_tranch.yaml'''
    #sys.argv[0] is a script name
    # To call python ./build_result.py with parameters:
    #1 N_of_rao
    #2 concrete_X
    #3 bentonite_X
    #4 buff_size
    #5 rao_quality
    #6 env_X
    #7 env_Y
    #8 env_Z_botoom
    #9 env_Z_top
    #10 env_quality
    #python. / build_result.py N_of_rao concrete_X bentonite_X buff_size rao_quality env_X env_Y env_Z_botoom env_Z_top env_quality
    n_of_rao = int(sys.argv[1])
    concrete_X = float(sys.argv[2])
    bentonite_X = float(sys.argv[3])
    buff_size = float(sys.argv[4])
    quality_rao = float(sys.argv[5])
    env_X = float(sys.argv[6])
    env_Y = float(sys.argv[7])
    env_Z_bottom = float(sys.argv[8])
    env_Z_top = float(sys.argv[9])
    quality_env = float(sys.argv[10])
    if concrete_X > bentonite_X or concrete_X == bentonite_X:
        print("Sizes of concrete and bentonite are wrong. Check sizes!")
        exit(1)
    #env_Z = float(sys.argv[6])
    #quality_env = float(sys.argv[7])
    single_block_length = resizing_rao(concrete_X, bentonite_X, quality_rao)
    block = resizing_buffer(buff_size, quality_rao, bentonite_X)
    tranch = resizing_tranches(n_of_rao, block, quality_rao, concrete_X, bentonite_X)
    if tranch > env_X or 5.6 > env_Y:
        print("Size of env cant be less than tranch size.")
        exit(1)
    resize_result(env_X, env_Y, env_Z_bottom, env_Z_top, tranch, quality_env)
    #resize_result(env_X, env_Y, env_Z, tranch, quality_env)
