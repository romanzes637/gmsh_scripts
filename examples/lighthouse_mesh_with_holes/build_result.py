import yaml
import sys
import math

#env.yaml
def resize_mesh(env_0: float,
                env_0_XY: float,
                concrete_0: float,
                concrete_1: float,
                env_1_Z: float,
                l1: float,
                l2: float,
                l3: float,
                l4: float,
                h1: float,
                h2: float,
                quality: float,
                quality_env: float):
    # with open('concrete_1_small.yaml') as f0:
    #     c_1_s = yaml.full_load(f0)
    with open('env+buildings.yaml') as f1:
        e_b = yaml.full_load(f1)
    # with open('long_building.yaml') as f2:
    #     long_b = yaml.full_load(f2)
    with open('result.yaml') as f3:
        result = yaml.full_load(f3)
    # with open('RW+Sand.yaml') as f4:
    #     RW = yaml.full_load(f4)
    # with open('small_building.yaml') as f5:
    #     small_b = yaml.full_load(f5)
    with open('concrete_up.yaml') as f6:
        c_u = yaml.full_load(f6)

    #Some vars here for moving elements
    len = 9.5 + concrete_0 * 2 # len of single container with concrete_0 in X
    #len_whole = len * 2 + 27 + len * 2
    m = abs(l1 - l2) / 2
    k = abs(l1 - l3) / 2
    n = abs(h2 - h1) / 2
    v = abs(l1 - l4) / 2
    l_small = abs(l1 - len * 3) / 2

    # #Workaround RW+Sand
    # RW["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    # RW["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality) #str(20) + str(";") + str(quality)
    #
    # RW["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    # RW["data"]["matrix"][1][1] = str(20) + str(";") + str(quality) #str(9.5) + str(";") + str(quality)
    #
    # RW["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    # RW["data"]["matrix"][2][1] = str(2.6) + str(";") + str(quality)
    # RW["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)

    #Workaround container
    # c_1_s["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    # c_1_s["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality) #str(20 + concrete_0 * 2) + str(";") + str(quality)
    #
    # c_1_s["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    # c_1_s["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality) #str(9.5 + concrete_0 * 2) + str(";") + str(quality)
    #
    # c_1_s["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    # c_1_s["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)
    #
    # c_1_s["data"]["children_transforms"][0][0][0] = concrete_0
    # c_1_s["data"]["children_transforms"][0][0][1] = concrete_0
    # c_1_s["data"]["children_transforms"][0][0][2] = concrete_0

    #Workaround small building
    # small_b["data"]["children_transforms"][1][0][0] = 9.5 + concrete_0 * 2
    # small_b["data"]["children_transforms"][2][0][0] = (9.5 + concrete_0 * 2) * 2
    # #small_b["data"]["children_transforms"][3][0][0] = (9.5 + concrete_0 * 2) * 3
    # small_b["data"]["children_transforms"][3][0][1] = 20 + concrete_0 * 2
    # small_b["data"]["children_transforms"][4][0][0] = 9.5 + concrete_0 * 2
    # small_b["data"]["children_transforms"][4][0][1] = 20 + concrete_0 * 2
    # small_b["data"]["children_transforms"][5][0][0] = (9.5 + concrete_0 * 2) * 2
    # small_b["data"]["children_transforms"][5][0][1] = 20 + concrete_0 * 2
    # small_b["data"]["children_transforms"][6][0][0] = (20 + concrete_0 * 2) * 2
    # small_b["data"]["children_transforms"][6][0][1] = (9.5 + concrete_0 * 2) * 3

    # small_b["data"]["children_transforms"][1][0][1] = 20 + concrete_0 * 2#9.5 + concrete_0 * 2
    # small_b["data"]["children_transforms"][2][0][1] = (20 + concrete_0 * 2) * 2#(9.5 + concrete_0 * 2) * 2
    # small_b["data"]["children_transforms"][3][0][0] = 9.5 + concrete_0 * 2#20 + concrete_0 * 2
    # small_b["data"]["children_transforms"][4][0][0] = 9.5 + concrete_0 * 2#20 + concrete_0 * 2
    # small_b["data"]["children_transforms"][4][0][1] = 20 + concrete_0 * 2#9.5 + concrete_0 * 2
    # small_b["data"]["children_transforms"][5][0][0] = 9.5 + concrete_0 * 2#20 + concrete_0 * 2
    # small_b["data"]["children_transforms"][5][0][1] = (20 + concrete_0 * 2) * 2#(9.5 + concrete_0 * 2) * 2

    #Workaround long building
    # long_b["data"]["children_transforms"][1][0][0] = (9.5 + concrete_0 * 2) * 3
    # long_b["data"]["children_transforms"][2][0][0] = (9.5 + concrete_0 * 2) * 6#((9.5 + concrete_0 * 2) * 3) * 2
    # long_b["data"]["children_transforms"][3][0][0] = (9.5 + concrete_0 * 2) * 6#20 + concrete_0 * 2
    # long_b["data"]["children_transforms"][3][0][1] = 20 + concrete_0 * 2#((9.5 + concrete_0 * 2) * 3) * 2

    #Workaround env+buildings
    #workaround floor
    e_b["data"]["points"][0][0] = round(l1 - (concrete_1 * math.cos(45)), 2) #TODO check if it moves corrdctly with concrete_1
    e_b["data"]["points"][0][1] = round(h2 - (concrete_1 * math.sin(45)), 2)
    e_b["data"]["points"][0][2] = 0
    e_b["data"]["points"][0][3] = quality

    e_b["data"]["points"][1][0] = round(concrete_1 * math.cos(45), 2)
    e_b["data"]["points"][1][1] = round(h2 - (concrete_1 * math.sin(45)), 2)
    e_b["data"]["points"][1][2] = 0
    e_b["data"]["points"][1][3] = quality

    e_b["data"]["points"][2][0] = round(m + (concrete_1 * math.cos(45)), 2)
    e_b["data"]["points"][2][1] = round(concrete_1 * math.sin(45), 2)
    e_b["data"]["points"][2][2] = 0
    e_b["data"]["points"][2][3] = quality

    e_b["data"]["points"][3][0] = round(m + l2 - (concrete_1 * math.cos(45)), 2)
    e_b["data"]["points"][3][1] = round(concrete_1 * math.sin(45), 2)
    e_b["data"]["points"][3][2] = 0
    e_b["data"]["points"][3][3] = quality

    #Workaroun roof
    e_b["data"]["points"][4][0] = round(k + l3 - (concrete_1 * math.cos(45)), 2) #k + l3 - concrete_1
    e_b["data"]["points"][4][1] = round(n + h1 - (concrete_1 * math.sin(45)), 2)#n + h1 - concrete_1
    e_b["data"]["points"][4][2] = env_1_Z - concrete_1#round(env_1_Z - (concrete_1 * math.sin(45)), 2)
    e_b["data"]["points"][4][3] = quality

    e_b["data"]["points"][5][0] = round(k + (concrete_1 * math.cos(45)), 2)#k + concrete_1
    e_b["data"]["points"][5][1] = round(n + h1 - (concrete_1 * math.sin(45)), 2)#n + h1 - concrete_1
    e_b["data"]["points"][5][2] = env_1_Z - concrete_1#round(env_1_Z - (concrete_1 * math.sin(45)), 2)
    e_b["data"]["points"][5][3] = quality

    e_b["data"]["points"][6][0] = round(v + (concrete_1 * math.cos(45)), 2)#v + concrete_1
    e_b["data"]["points"][6][1] = round(n + (concrete_1 * math.sin(45)), 2)#n #+ concrete_1
    e_b["data"]["points"][6][2] = env_1_Z - concrete_1#round(env_1_Z - (concrete_1 * math.sin(45)), 2)
    e_b["data"]["points"][6][3] = quality

    e_b["data"]["points"][7][0] = round(v + l4 - (concrete_1 * math.cos(45)), 2)#v + l4 - concrete_1
    e_b["data"]["points"][7][1] = round(n + (concrete_1 * math.sin(45)), 2)#n #+ concrete_1
    e_b["data"]["points"][7][2] = env_1_Z - concrete_1#round(env_1_Z - (concrete_1 * math.sin(45)), 2)
    e_b["data"]["points"][7][3] = quality

    #size of buildings in y = (20+concrete_0*2)*4 + 27
    #Workaround small building
    e_b["data"]["children_transforms"][0][0][0] = l_small#X
    e_b["data"]["children_transforms"][0][0][1] = abs((h2 - concrete_1 * 2) - ((20 + concrete_0 * 2) * 4 + 27)) / 2# middle of h2

    #Workaround long building
    e_b["data"]["children_transforms"][1][0][0] = abs(l1 - (9.5 + concrete_0 * 2) * 7) / 2#X
    e_b["data"]["children_transforms"][1][0][1] = (abs((h2 - concrete_1 * 2) - ((20 + concrete_0 * 2) * 4) + 27) / 2) + 27 + (20 + concrete_0 * 2)

    #Workaround concrete_up
    #floor points with right hand numeration
    c_u["data"]["points"][0][0] = l1
    c_u["data"]["points"][0][1] = h2
    c_u["data"]["points"][0][2] = 0
    c_u["data"]["points"][0][3] = quality

    c_u["data"]["points"][1][0] = 0
    c_u["data"]["points"][1][1] = h2
    c_u["data"]["points"][1][2] = 0
    c_u["data"]["points"][1][3] = quality

    c_u["data"]["points"][2][0] = m
    c_u["data"]["points"][2][1] = 0
    c_u["data"]["points"][2][2] = 0
    c_u["data"]["points"][2][3] = quality

    c_u["data"]["points"][3][0] = m + l2
    c_u["data"]["points"][3][1] = 0
    c_u["data"]["points"][3][2] = 0
    c_u["data"]["points"][3][3] = quality

    #roof points with right hadn numeration
    c_u["data"]["points"][4][0] = k + l3
    c_u["data"]["points"][4][1] = n + h1
    c_u["data"]["points"][4][2] = env_1_Z #+ concrete_1
    c_u["data"]["points"][4][3] = quality

    c_u["data"]["points"][5][0] = k
    c_u["data"]["points"][5][1] = n + h1
    c_u["data"]["points"][5][2] = env_1_Z #+ concrete_1
    c_u["data"]["points"][5][3] = quality

    c_u["data"]["points"][6][0] = v
    c_u["data"]["points"][6][1] = n
    c_u["data"]["points"][6][2] = env_1_Z #+ concrete_1
    c_u["data"]["points"][6][3] = quality

    c_u["data"]["points"][7][0] = v + l4
    c_u["data"]["points"][7][1] = n
    c_u["data"]["points"][7][2] = env_1_Z #+ concrete_1
    c_u["data"]["points"][7][3] = quality
    c_u["data"]["children_transforms"][0][0][0] = 0#concrete_1 #60 + (9.5 + concrete_0 * 2) * 2
    c_u["data"]["children_transforms"][0][0][1] = 0#concrete_1
    # c_u["data"]["children_transforms"][1][0][0] = 190 - 40 - (20 + concrete_0 * 2) * 2

    #Workaround result
    result["data"]["matrix"][0][0] = str(0) + str(";") + str(quality_env)
    result["data"]["matrix"][0][1] = str(env_0_XY) + str(";") + str(quality_env)

    result["data"]["matrix"][1][0] = str(0) + str(";") + str(quality_env)
    result["data"]["matrix"][1][1] = str(env_0_XY) + str(";") + str(quality_env)

    result["data"]["matrix"][2][0] = str(0) + str(";") + str(quality_env)
    result["data"]["matrix"][2][1] = str(env_0) + str(";") + str(quality_env)

    result["data"]["children_transforms"][0][0][0] = abs(env_0_XY - l1 + concrete_1) / 2
    result["data"]["children_transforms"][0][0][1] = abs(env_0_XY - l1 + concrete_1) / 2
    result["data"]["children_transforms"][0][0][2] = env_0


    # with open('concrete_1_small.yaml', 'w') as outfile:
    #     yaml.dump(c_1_s, outfile)
    with open('env+buildings.yaml', 'w') as outfile:
        yaml.dump(e_b, outfile)
    # with open('long_building.yaml', 'w') as outfile:
    #     yaml.dump(long_b, outfile)
    with open('result.yaml', 'w') as outfile:
        yaml.dump(result, outfile)
    # with open('RW+Sand.yaml', 'w') as outfile:
    #     yaml.dump(RW, outfile)
    # with open('small_building.yaml', 'w') as outfile:
    #     yaml.dump(small_b, outfile)
    with open('concrete_up.yaml', 'w') as outfile:
        yaml.dump(c_u, outfile)

if __name__ == "__main__":
    '''The goal is to rescale the length of resulting mesh. We change ENV in +X -X simultaneously,
     ENV in +Y -Y separately, rescaling tube with ENV in Z. Changing mesh quality for ENV separately from the main mesh'''
    #sys.argv[0] is a script name
    # To call python ./build_result.py with parameters:
    #1 env_0 - size of env_0 in Z
    #2 env_0_XY - size of env_0 in XY
    #3 concrete_0 - size of concrete_0 around RW+Sand
    #4 concrete_1 - size of concrete_1 around buildings
    #5 env_1 - size of env_1 in Z
    #7 quality
    #8 quality_env
    #python. / build_result.py %pars%
    env_0_Z = float(sys.argv[1])
    env_0_XY = float(sys.argv[2])
    concrete_0 = float(sys.argv[3])
    concrete_1 = float(sys.argv[4])
    env_1_Z = float(sys.argv[5])
    l1 = float(sys.argv[6])
    l2 = float(sys.argv[7])
    l3 = float(sys.argv[8])
    l4 = float(sys.argv[9])
    h1 = float(sys.argv[10])
    h2 = float(sys.argv[11])
    quality = float(sys.argv[12])
    quality_env = float(sys.argv[13])
    resize_mesh(env_0_Z, env_0_XY, concrete_0, concrete_1, env_1_Z, l1, l2, l3, l4, h1, h2, quality, quality_env)
