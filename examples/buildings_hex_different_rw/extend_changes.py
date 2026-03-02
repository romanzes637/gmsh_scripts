import yaml
import sys
import math


if __name__ == "__main__":
    '''Changing single_rw_I according to single_rw'''

    with open('single_rw.yaml') as f0:
        main = yaml.full_load(f0)
    with open('single_rw_1.yaml') as f1:
        main_1 = yaml.full_load(f1)
    with open('single_rw_2.yaml') as f2:
        main_2 = yaml.full_load(f2)
    with open('single_rw_3.yaml') as f3:
        main_3 = yaml.full_load(f3)
    with open('single_rw_4.yaml') as f4:
        main_4 = yaml.full_load(f4)
    with open('single_rw_5.yaml') as f5:
        main_5 = yaml.full_load(f5)
    with open('single_rw_6.yaml') as f6:
        main_6 = yaml.full_load(f6)
    with open('single_rw_7.yaml') as f7:
        main_7 = yaml.full_load(f7)
    with open('single_rw_8.yaml') as f8:
        main_8 = yaml.full_load(f8)
    with open('single_rw_9.yaml') as f9:
        main_9 = yaml.full_load(f9)
    with open('single_rw_10.yaml') as f10:
        main_10 = yaml.full_load(f10)
    with open('single_rw_11.yaml') as f11:
        main_11 = yaml.full_load(f11)
    with open('single_rw_12.yaml') as f12:
        main_12 = yaml.full_load(f12)
    with open('single_rw_13.yaml') as f13:
        main_13 = yaml.full_load(f13)
    with open('single_rw_14.yaml') as f14:
        main_14 = yaml.full_load(f14)
    with open('single_rw_15.yaml') as f15:
        main_15 = yaml.full_load(f15)
    with open('single_rw_16.yaml') as f16:
        main_16 = yaml.full_load(f16)
    with open('single_rw_17.yaml') as f17:
        main_17 = yaml.full_load(f17)
    with open('single_rw_18.yaml') as f18:
        main_18 = yaml.full_load(f18)
    with open('single_rw_19.yaml') as f19:
        main_19 = yaml.full_load(f19)


    #changing files
    # work with main.yaml
    main_1["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_1["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_1["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_1["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_1["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_1["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_1["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_1["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_1["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_1["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_1["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_1["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_1["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_2["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_2["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_2["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_2["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_2["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_2["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_2["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_2["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_2["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_2["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_2["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_2["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_2["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_3["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_3["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_3["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_3["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_3["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_3["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_3["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_3["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_3["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_3["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_3["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_3["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_3["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_4["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_4["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_4["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_4["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_4["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_4["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_4["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_4["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_4["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_4["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_4["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_4["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_4["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_5["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_5["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_5["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_5["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_5["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_5["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_5["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_5["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_5["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_5["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_5["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_5["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_5["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_6["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_6["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_6["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_6["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_6["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_6["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_6["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_6["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_6["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_6["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_6["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_6["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_6["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_7["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_7["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_7["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_7["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_7["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_7["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_7["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_7["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_7["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_7["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_7["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_7["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_7["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_8["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_8["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_8["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_8["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_8["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_8["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_8["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_8["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_8["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_8["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_8["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_8["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_8["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_9["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_9["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_9["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_9["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_9["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_9["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_9["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_9["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_9["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_9["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_9["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_9["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_9["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_10["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_10["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_10["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_10["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_10["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_10["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_10["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_10["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_10["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_10["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_10["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_10["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_10["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_11["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_11["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_11["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_11["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_11["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_11["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_11["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_11["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_11["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_11["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_11["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_11["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_11["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_12["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_12["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_12["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_12["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_12["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_12["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_12["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_12["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_12["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_12["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_12["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_12["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_12["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_13["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_13["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_13["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_13["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_13["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_13["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_13["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_13["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_13["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_13["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_13["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_13["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_13["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_14["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_14["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_14["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_14["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_14["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_14["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_14["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_14["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_14["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_14["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_14["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_14["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_14["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_15["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_15["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_15["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_15["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_15["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_15["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_15["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_15["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_15["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_15["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_15["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_15["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_15["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_16["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_16["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_16["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_16["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_16["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_16["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_16["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_16["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_16["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_16["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_16["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_16["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_16["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_17["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_17["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_17["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_17["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_17["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_17["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_17["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_17["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_17["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_17["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_17["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_17["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_17["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_18["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_18["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_18["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_18["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_18["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_18["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_18["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_18["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_18["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_18["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_18["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_18["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_18["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    # work with main.yaml
    main_19["data"]["matrix"][0][0] = main["data"]["matrix"][0][0]
    main_19["data"]["matrix"][0][1] = main["data"]["matrix"][0][1]
    main_19["data"]["matrix"][0][2] = main["data"]["matrix"][0][2]
    main_19["data"]["matrix"][0][3] = main["data"]["matrix"][0][3]

    main_19["data"]["matrix"][1][0] = main["data"]["matrix"][1][0]
    main_19["data"]["matrix"][1][1] = main["data"]["matrix"][1][1]
    main_19["data"]["matrix"][1][2] = main["data"]["matrix"][1][2]
    main_19["data"]["matrix"][1][3] = main["data"]["matrix"][1][3]

    main_19["data"]["matrix"][2][0] = main["data"]["matrix"][2][0]
    main_19["data"]["matrix"][2][1] = main["data"]["matrix"][2][1]
    main_19["data"]["matrix"][2][2] = main["data"]["matrix"][2][2]
    main_19["data"]["matrix"][2][3] = main["data"]["matrix"][2][3]
    main_19["data"]["matrix"][2][4] = main["data"]["matrix"][2][4]

    with open('single_rw_1.yaml', 'w') as outfile:
        yaml.dump(main_1, outfile)
    with open('single_rw_2.yaml', 'w') as outfile:
        yaml.dump(main_2, outfile)
    with open('single_rw_3.yaml', 'w') as outfile:
        yaml.dump(main_3, outfile)
    with open('single_rw_4.yaml', 'w') as outfile:
        yaml.dump(main_4, outfile)
    with open('single_rw_5.yaml', 'w') as outfile:
        yaml.dump(main_5, outfile)
    with open('single_rw_6.yaml', 'w') as outfile:
        yaml.dump(main_6, outfile)
    with open('single_rw_7.yaml', 'w') as outfile:
        yaml.dump(main_7, outfile)
    with open('single_rw_8.yaml', 'w') as outfile:
        yaml.dump(main_8, outfile)
    with open('single_rw_9.yaml', 'w') as outfile:
        yaml.dump(main_9, outfile)
    with open('single_rw_10.yaml', 'w') as outfile:
        yaml.dump(main_10, outfile)
    with open('single_rw_11.yaml', 'w') as outfile:
        yaml.dump(main_11, outfile)
    with open('single_rw_12.yaml', 'w') as outfile:
        yaml.dump(main_12, outfile)
    with open('single_rw_13.yaml', 'w') as outfile:
        yaml.dump(main_13, outfile)
    with open('single_rw_14.yaml', 'w') as outfile:
        yaml.dump(main_14, outfile)
    with open('single_rw_15.yaml', 'w') as outfile:
        yaml.dump(main_15, outfile)
    with open('single_rw_16.yaml', 'w') as outfile:
        yaml.dump(main_16, outfile)
    with open('single_rw_17.yaml', 'w') as outfile:
        yaml.dump(main_17, outfile)
    with open('single_rw_18.yaml', 'w') as outfile:
        yaml.dump(main_18, outfile)
    with open('single_rw_19.yaml', 'w') as outfile:
        yaml.dump(main_19, outfile)