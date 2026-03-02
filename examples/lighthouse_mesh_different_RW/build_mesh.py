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
                quality_env: float,
                RW_size: float):

    with open('concrete_1_small_1.yaml') as f0_1:
        c_1_s_1 = yaml.full_load(f0_1)
    with open('concrete_1_small_2.yaml') as f0_2:
        c_1_s_2 = yaml.full_load(f0_2)
    with open('concrete_1_small_3.yaml') as f0_3:
        c_1_s_3 = yaml.full_load(f0_3)
    with open('concrete_1_small_4.yaml') as f0_4:
        c_1_s_4 = yaml.full_load(f0_4)
    with open('concrete_1_small_5.yaml') as f0_5:
        c_1_s_5 = yaml.full_load(f0_5)
    with open('concrete_1_small_6.yaml') as f0_6:
        c_1_s_6 = yaml.full_load(f0_6)
    with open('concrete_1_small_7.yaml') as f0_7:
        c_1_s_7 = yaml.full_load(f0_7)
    with open('concrete_1_small_8.yaml') as f0_8:
        c_1_s_8 = yaml.full_load(f0_8)
    with open('concrete_1_small_9.yaml') as f0_9:
        c_1_s_9 = yaml.full_load(f0_9)
    with open('concrete_1_small_10.yaml') as f0_10:
        c_1_s_10 = yaml.full_load(f0_10)
    with open('concrete_1_small_11.yaml') as f0_11:
        c_1_s_11 = yaml.full_load(f0_11)
    with open('concrete_1_small_12.yaml') as f0_12:
        c_1_s_12 = yaml.full_load(f0_12)
    with open('concrete_1_small_13.yaml') as f0_13:
        c_1_s_13 = yaml.full_load(f0_13)
    with open('concrete_1_small_14.yaml') as f0_14:
        c_1_s_14 = yaml.full_load(f0_14)
    with open('concrete_1_small_15.yaml') as f0_15:
        c_1_s_15 = yaml.full_load(f0_15)
    with open('concrete_1_small_16.yaml') as f0_16:
        c_1_s_16 = yaml.full_load(f0_16)
    with open('concrete_1_small_17.yaml') as f0_17:
        c_1_s_17 = yaml.full_load(f0_17)
    with open('concrete_1_small_18.yaml') as f0_18:
        c_1_s_18 = yaml.full_load(f0_18)
    with open('concrete_1_small_19.yaml') as f0_19:
        c_1_s_19 = yaml.full_load(f0_19)
    with open('concrete_1_small_20.yaml') as f0_20:
        c_1_s_20 = yaml.full_load(f0_20)

    with open('env+buildings.yaml') as f1:
        e_b = yaml.full_load(f1)
    with open('long_building.yaml') as f2:
        long_b = yaml.full_load(f2)
    with open('result.yaml') as f3:
        result = yaml.full_load(f3)

    with open('RW+Sand_1.yaml') as f4_1:
        RW_1 = yaml.full_load(f4_1)
    with open('RW+Sand_2.yaml') as f4_2:
        RW_2 = yaml.full_load(f4_2)
    with open('RW+Sand_3.yaml') as f4_3:
        RW_3 = yaml.full_load(f4_3)
    with open('RW+Sand_4.yaml') as f4_4:
        RW_4 = yaml.full_load(f4_4)
    with open('RW+Sand_5.yaml') as f4_5:
        RW_5 = yaml.full_load(f4_5)
    with open('RW+Sand_6.yaml') as f4_6:
        RW_6 = yaml.full_load(f4_6)
    with open('RW+Sand_7.yaml') as f4_7:
        RW_7 = yaml.full_load(f4_7)
    with open('RW+Sand_8.yaml') as f4_8:
        RW_8 = yaml.full_load(f4_8)
    with open('RW+Sand_9.yaml') as f4_9:
        RW_9 = yaml.full_load(f4_9)
    with open('RW+Sand_10.yaml') as f4_10:
        RW_10 = yaml.full_load(f4_10)
    with open('RW+Sand_11.yaml') as f4_11:
        RW_11 = yaml.full_load(f4_11)
    with open('RW+Sand_12.yaml') as f4_12:
        RW_12 = yaml.full_load(f4_12)
    with open('RW+Sand_13.yaml') as f4_13:
        RW_13 = yaml.full_load(f4_13)
    with open('RW+Sand_14.yaml') as f4_14:
        RW_14 = yaml.full_load(f4_14)
    with open('RW+Sand_15.yaml') as f4_15:
        RW_15 = yaml.full_load(f4_15)
    with open('RW+Sand_16.yaml') as f4_16:
        RW_16 = yaml.full_load(f4_16)
    with open('RW+Sand_17.yaml') as f4_17:
        RW_17 = yaml.full_load(f4_17)
    with open('RW+Sand_18.yaml') as f4_18:
        RW_18 = yaml.full_load(f4_18)
    with open('RW+Sand_19.yaml') as f4_19:
        RW_19 = yaml.full_load(f4_19)
    with open('RW+Sand_20.yaml') as f4_20:
        RW_20 = yaml.full_load(f4_20)

    with open('small_building.yaml') as f5:
        small_b = yaml.full_load(f5)
    with open('small_building_2.yaml') as f5_2:
        small_b_2 = yaml.full_load(f5_2)
    with open('small_building_3.yaml') as f5_3:
        small_b_3 = yaml.full_load(f5_3)

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
    RW_1["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_1["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_1["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_1["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_1["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_1["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_1["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    #____________________________________________________________

    RW_2["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_2["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_2["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_2["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_2["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_2["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_2["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________

    RW_3["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_3["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_3["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_3["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_3["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_3["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_3["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_4["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_4["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_4["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_4["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_4["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_4["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_4["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_5["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_5["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_5["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_5["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_5["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_5["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_5["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_6["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_6["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_6["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_6["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_6["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_6["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_6["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_7["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_7["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_7["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_7["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_7["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_7["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_7["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_8["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_8["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_8["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_8["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_8["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_8["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_8["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_9["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_9["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_9["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_9["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_9["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_9["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_9["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_10["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_10["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_10["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_10["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_10["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_10["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_10["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_11["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_11["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_11["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_11["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_11["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_11["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_11["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_12["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_12["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_12["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_12["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_12["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_12["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_12["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_13["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_13["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_13["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_13["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_13["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_13["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_13["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_14["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_14["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_14["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_14["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_14["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_14["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_14["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_15["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_15["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_15["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_15["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_15["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_15["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_15["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_16["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_16["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_16["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_16["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_16["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_16["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_16["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_17["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_17["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_17["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_17["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_17["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_17["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_17["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_18["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_18["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_18["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_18["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_18["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_18["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_18["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_19["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_19["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_19["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_19["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_19["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_19["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_19["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________
    RW_20["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    RW_20["data"]["matrix"][0][1] = str(9.5) + str(";") + str(quality)

    RW_20["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    RW_20["data"]["matrix"][1][1] = str(20) + str(";") + str(quality)

    RW_20["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    RW_20["data"]["matrix"][2][1] = str(RW_size) + str(";") + str(quality)
    RW_20["data"]["matrix"][2][2] = str(7) + str(";") + str(quality)
    # ____________________________________________________________

    #Workaround container

    c_1_s_1["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_1["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_1["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_1["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_1["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_1["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_1["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_1["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_1["data"]["children_transforms"][0][0][2] = concrete_0
    #__________________________________________________________
    c_1_s_2["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_2["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_2["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_2["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_2["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_2["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_2["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_2["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_2["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_3["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_3["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_3["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_3["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_3["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_3["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_3["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_3["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_3["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_4["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_4["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_4["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_4["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_4["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_4["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_4["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_4["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_4["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_5["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_5["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_5["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_5["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_5["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_5["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_5["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_5["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_5["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_6["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_6["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_6["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_6["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_6["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_6["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_6["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_6["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_6["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_7["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_7["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_7["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_7["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_7["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_7["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_7["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_7["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_7["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_8["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_8["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_8["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_8["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_8["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_8["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_8["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_8["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_8["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_9["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_9["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_9["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_9["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_9["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_9["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_9["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_9["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_9["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_10["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_10["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_10["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_10["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_10["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_10["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_10["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_10["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_10["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_11["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_11["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_11["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_11["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_11["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_11["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_11["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_11["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_11["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_12["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_12["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_12["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_12["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_12["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_12["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_12["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_12["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_12["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_13["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_13["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_13["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_13["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_13["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_13["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_13["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_13["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_13["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_14["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_14["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_14["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_14["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_14["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_14["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_14["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_14["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_14["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_15["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_15["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_15["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_15["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_15["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_15["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_15["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_15["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_15["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_16["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_16["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_16["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_16["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_16["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_16["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_16["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_16["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_16["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_17["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_17["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_17["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_17["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_17["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_17["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_17["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_17["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_17["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_18["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_18["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_18["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_18["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_18["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_18["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_18["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_18["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_18["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_19["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_19["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_19["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_19["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_19["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_19["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_19["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_19["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_19["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________
    c_1_s_20["data"]["matrix"][0][0] = str(0) + str(";") + str(quality)
    c_1_s_20["data"]["matrix"][0][1] = str(9.5 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_20["data"]["matrix"][1][0] = str(0) + str(";") + str(quality)
    c_1_s_20["data"]["matrix"][1][1] = str(20 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_20["data"]["matrix"][2][0] = str(0) + str(";") + str(quality)
    c_1_s_20["data"]["matrix"][2][1] = str(7 + concrete_0 * 2) + str(";") + str(quality)

    c_1_s_20["data"]["children_transforms"][0][0][0] = concrete_0
    c_1_s_20["data"]["children_transforms"][0][0][1] = concrete_0
    c_1_s_20["data"]["children_transforms"][0][0][2] = concrete_0
    # __________________________________________________________

    #Workaround small building

    small_b["data"]["children_transforms"][1][0][0] = 9.5 + concrete_0 * 2
    small_b["data"]["children_transforms"][2][0][0] = (9.5 + concrete_0 * 2) * 2
    small_b["data"]["children_transforms"][3][0][1] = 20 + concrete_0 * 2
    small_b["data"]["children_transforms"][4][0][0] = 9.5 + concrete_0 * 2
    small_b["data"]["children_transforms"][4][0][1] = 20 + concrete_0 * 2
    small_b["data"]["children_transforms"][5][0][0] = (9.5 + concrete_0 * 2) * 2
    small_b["data"]["children_transforms"][5][0][1] = 20 + concrete_0 * 2
    #_____________________________________________________________________
    small_b_2["data"]["children_transforms"][1][0][0] = 9.5 + concrete_0 * 2
    small_b_2["data"]["children_transforms"][2][0][0] = (9.5 + concrete_0 * 2) * 2
    small_b_2["data"]["children_transforms"][3][0][1] = 20 + concrete_0 * 2
    small_b_2["data"]["children_transforms"][4][0][0] = 9.5 + concrete_0 * 2
    small_b_2["data"]["children_transforms"][4][0][1] = 20 + concrete_0 * 2
    small_b_2["data"]["children_transforms"][5][0][0] = (9.5 + concrete_0 * 2) * 2
    small_b_2["data"]["children_transforms"][5][0][1] = 20 + concrete_0 * 2
    # _____________________________________________________________________
    small_b_3["data"]["children_transforms"][1][0][0] = 9.5 + concrete_0 * 2
    small_b_3["data"]["children_transforms"][2][0][0] = (9.5 + concrete_0 * 2) * 2
    small_b_3["data"]["children_transforms"][3][0][1] = 20 + concrete_0 * 2
    small_b_3["data"]["children_transforms"][4][0][0] = 9.5 + concrete_0 * 2
    small_b_3["data"]["children_transforms"][4][0][1] = 20 + concrete_0 * 2
    small_b_3["data"]["children_transforms"][5][0][0] = (9.5 + concrete_0 * 2) * 2
    small_b_3["data"]["children_transforms"][5][0][1] = 20 + concrete_0 * 2
    # _____________________________________________________________________

    #Workaround long building

    long_b["data"]["children_transforms"][1][0][0] = (9.5 + concrete_0 * 2) * 3
    long_b["data"]["children_transforms"][2][0][0] = (9.5 + concrete_0 * 2) * 6#((9.5 + concrete_0 * 2) * 3) * 2
    long_b["data"]["children_transforms"][3][0][0] = (9.5 + concrete_0 * 2) * 6#20 + concrete_0 * 2
    long_b["data"]["children_transforms"][3][0][1] = 20 + concrete_0 * 2#((9.5 + concrete_0 * 2) * 3) * 2

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


    with open('concrete_1_small_1.yaml', 'w') as outfile:
        yaml.dump(c_1_s_1, outfile)
    with open('concrete_1_small_2.yaml', 'w') as outfile:
        yaml.dump(c_1_s_2, outfile)
    with open('concrete_1_small_3.yaml', 'w') as outfile:
        yaml.dump(c_1_s_3, outfile)
    with open('concrete_1_small_4.yaml', 'w') as outfile:
        yaml.dump(c_1_s_4, outfile)
    with open('concrete_1_small_5.yaml', 'w') as outfile:
        yaml.dump(c_1_s_5, outfile)
    with open('concrete_1_small_6.yaml', 'w') as outfile:
        yaml.dump(c_1_s_6, outfile)
    with open('concrete_1_small_7.yaml', 'w') as outfile:
        yaml.dump(c_1_s_7, outfile)
    with open('concrete_1_small_8.yaml', 'w') as outfile:
        yaml.dump(c_1_s_8, outfile)
    with open('concrete_1_small_9.yaml', 'w') as outfile:
        yaml.dump(c_1_s_9, outfile)
    with open('concrete_1_small_10.yaml', 'w') as outfile:
        yaml.dump(c_1_s_10, outfile)
    with open('concrete_1_small_11.yaml', 'w') as outfile:
        yaml.dump(c_1_s_11, outfile)
    with open('concrete_1_small_12.yaml', 'w') as outfile:
        yaml.dump(c_1_s_12, outfile)
    with open('concrete_1_small_13.yaml', 'w') as outfile:
        yaml.dump(c_1_s_13, outfile)
    with open('concrete_1_small_14.yaml', 'w') as outfile:
        yaml.dump(c_1_s_14, outfile)
    with open('concrete_1_small_15.yaml', 'w') as outfile:
        yaml.dump(c_1_s_15, outfile)
    with open('concrete_1_small_16.yaml', 'w') as outfile:
        yaml.dump(c_1_s_16, outfile)
    with open('concrete_1_small_17.yaml', 'w') as outfile:
        yaml.dump(c_1_s_17, outfile)
    with open('concrete_1_small_18.yaml', 'w') as outfile:
        yaml.dump(c_1_s_18, outfile)
    with open('concrete_1_small_19.yaml', 'w') as outfile:
        yaml.dump(c_1_s_19, outfile)
    with open('concrete_1_small_20.yaml', 'w') as outfile:
        yaml.dump(c_1_s_20, outfile)

    with open('env+buildings.yaml', 'w') as outfile:
        yaml.dump(e_b, outfile)
    with open('long_building.yaml', 'w') as outfile:
        yaml.dump(long_b, outfile)
    with open('result.yaml', 'w') as outfile:
        yaml.dump(result, outfile)

    with open('RW+Sand_1.yaml', 'w') as outfile:
        yaml.dump(RW_1, outfile)
    with open('RW+Sand_2.yaml', 'w') as outfile:
        yaml.dump(RW_2, outfile)
    with open('RW+Sand_3.yaml', 'w') as outfile:
        yaml.dump(RW_3, outfile)
    with open('RW+Sand_4.yaml', 'w') as outfile:
        yaml.dump(RW_4, outfile)
    with open('RW+Sand_5.yaml', 'w') as outfile:
        yaml.dump(RW_5, outfile)
    with open('RW+Sand_6.yaml', 'w') as outfile:
        yaml.dump(RW_6, outfile)
    with open('RW+Sand_7.yaml', 'w') as outfile:
        yaml.dump(RW_7, outfile)
    with open('RW+Sand_8.yaml', 'w') as outfile:
        yaml.dump(RW_8, outfile)
    with open('RW+Sand_9.yaml', 'w') as outfile:
        yaml.dump(RW_9, outfile)
    with open('RW+Sand_10.yaml', 'w') as outfile:
        yaml.dump(RW_10, outfile)
    with open('RW+Sand_11.yaml', 'w') as outfile:
        yaml.dump(RW_11, outfile)
    with open('RW+Sand_12.yaml', 'w') as outfile:
        yaml.dump(RW_12, outfile)
    with open('RW+Sand_13.yaml', 'w') as outfile:
        yaml.dump(RW_13, outfile)
    with open('RW+Sand_14.yaml', 'w') as outfile:
        yaml.dump(RW_14, outfile)
    with open('RW+Sand_15.yaml', 'w') as outfile:
        yaml.dump(RW_15, outfile)
    with open('RW+Sand_16.yaml', 'w') as outfile:
        yaml.dump(RW_16, outfile)
    with open('RW+Sand_17.yaml', 'w') as outfile:
        yaml.dump(RW_17, outfile)
    with open('RW+Sand_18.yaml', 'w') as outfile:
        yaml.dump(RW_18, outfile)
    with open('RW+Sand_19.yaml', 'w') as outfile:
        yaml.dump(RW_19, outfile)
    with open('RW+Sand_20.yaml', 'w') as outfile:
        yaml.dump(RW_20, outfile)

    with open('small_building.yaml', 'w') as outfile:
        yaml.dump(small_b, outfile)
    with open('small_building_2.yaml', 'w') as outfile:
        yaml.dump(small_b_2, outfile)
    with open('small_building_3.yaml', 'w') as outfile:
        yaml.dump(small_b_3, outfile)

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
    RW_size = float(sys.argv[14])# between 0and 7
    resize_mesh(env_0_Z, env_0_XY, concrete_0, concrete_1, env_1_Z, l1, l2, l3, l4, h1, h2, quality, quality_env, RW_size)
