import gmsh
import sys
import re

def rebuild_elements(fl, old_tag, new_tag):

    new_elements = []
    fixed_elements = []
    new_el = list()
    c = False

    for line in fl:
        if line.startswith("$Elements"):
            c = True
        if c:
            new_elements.append(line)
        if line.startswith("$EndElements"):
            break

    for l in new_elements[2:-1]:
        if int(l.split()[3]) == old_tag:
            new_el.append(l.split()[0] + " ")
            new_el.append(l.split()[1] + " ")
            new_el.append(l.split()[2] + " ")
            new_el.append(str(new_tag) + " ")#and til the end
            for j in range(4, len(l.split())):
                new_el.append(l.split()[j] + " ")
            # new_el.append(l.split()[4] + " ")
            # new_el.append(l.split()[5] + " ")
            # new_el.append(l.split()[6] + " ")
            # new_el.append(l.split()[7] + "\n")
            new_el.append("\n")
            fixed_elements.append(''.join(new_el))
            new_el.clear()
            continue
        if int(l.split()[3]) > old_tag:

            new_el.append(l.split()[0] + " ")
            new_el.append(l.split()[1] + " ")
            new_el.append(l.split()[2] + " ")
            new_el.append(str(int(l.split()[3]) - 1) + " ")#and til the end
            for j in range(4, len(l.split())):
                new_el.append(l.split()[j] + " ")
            # new_el.append(l.split()[4] + " ")
            # new_el.append(l.split()[5] + " ")
            # new_el.append(l.split()[6] + " ")
            # new_el.append(l.split()[7] + "\n")
            new_el.append("\n")
            fixed_elements.append(''.join(new_el))
            new_el.clear()
            continue
        fixed_elements.append(l)

    return fixed_elements

def rebuild_names(fl, new_zone, old_zone_1, old_zone_2):

    new_phys_names = list()
    fl = open(file).readlines()

    count = False
    for line in fl:
        if line.startswith("$PhysicalNames"):
            count = True
        if count:
            new_phys_names.append(line)
        if line.startswith("$EndPhysicalNames"):
            break

    new_phys_names[1] = str(int(new_phys_names[1]) - 1) + "\n"

    new_line = list()
    phys_names = list()
    tag_1 = 0
    tag_2 = 0
    phys_names.append(new_phys_names[0])
    phys_names.append(new_phys_names[1])

    for l in new_phys_names[2:-1]:
        # print(l[l.find("\""):l.find("\"")])#contains smth like __2 3 "env_0|un-Z1"__
        # print(l.split()[2].strip("\""))
        if l.split()[2].strip("\"") == old_zone_1:
            new_line.append(l.split()[0] + " ")
            new_line.append(l.split()[1] + " ")
            new_line.append("\"" + new_zone + "\"" + "\n")
            phys_names.append(''.join(new_line))
            new_line.clear()
            tag_1 = int(l.split()[1])
            # print(new_phys_names.index(l))
            # input()
            continue
        if l.split()[2].strip("\"") == old_zone_2:
            tag_2 = int(l.split()[1])
            # print(new_phys_names.index(l))
            # print(new_phys_names[new_phys_names.index(l)])
            # input()
            del new_phys_names[new_phys_names.index(l)]
            continue
        phys_names.append(l)

    phys_names.append(new_phys_names[-1])


    # print("our func")
    # print(phys_names)
    # input()
    #store physical adressing 'old':new
    adressing = list()


    names = list()
    names.append(new_phys_names[0])
    names.append(new_phys_names[1])
    new_line.clear()

    for l in phys_names[2:-1]:
        if int(l.split()[1]) > tag_2:
            new_line.append(l.split()[0] + " ")
            new_line.append(str(int(l.split()[1]) - 1) + " ")
            new_line.append(l.split()[2])
            # adressing.append(int(l.split()[1]))
            # adressing.append(',')
            # adressing.append(int(l.split()[1]) - 1)
            # adressing.append("\n")
            names.append(''.join(new_line) + "\n")
            new_line.clear()
            continue
        names.append(l)



    # print("new phys names are :\n")
    # print(names)
    # input()
    names.append(new_phys_names[-1])
    # print(''.join(adressing))
    # input()
    return names, tag_1, tag_2

if __name__ == "__main__":
    '''unite in 1 element input parameters in file.msh2
    '''

    surf_1 = str(sys.argv[1])
    surf_2 = str(sys.argv[2])
    file = str(sys.argv[3])

    #TODO fix $PhysicalNames section to form new list of surfaces\volumes
    new_phys_names = list()
    fl = open(file).readlines()
    count = False
    for line in fl:
        if line.startswith("$PhysicalNames"):
            count = True
        if count:
            new_phys_names.append(line)
        if line.startswith("$EndPhysicalNames"):
            break

    # print(new_phys_names)#it has correct format
    if_present_first = False
    first = 0
    second = 0
    old_tag_1 = -1
    old_tag_2 = -1
    if_present_second = False
    new_zone = ""
    if any(surf_1 in l for l in new_phys_names):
        if_present_first = True
    if any(surf_2 in l for l in new_phys_names):
        if_present_second = True
    # #TODO add element dimension checking later
    #
    # print(if_present_first)
    # print(if_present_second)
    if if_present_first and if_present_second:
        new_zone += str(surf_1) + "|" + str(surf_2)
    else:
        print("Surface names are incorrect.")
        sys.exit()

    # print("Old physical names:\n")
    # print(new_phys_names)
    physical_names_list, old_tag_1, old_tag_2 = rebuild_names(fl, new_zone, surf_1, surf_2)
    # print("modified names:\n")
    # print(physical_names_list)
    # input()
    new_phys_tag = 0


    # with open('zones.txt', 'w') as outfile:
    #     outfile.writelines(physical_names_list)
    #         # write(new_phys_names)
    # input()


    #TODO fix $Elements section in order to reassign elements to new physical tags


    fixed_elements = rebuild_elements(fl, old_tag_2, old_tag_1)
    # with open('elements.txt', 'w') as outfile:
    #     outfile.writelines(fixed_elements)


    old_mesh = list()
    new_mesh_file = list()
    mesh = []

    for l in fl:
        old_mesh.append(l)
    new_mesh_file.append(old_mesh[0])
    new_mesh_file.append(old_mesh[1])
    new_mesh_file.append(old_mesh[2])

    for l in physical_names_list:
        new_mesh_file.append(l)


    cnt = False
    for line in fl:
        if line.startswith("$Nodes"):
            cnt = True
        if cnt:
            # forming new zones
            new_mesh_file.append(line)
            # print(line)
        if line.startswith("$EndNodes"):
            break

    new_mesh_file.append("$Elements\n")
    new_mesh_file.append(fl[int(fl.index("$Elements\n")+1)])
    for l in fixed_elements:
        new_mesh_file.append(l)
    new_mesh_file.append(fl[-1])

    with open('new_mesh.msh2', 'w') as out:
        out.writelines(new_mesh_file)