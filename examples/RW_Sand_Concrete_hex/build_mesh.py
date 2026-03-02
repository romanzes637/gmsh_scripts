import yaml
import sys
import math
def resize_mesh(quality: float,
                rw_size: float,
                concrete_0: float):
    with open('main.yaml') as f0:
        main = yaml.full_load(f0)

    #work with main.yaml
    main["data"]["matrix"][0][0] = str(0)
    main["data"]["matrix"][0][1] = str(concrete_0) + str(";") + str(quality) + str(";10")
    main["data"]["matrix"][0][2] = str(11.5 - concrete_0) + str(";") + str(quality) + str(";10")
    main["data"]["matrix"][0][3] = str(11.5) + str(";") + str(quality) + str(";10")

    main["data"]["matrix"][1][0] = str(0)
    main["data"]["matrix"][1][1] = str(concrete_0) + str(";") + str(quality) + str(";10")
    main["data"]["matrix"][1][2] = str(22 - concrete_0) + str(";") + str(quality) + str(";10")
    main["data"]["matrix"][1][3] = str(22) + str(";") + str(quality) + str(";10")

    main["data"]["matrix"][2][0] = str(0)
    main["data"]["matrix"][2][1] = str(concrete_0) + str(";") + str(quality) + str(";10")
    main["data"]["matrix"][2][2] = str(concrete_0 + rw_size) + str(";") + str(quality) + str(";10")
    main["data"]["matrix"][2][3] = str(9 - concrete_0) + str(";") + str(quality) + str(";10")
    main["data"]["matrix"][2][4] = str(9) + str(";") + str(quality) + str(";10")



    with open('main.yaml', 'w') as outfile:
        yaml.dump(main, outfile)
if __name__ == "__main__":
    '''The goal is to rescale the length of resulting mesh. We change ENV in +X -X simultaneously,
     ENV in +Y -Y separately, rescaling tube with ENV in Z. Changing mesh quality for ENV separately from the main mesh'''
    #sys.argv[0] is a script name
    # To call python ./build_result.py with parameters:
    #1 quality
    #2 RW size in Z
    #python. / build_result.py %pars%
    # env_0_Z = float(sys.argv[1])
    # env_0_XY = float(sys.argv[2])
    # concrete_0 = float(sys.argv[3])
    # concrete_1 = float(sys.argv[4])
    # env_1_Z = float(sys.argv[5])
    # l1 = float(sys.argv[6])
    # l2 = float(sys.argv[7])
    # l3 = float(sys.argv[8])
    # l4 = float(sys.argv[9])
    # h1 = float(sys.argv[10])
    # h2 = float(sys.argv[11])
    quality = float(sys.argv[1])
    rw_size = float(sys.argv[2])
    concrete_0 = float(sys.argv[3])
    resize_mesh(quality, rw_size, concrete_0)
