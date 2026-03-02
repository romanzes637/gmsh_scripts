# К ней необходимо приделать скрипт для ее модификации.
# Система координат:
#  Начало по оси x в центре,
# по Y в начале туннеля и далее вдоль туннеля
# по Z - вверх, начало на линии начала купола (т.е. пол туннеля -5.25)
#
# Сетка строится из нескольких блоков по названиям разберетесь
# нужно менять общий размер всей расчетной области по X,Y,Z
#
# Далее ширина туннеля, высота до купола, высота всего купола, толщина бетона
# По куполу дополнительно R - радиус верхней части и изменение угла alpha верхней части купола (-alpha - +alpha, на на рисунке туннеля 33.41)
#
# купол строится по кривой заданной набором точек кривой линии вдоль X изменение по Z,
#
# начальные точки points задают значения в начале и конце линии
# сами точки в линии вычисляются по расположению на сегменте окружности
# x=R * sin(alpha); z= Zm - R * (1.0-Cos(alpha))
#
# Zm верхняя точка купола при x=0
# нужно несколько точек для нашей картинки в сегменте -33.41 +33.41
#
# Отдельно для купола бетона, отдельно для купола породы
# При этом верхняя линия бетона должна полностью совпадать с нижней линией породы
#
# И наконец два параметра:
# количество ячеек по толщине бетона
# И некоторое качество сетки по породе
#
# При этом конечно количество разбиений по координатам нужно согласованно менять во всех блоках.
#
# точно также и размеры должны быть согласованы во всех блоках
import yaml
import sys
import math

#need all files be opened global
with open('blockTopB.yaml') as f0:
    btb = yaml.full_load(f0)

with open('blockTopR.yaml') as f1:
    btr = yaml.full_load(f1)

with open('blockLB.yaml') as f2:
    blb1 = yaml.full_load(f2)

with open('blockLR.yaml') as f3:
    blr1 = yaml.full_load(f3)

with open('blockRB.yaml') as f4:
    brb = yaml.full_load(f4)

with open('blockRR.yaml') as f5:
    brr1 = yaml.full_load(f5)

with open('bottomLR.yaml') as f6:
    blr = yaml.full_load(f6)

with open('bottomLB.yaml') as f7:
    blb = yaml.full_load(f7)

with open('bottomBR.yaml') as f8:
    bbr = yaml.full_load(f8)

with open('bottomBB.yaml') as f9:
    bbb = yaml.full_load(f9)

with open('bottomRR.yaml') as f10:
    brr = yaml.full_load(f10)


a_list = (-33.41, -28.05, -21.96, -14.95, -7.02, 0, 7.02, 14.95, 21.96, 28.05, 33.41)#grads

def fix_blockTopB(tunnel_length, c_q_x, c_q_y, c_q_z, concrete_size, radius):
    #workaround blockTopB.yaml
    #for curves
    alpha = 33.41
    m_alpha = -33.41
    alpha_step = 15
    R = 4.05#?

    #change size here
    #меняем длину туннеля и меняется длина бетона
    # print(btb["points"][0])
    # print("Old points: ")
    # for i in btb["data"]["points"]:
    #     print(i)
    #manage size of tunnel
    btb["data"]["points"][2][1] = tunnel_length
    btb["data"]["points"][3][1] = tunnel_length
    btb["data"]["points"][6][1] = tunnel_length
    btb["data"]["points"][7][1] = tunnel_length
    #--change size of concrete here
    btb["data"]["points"][4][2] = concrete_size
    btb["data"]["points"][5][2] = concrete_size
    btb["data"]["points"][6][2] = concrete_size
    btb["data"]["points"][7][2] = concrete_size
    #--
    btb["data"]["points"][4][0] = round(math.copysign(1, btb["data"]["points"][0][0]) * (abs(btb["data"]["points"][0][0]) + concrete_size),3)
    btb["data"]["points"][5][0] = round(math.copysign(1, btb["data"]["points"][1][0]) * (abs(btb["data"]["points"][1][0]) + concrete_size),3)
    btb["data"]["points"][6][0] = round(math.copysign(1, btb["data"]["points"][2][0]) * (abs(btb["data"]["points"][2][0]) + concrete_size),3)
    btb["data"]["points"][7][0] = round(math.copysign(1, btb["data"]["points"][3][0]) * (abs(btb["data"]["points"][3][0]) + concrete_size),3)
    # print("New points: ")
    # for i in btb["data"]["points"]:
    #     print(i)
    # setting qenv quality
    #manage structure matrix
    # for item in btb["data"]["structure"]:#split item to manage size for X, Y, Z respectively
    #     item[0] = concrete_quality
    btb["data"]["structure"][0][0] = c_q_x
    btb["data"]["structure"][1][0] = c_q_y
    btb["data"]["structure"][2][0] = c_q_z
    # value = math.asin(0.05 / 4.05)
    # print("value is: ", math.radians((value)))
    #we have 4 curves
    #x = R * sin(alpha_step)
    #z = 1.92/(2.03)/ - R * (1 - cos(aplha_step)
    #x=R * sin(alpha); z= Zm - R * (1.0-Cos(alpha))
    #inner
    for i in range(0, 11):
        # print(btb["data"]["curves"][0][1][i])# = #X
        # print("Calculated: ")
        # print("sin grad: ", math.sin(math.radians(a_list[i])))
        x = radius * math.sin(math.radians(a_list[i]))
        z = radius - radius * (1 - math.cos(math.radians(a_list[i])))
        btb["data"]["curves"][0][1][i][0] = round(x, 3)
        # btb["data"]["curves"][0][1][i][0] = round(x, 2)
        btb["data"]["curves"][0][1][i][2] = round(z, 3)
        # print("x =", round(x, 2), "z =", round(z, 2))
        # print("grads: ", a_list[i])
        # print("Modified: ", btb["data"]["curves"][0][1][i])

    # for i in range(0, 11):
    #     x = btb["data"]["curves"][0][1][i][0]
    #     al = math.asin(x / R)
    #     print("reconstructed degrees: ", math.degrees(al))


        # print(btb["data"]["curves"][0][1][i])# = #Z
    # for i in range(5, 11):
    #     btb["data"]["curves"][0][1][i][0] = #X
    #     btb["data"]["curves"][0][1][i][2] = #Z
    # print("***")
    #inner+shift
    for i in range(0, 11):
        # print(btb["data"]["curves"][1][1][i])
        # print(btb["data"]["curves"][1][1][i])  # = #X
        # print("Calculated: ")
        # print("sin grad: ", math.sin(math.radians(a_list[i])))
        x = radius * math.sin(math.radians(a_list[i]))
        z = (radius + concrete_size) - radius * (1 - math.cos(math.radians(a_list[i])))
        btb["data"]["curves"][1][1][i][0] = round(x, 3)
        # btb["data"]["curves"][0][1][i][0] = round(x, 2)
        btb["data"]["curves"][1][1][i][2] = round(z, 3)
        # print("x =", round(x, 2), "z =", round(z, 2))
        # btr["data"]["curves"][0][1][i] = btb["data"]["curves"][2][1][i]
        # print("grads: ", a_list[i])
        # print("Modified: ", btb["data"]["curves"][1][1][i])
    # print("***")

    #outer
    # btr["data"]["curves"][0][1][i][0] = round(x, 2)
    # btr["data"]["curves"][0][1][i][2] = round(z, 2)
    for i in range(0, 11):
        # print(btb["data"]["curves"][2][1][i])
        # print(btb["data"]["curves"][2][1][i])  # = #X
        # print("Calculated: ")
        # print("sin grad: ", math.sin(math.radians(a_list[i])))
        x = radius * math.sin(math.radians(a_list[i]))
        z = (radius + concrete_size) - radius * (1 - math.cos(math.radians(a_list[i])))
        btb["data"]["curves"][2][1][i][0] = round(x, 3)
        btb["data"]["curves"][2][1][i][1] = tunnel_length
        btb["data"]["curves"][2][1][i][2] = round(z, 3)
        # print("x =", round(x, 2), "z =", round(z, 2))
        #same points in rock
        # print(btr["data"]["curves"][0][1][i])
        # btr["data"]["curves"][3][1][i] = btb["data"]["curves"][2][1][i]
        # print("grads: ", a_list[i])
    #     print("Modified: ", btb["data"]["curves"][2][1][i])
    # print("***")
    #outer+shift
    # btr["data"]["curves"][3][1][i][0] = round(x, 2)
    # btr["data"]["curves"][3][1][i][1] = tunnel_length
    # btr["data"]["curves"][3][1][i][2] = round(z, 2)
    # print("second curves",btr["data"]["curves"][3][1])


    for i in range(0, 11):
        # print(btb["data"]["curves"][3][1][i])
        # print(btb["data"]["curves"][3][1][i])  # = #X
        # print("Calculated: ")
        # print("sin grad: ", math.sin(math.radians(a_list[i])))
        x = radius * math.sin(math.radians(a_list[i]))
        z = radius - radius * (1 - math.cos(math.radians(a_list[i])))
        btb["data"]["curves"][3][1][i][0] = round(x, 3)
        btb["data"]["curves"][3][1][i][1] = tunnel_length
        btb["data"]["curves"][3][1][i][2] = round(z, 3)
        # print("x =", round(x, 2), "z =", round(z, 2))
        # same points in rock
        # print(btr["data"]["curves"][1][1][i])
        # print("grads: ", a_list[i])
    #     print("Modified: ", btb["data"]["curves"][3][1][i])
    # print("***")
    # print(btb["data"]["curves"][0][1][1])
    # for item in btb["data"]["points"]:
    #     item[3] = concrete_quality

    with open('blockTopB.yaml', 'w') as outfile:
        yaml.dump(btb, outfile)

def fix_blockTopR(tunnel_length, env_xz, e_q_x, e_q_y, e_q_z, radius, concrete_size):
    #workaround blockTopB.yaml

    # for i in btr["data"]["points"]:
    #     print(i)
    #points for radius_segment& shift for cocrete
    btr["data"]["points"][0][0] = btb["data"]["points"][4][0]
    btr["data"]["points"][0][2] = concrete_size
    btr["data"]["points"][1][0] = btb["data"]["points"][5][0]
    btr["data"]["points"][1][2] = concrete_size
    btr["data"]["points"][2][0] = btb["data"]["points"][6][0]
    btr["data"]["points"][2][2] = concrete_size
    btr["data"]["points"][3][0] = btb["data"]["points"][7][0]
    btr["data"]["points"][3][2] = concrete_size
    #points for env_body in X
    btr["data"]["points"][4][0] = round(math.copysign(1, btr["data"]["points"][4][0]) * env_xz,3)
    btr["data"]["points"][5][0] = round(math.copysign(1, btr["data"]["points"][5][0]) * env_xz,3)
    btr["data"]["points"][6][0] = round(math.copysign(1, btr["data"]["points"][6][0]) * env_xz,3)
    btr["data"]["points"][7][0] = round(math.copysign(1, btr["data"]["points"][7][0]) * env_xz,3)
    #in Z
    btr["data"]["points"][4][2] = round(math.copysign(1, btr["data"]["points"][4][2]) * env_xz,3)
    btr["data"]["points"][5][2] = round(math.copysign(1, btr["data"]["points"][5][2]) * env_xz,3)
    btr["data"]["points"][6][2] = round(math.copysign(1, btr["data"]["points"][6][2]) * env_xz,3)
    btr["data"]["points"][7][2] = round(math.copysign(1, btr["data"]["points"][7][2]) * env_xz,3)
    # print("new: ")
    # for i in btr["data"]["points"]:
    #     print(i)
    #change size here
    for i in range(0, 11):
        btr["data"]["curves"][3][1][i] = btb["data"]["curves"][2][1][i]#6-7 fron btb
        btr["data"]["curves"][0][1][i] = btb["data"]["curves"][1][1][i]#5-4 from btb



    # X Y Z quality
    btr["data"]["points"][2][1] = tunnel_length
    btr["data"]["points"][3][1] = tunnel_length
    btr["data"]["points"][6][1] = tunnel_length
    btr["data"]["points"][7][1] = tunnel_length

    # inner
    #calced previosly
    # for i in range(0, 11):
    #     # print(btr["data"]["curves"][0][1][i])# = #X
    #     # print("Calculated: ")
    #     # print("sin grad: ", math.sin(math.radians(a_list[i])))
    #
    #     x = radius * math.sin(math.radians(a_list[i]))
    #     z = (radius + concrete_size) - radius * (1 - math.cos(math.radians(a_list[i])))
    #     btr["data"]["curves"][0][1][i][0] = round(x, 2)
    #     btr["data"]["curves"][0][1][i][2] = round(z, 2)
    #
    #     # print("x =", round(x, 2), "z =", round(z, 2))
    #     # print("grads: ", a_list[i])
    #     # print("Modified: ", btr["data"]["curves"][0][1][i])

    # for i in range(0, 11):
    #     x = btb["data"]["curves"][0][1][i][0]
    #     al = math.asin(x / R)
    #     print("reconstructed degrees: ", math.degrees(al))

    # print(btb["data"]["curves"][0][1][i])# = #Z
    # for i in range(5, 11):
    #     btb["data"]["curves"][0][1][i][0] = #X
    #     btb["data"]["curves"][0][1][i][2] = #Z
    # print("***")
    # inner+shift
    #calced previosly
    # for i in range(0, 11):
    #     # print(btr["data"]["curves"][3][1][i])
    #     # print(btb["data"]["curves"][1][1][i])  # = #X
    #     # print("Calculated: ")
    #     # print("sin grad: ", math.sin(math.radians(a_list[i])))
    #     x = radius * math.sin(math.radians(a_list[i]))
    #     z = (radius + concrete_size) - radius * (1 - math.cos(math.radians(a_list[i])))
    #     btr["data"]["curves"][3][1][i][0] = round(x, 2)
    #     btr["data"]["curves"][3][1][i][1] = tunnel_length
    #     btr["data"]["curves"][3][1][i][2] = round(z, 2)
    #     # print("x =", round(x, 2), "z =", round(z, 2))
    #     # print("grads: ", a_list[i])
    #     # print("Modified: ", btr["data"]["curves"][3][1][i])
    # print("***")

    # for item in btr["data"]["structure"]:#split item to manage size for X, Y, Z respectively
    #     item[0] = env_quality
    btr["data"]["structure"][0][0] = btb["data"]["structure"][0][0]#x
    btr["data"]["structure"][1][0] = btb["data"]["structure"][1][0]#y
    btr["data"]["structure"][2][0] = e_q_z#z

    #setting qenv quality
    # for item in btr["data"]["points"]:
    #     item[3] = env_quality


    with open('blockTopR.yaml', 'w') as outfile:
        yaml.dump(btr, outfile)

def fix_blockLB(tunnel_length, tunnel_height, concrete_size, c_q_x, c_q_y, c_q_z):
    #workaround blockTopB.yaml
    #change tunnel size here
    blb1["data"]["points"][2][1] = tunnel_length
    blb1["data"]["points"][3][1] = tunnel_length
    blb1["data"]["points"][6][1] = tunnel_length
    blb1["data"]["points"][7][1] = tunnel_length
    #we set tunnel height in  p0 p1 p2 p3: blb1["data"]["points"][0][2],..,blb1["data"]["points"][3][2]
    blb1["data"]["points"][0][2] = 0 - tunnel_height
    blb1["data"]["points"][1][2] = 0 - tunnel_height
    blb1["data"]["points"][2][2] = 0 - tunnel_height
    blb1["data"]["points"][3][2] = 0 - tunnel_height
    #upper points must accord with btb points
    blb1["data"]["points"][4] = btb["data"]["points"][1]
    blb1["data"]["points"][4][2] = concrete_size#?
    blb1["data"]["points"][5] = btb["data"]["points"][5]
    blb1["data"]["points"][6] = btb["data"]["points"][6]
    blb1["data"]["points"][7] = btb["data"]["points"][2]
    blb1["data"]["points"][7][2] = concrete_size#?
    #lower points calculated
    # blb1["data"]["points"][0][1] = tunnel_length
    blb1["data"]["points"][1][0] = math.copysign(1, blb1["data"]["points"][1][0]) * (abs(blb1["data"]["points"][0][0]) + concrete_size)
    blb1["data"]["points"][2][0] = math.copysign(1, blb1["data"]["points"][2][0]) * (abs(blb1["data"]["points"][3][0]) + concrete_size)
    # blb1["data"]["points"][3][1] = tunnel_length

    # for item in blb1["data"]["structure"]:#split item to manage size for X, Y, Z respectively
    #     item[0] = concrete_quality
    blb1["data"]["structure"][0][0] = btb["data"]["structure"][0][0]
    blb1["data"]["structure"][1][0] = btb["data"]["structure"][1][0]
    blb1["data"]["structure"][2][0] = btb["data"]["structure"][2][0]
    #set concrete size
    #math.copysign(1, btb["data"]["points"][0][0]) *
    # print(blb1["data"]["points"][1][0])
    # blb1["data"]["points"][1][0] = math.copysign(1, blb1["data"]["points"][0][0]) * (abs(blb1["data"]["points"][0][0]) + concrete_size)
    # print(blb1["data"]["points"][1][0])
    # print("***")
    # print(blb1["data"]["points"][2][0])
    # blb1["data"]["points"][2][0] = math.copysign(1, blb1["data"]["points"][3][0]) * (abs(blb1["data"]["points"][3][0]) + concrete_size)
    # print(blb1["data"]["points"][2][0])
    # print("***")
    # print(blb1["data"]["points"][5][0])
    # blb1["data"]["points"][5][0] = math.copysign(1, blb1["data"]["points"][4][0]) * (abs(blb1["data"]["points"][4][0]) + concrete_size)
    # print(blb1["data"]["points"][5][0])
    # print("***")
    # print(blb1["data"]["points"][6][0])
    # blb1["data"]["points"][6][0] = math.copysign(1, blb1["data"]["points"][7][0]) * (abs(blb1["data"]["points"][7][0]) + concrete_size)
    # print(blb1["data"]["points"][6][0])
    # print("***")

    # setting qenv quality
    # for item in blb["data"]["points"]:
    #     item[3] = quality_env

    with open('blockLB.yaml', 'w') as outfile:
        yaml.dump(blb1, outfile)

def fix_blockLR(tunnel_length, tunnel_height, e_q_x, e_q_y, e_q_z, env_xz, concrete_size):
    #workaround blockTopB.yaml

    #change tunnel size here
    blr1["data"]["points"][2][1] = tunnel_length
    blr1["data"]["points"][3][1] = tunnel_length
    blr1["data"]["points"][6][1] = tunnel_length
    blr1["data"]["points"][7][1] = tunnel_length

    #set points accordingly to blb1
    #so we set height of tunnel via blb1
    # print(blr1["data"]["points"][4])
    # print(btr["data"]["points"][1])
    blr1["data"]["points"][0] = blb1["data"]["points"][1]
    blr1["data"]["points"][3] = blb1["data"]["points"][2]
    blr1["data"]["points"][4] = btr["data"]["points"][1]
    # blr1["data"]["points"][4][2] = 0-concrete_size
    blr1["data"]["points"][7] = btr["data"]["points"][2]
    # blr1["data"]["points"][7][2] = 0-concrete_size
    #set points accordingly to btr
    blr1["data"]["points"][5] = btr["data"]["points"][5]
    blr1["data"]["points"][6] = btr["data"]["points"][6]
    # print("points",blr1["data"]["points"][7], btr["data"]["points"][2])

    #set size of rock
    # blb1["data"]["points"][1][2]
    blr1["data"]["points"][1][0] = round(math.copysign(1, blr1["data"]["points"][1][0]) * (env_xz),2)
    blr1["data"]["points"][1][2] = blb1["data"]["points"][1][2]#must accord with blockLB p1 in Z blb1
    blr1["data"]["points"][2][0] = round(math.copysign(1, blr1["data"]["points"][2][0]) * (env_xz),2)
    blr1["data"]["points"][2][2] = blb1["data"]["points"][2][2]#must accord with blockLB p2 in Z blb1
    # blr1["data"]["points"][1][2] = math.copysign(1, blr1["data"]["points"][1][2]) * (env_xz)
    # blr1["data"]["points"][2][2] = math.copysign(1, blr1["data"]["points"][2][2]) * (env_xz)

    # setting qenv quality
    # for item in blr["data"]["points"]:
    #     item[3] = quality_env

    # structure: [
    #     [14, 0, 0.833333333],  # X
    #     [9, 0, 1.0],  # Y
    #     [15, 0, 1.0],  # Z
    # ]
    blr1["data"]["structure"][0][0] = btr["data"]["structure"][2][0]
    blr1["data"]["structure"][1][0] = btr["data"]["structure"][1][0]
    blr1["data"]["structure"][2][0] = btb["data"]["structure"][2][0]#e_q_z#btb["data"]["structure"][2][0]

    # for item in blr1["data"]["structure"]:#split item to manage size for X, Y, Z respectively
    #     item[0] = quality_env

    with open('blockLR.yaml', 'w') as outfile:
        yaml.dump(blr1, outfile)

def fix_blockRB(tunnel_length, tunnel_height, concrete_size, c_q_x, c_q_y, c_q_z):
    # workaround blockTopB.yaml
    # change tunnel size here
    brb["data"]["points"][2][1] = tunnel_length
    brb["data"]["points"][3][1] = tunnel_length
    brb["data"]["points"][6][1] = tunnel_length
    brb["data"]["points"][7][1] = tunnel_length
    # upper points must accord with btb points
    brb["data"]["points"][4] = btb["data"]["points"][4]
    brb["data"]["points"][5] = btb["data"]["points"][0]
    brb["data"]["points"][5][2] = concrete_size#?
    brb["data"]["points"][6] = btb["data"]["points"][3]
    brb["data"]["points"][6][2] = concrete_size#?
    brb["data"]["points"][7] = btb["data"]["points"][7]
    # we set tunnel height in  p0 p1 p2 p3: brb["data"]["points"][0][2],..,blb1["data"]["points"][3][2]
    brb["data"]["points"][0][2] = 0 - tunnel_height
    brb["data"]["points"][1][2] = 0 - tunnel_height
    brb["data"]["points"][2][2] = 0 - tunnel_height
    brb["data"]["points"][3][2] = 0 - tunnel_height

    # lower points calculated
    # blb1["data"]["points"][0][1] = tunnel_length
    brb["data"]["points"][0][0] = math.copysign(1, brb["data"]["points"][1][0]) * (
                abs(brb["data"]["points"][1][0]) + concrete_size)
    brb["data"]["points"][3][0] = math.copysign(1, brb["data"]["points"][2][0]) * (
                abs(brb["data"]["points"][2][0]) + concrete_size)
    # blb1["data"]["points"][3][1] = tunnel_length

    # for item in brb["data"]["structure"]:  # split item to manage size for X, Y, Z respectively
    #     item[0] = concrete_quality
    brb["data"]["structure"][0][0] = btb["data"]["structure"][0][0]
    brb["data"]["structure"][1][0] = btb["data"]["structure"][1][0]
    brb["data"]["structure"][2][0] = btb["data"]["structure"][2][0]
    # set concrete size

    # math.copysign(1, btb["data"]["points"][0][0]) *
    # print(blb1["data"]["points"][1][0])
    # blb1["data"]["points"][1][0] = math.copysign(1, blb1["data"]["points"][0][0]) * (abs(blb1["data"]["points"][0][0]) + concrete_size)
    # print(blb1["data"]["points"][1][0])
    # print("***")
    # print(blb1["data"]["points"][2][0])
    # blb1["data"]["points"][2][0] = math.copysign(1, blb1["data"]["points"][3][0]) * (abs(blb1["data"]["points"][3][0]) + concrete_size)
    # print(blb1["data"]["points"][2][0])
    # print("***")
    # print(blb1["data"]["points"][5][0])
    # blb1["data"]["points"][5][0] = math.copysign(1, blb1["data"]["points"][4][0]) * (abs(blb1["data"]["points"][4][0]) + concrete_size)
    # print(blb1["data"]["points"][5][0])
    # print("***")
    # print(blb1["data"]["points"][6][0])
    # blb1["data"]["points"][6][0] = math.copysign(1, blb1["data"]["points"][7][0]) * (abs(blb1["data"]["points"][7][0]) + concrete_size)
    # print(blb1["data"]["points"][6][0])
    # print("***")

    # setting qenv quality
    # for item in blb["data"]["points"]:
    #     item[3] = quality_env

    with open('blockRB.yaml', 'w') as outfile:
        yaml.dump(brb, outfile)

def fix_blockRR(tunnel_length, tunnel_height, e_q_x, e_q_y, e_q_z, env_xz, concrete_size):
    # workaround blockTopB.yaml

    # change tunnel size here
    brr1["data"]["points"][2][1] = tunnel_length
    brr1["data"]["points"][3][1] = tunnel_length
    brr1["data"]["points"][6][1] = tunnel_length
    brr1["data"]["points"][7][1] = tunnel_length

    # set points accordingly to brb
    #tunnel height sets via brb
    brr1["data"]["points"][1] = brb["data"]["points"][0]
    brr1["data"]["points"][2] = brb["data"]["points"][3]
    brr1["data"]["points"][5] = brb["data"]["points"][4]
    brr1["data"]["points"][6] = brb["data"]["points"][7]
    # set points accordingly to btr
    brr1["data"]["points"][4] = btr["data"]["points"][4]
    brr1["data"]["points"][7] = btr["data"]["points"][7]

    # set size of rock
    brr1["data"]["points"][0][0] = math.copysign(1, brr1["data"]["points"][0][0]) * (env_xz)
    brr1["data"]["points"][0][2] = brb["data"]["points"][0][2]#p0 of brb
    brr1["data"]["points"][3][0] = math.copysign(1, brr1["data"]["points"][3][0]) * (env_xz)
    brr1["data"]["points"][3][2] = brb["data"]["points"][3][2]#p3 of brb
    # blr1["data"]["points"][1][2] = math.copysign(1, blr1["data"]["points"][1][2]) * (env_xz)
    # blr1["data"]["points"][2][2] = math.copysign(1, blr1["data"]["points"][2][2]) * (env_xz)

    # setting qenv quality
    # for item in blr["data"]["points"]:
    #     item[3] = quality_env

    # for item in brr1["data"]["structure"]:  # split item to manage size for X, Y, Z respectively
    #     item[0] = quality_env
    brr1["data"]["structure"][0][0] = btr["data"]["structure"][2][0]
    brr1["data"]["structure"][1][0] = btr["data"]["structure"][1][0]
    brr1["data"]["structure"][2][0] = brb["data"]["structure"][2][0]

    with open('blockRR.yaml', 'w') as outfile:
        yaml.dump(brr1, outfile)

def fix_bottomLR(tunnel_length, tunnel_height, e_q_x, e_q_y, e_q_z, env_xz, concrete_size):
    #matrix
    #change size here
    # print(blr["data"]["matrix"][1][1][0])
    # [[-10;.1, -3.005;.1;14: 0:0.8333333],
    # [0;.1, 8;.1;9],
    # [-13;.1, -5.250;.1;12: 0:0.933333]]
    # print(int(blr["data"]["matrix"][0][0].split(";")[0]))
    # print(int(blr["data"]["matrix"][2][0].split(";")[0]))
    basic_tunnel = -2.925
    # str(quality_env)
    x = math.copysign(1, float(blr["data"]["matrix"][0][0].split(";")[0])) * env_xz
    x2 = math.copysign(1, float(blr["data"]["matrix"][0][0].split(";")[0])) * (abs(basic_tunnel) + concrete_size)
    z = math.copysign(1, float(blr["data"]["matrix"][2][0].split(";")[0])) * env_xz
    #Build X part of matrix
    # btr["data"]["structure"][0][0]
    blr["data"]["matrix"][0][0] = str(x) + ";;"
    blr["data"]["matrix"][0][1] = str(x2) + ";;" + str(btr["data"]["structure"][2][0]) + ":0:0.8333333"#14
    # blr["data"]["matrix"][0][1] = str(x2) + ";;" + str(e_q_x) + ":0:0.8333333"
    #Build Y part of matrix
    blr["data"]["matrix"][1][1] = str(tunnel_length) + ";;" + str(brr1["data"]["structure"][1][0])  #9 = str(tunnel_length)#[ 0;.1, 8;.1;9 ]
    # blr["data"]["matrix"][1][1] = str(tunnel_length) + ";;" + str(e_q_y)
    #Build Z part of matrix
    blr["data"]["matrix"][2][0] = str(z) + ";;"
    #on Z depends of tunnel height
    # 0 - tunnel_height
    #[ -13;.1, -5.250;.1;12:0:0.933333 ] ]
    blr["data"]["matrix"][2][1] = str(0 - tunnel_height) + ";;" + str(e_q_z) + ":0:0.93"#12
    # blr["data"]["matrix"][1][1][0] = text
    # for i in blr["data"]["matrix"]:
    #     print(i)
    # print(blr["data"]["matrix"][1][1])
    # for item in blr["data"]["matrix"]:
    #     print(item[1][0])
    #     item[3] = quality_env

    with open('bottomLR.yaml', 'w') as outfile:
        yaml.dump(blr, outfile)

def fix_bottomLB(tunnel_length, tunnel_height, e_q_x, e_q_y, e_q_z, env_xz, concrete_size):
    # matrix
    #inder layer of concrete
    #must accord with blockLB
    # change size here
    # print(blr["data"]["matrix"][1][1][0])
    # [[-10;.1, -3.005;.1;14: 0:0.8333333],
    # [0;.1, 8;.1;9],
    # [-13;.1, -5.250;.1;12: 0:0.933333]]
    # print(int(blr["data"]["matrix"][0][0].split(";")[0]))
    # print(int(blr["data"]["matrix"][2][0].split(";")[0]))
    basic_tunnel = 2.925
    x2 = blb1["data"]["points"][1][0]
    # x2 = math.copysign(1, float(blb["data"]["matrix"][0][1].split(";")[0])) * (abs(basic_tunnel) + concrete_size)
    x1 = math.copysign(1, float(blb["data"]["matrix"][0][0].split(";")[0])) * env_xz

    #blb1
    z = math.copysign(1, float(blb["data"]["matrix"][2][0].split(";")[0])) * env_xz
    # Build X part of matrix
    # print(blb1["data"]["points"][1][0])
    blb["data"]["matrix"][0][0] = str(x2) + ";.1"
    # + str(quality_env) + ":0:0.8333333"
    blb["data"]["matrix"][0][1] = str(0 - basic_tunnel) + ";.1;" + str(e_q_x) + ":0:1.0"#14
    # Build Y part of matrix
    blb["data"]["matrix"][1][1] = str(tunnel_length) + ";.1;" + str(blb1["data"]["structure"][1][0]) #9 = str(tunnel_length)#[ 0;.1, 8;.1;9 ]
    # Build Z part of matrix
    blb["data"]["matrix"][2][0] = str(0 - env_xz) + ";.1"
    blb["data"]["matrix"][2][1] = str(0 - tunnel_height) + ";.1;" + str(e_q_z) + ":0:0.9"#12
    # blr["data"]["matrix"][1][1][0] = text
    # for i in blr["data"]["matrix"]:
    #     print(i)
    # print(blr["data"]["matrix"][1][1])
    # for item in blr["data"]["matrix"]:
    #     print(item[1][0])
    #     item[3] = quality_env

    with open('bottomLB.yaml', 'w') as outfile:
        yaml.dump(blb, outfile)

def fix_bottomBR(tunnel_length, tunnel_height, e_q_x, e_q_y, e_q_z, env_xz):
    # matrix
    # change size here
    # print(blr["data"]["matrix"][1][1][0])
    # [[-10;.1, -3.005;.1;14: 0:0.8333333],
    # [0;.1, 8;.1;9],
    # [-13;.1, -5.250;.1;12: 0:0.933333]]
    # print(int(blr["data"]["matrix"][0][0].split(";")[0]))
    # print(int(blr["data"]["matrix"][2][0].split(";")[0]))
    basic_tunnel_size = 2.925
    x = math.copysign(1, float(blb["data"]["matrix"][0][0].split(";")[0])) * env_xz
    z = math.copysign(1, float(bbr["data"]["matrix"][2][0].split(";")[0])) * env_xz
    # Build X part of matrix
    bbr["data"]["matrix"][0][0] = str(0 - basic_tunnel_size) + ";.1"
    bbr["data"]["matrix"][0][1] = str(basic_tunnel_size) + ";.1;" + str(e_q_x) + ":0:1.0"#14
    # Build Y part of matrix
    bbr["data"]["matrix"][1][1] = str(tunnel_length) + ";.1;" + str(blb1["data"]["structure"][1][0]) #9 = str(tunnel_length)#[ 0;.1, 8;.1;9 ]
    # Build Z part of matrix
    bbr["data"]["matrix"][2][0] = str(0 - env_xz) + ";.1"
    bbr["data"]["matrix"][2][1] = str(0 - tunnel_height) + ";.1;" + str(e_q_z) + ":0:0.9"#12
    # blr["data"]["matrix"][1][1][0] = text
    # for i in blr["data"]["matrix"]:
    #     print(i)
    # print(blr["data"]["matrix"][1][1])
    # for item in blr["data"]["matrix"]:
    #     print(item[1][0])
    #     item[3] = quality_env

    with open('bottomBR.yaml', 'w') as outfile:
        yaml.dump(bbr, outfile)

def fix_bottomBB(tunnel_length, tunnel_height, e_q_x, e_q_y, e_q_z, env_xz, concrete_size):
    #matrix
    #workaround blockTopB.yaml

    basic_tunnel = 2.925
    x2 = brb["data"]["points"][0][0]
    # x2 = math.copysign(1, float(bbb["data"]["matrix"][0][1].split(";")[0])) * (abs(basic_tunnel) + concrete_size)
    x1 = math.copysign(1, float(bbb["data"]["matrix"][0][0].split(";")[0])) * env_xz

    # blb1
    z = math.copysign(1, float(bbb["data"]["matrix"][2][0].split(";")[0])) * env_xz
    # Build X part of matrix
    # print(blb1["data"]["points"][1][0])
    bbb["data"]["matrix"][0][0] = str(basic_tunnel) + ";.1"
    bbb["data"]["matrix"][0][1] = str(x2) + ";.1;" + str(brb["data"]["structure"][0][0]) + ":0:1.0"#14
    # Build Y part of matrix
    bbb["data"]["matrix"][1][1] = str(tunnel_length) + ";.1;" + str(brb["data"]["structure"][1][0]) #9 = str(tunnel_length)#[ 0;.1, 8;.1;9 ]
    # Build Z part of matrix
    bbb["data"]["matrix"][2][0] = str(0 - env_xz) + ";.1"
    bbb["data"]["matrix"][2][1] = str(0 - tunnel_height) + ";.1;" + str(e_q_z) + ":0:0.9"#12
    with open('bottomBB.yaml', 'w') as outfile:
        yaml.dump(bbb, outfile)

def fix_bottomRR(tunnel_length, tunnel_height, e_q_x, e_q_y, e_q_z, env_xz, concrete_size):
    #matrix
    #workaround blockTopB.yaml

    #change size here
    #working with
    basic_tunnel = 2.925
    x1 = btb["data"]["points"][4][0]
    # x2 = math.copysign(1, float(brr["data"]["matrix"][0][1].split(";")[0])) * (abs(basic_tunnel) + concrete_size)
    x2 = math.copysign(1, float(brr["data"]["matrix"][0][1].split(";")[0])) * env_xz

    # blb1
    z = math.copysign(1, float(brr["data"]["matrix"][2][0].split(";")[0])) * env_xz
    # Build X part of matrix
    # print(blb1["data"]["points"][1][0])
    brr["data"]["matrix"][0][0] = str(x1) + ";.1"
    brr["data"]["matrix"][0][1] = str(env_xz) + ";.1;" + str(btr["data"]["structure"][2][0]) + ":0:1.2"#14
    # Build Y part of matrix
    brr["data"]["matrix"][1][1] = str(tunnel_length) + ";.1;" + str(brr1["data"]["structure"][1][0]) #9 = str(tunnel_length)#[ 0;.1, 8;.1;9 ]
    # Build Z part of matrix
    brr["data"]["matrix"][2][0] = str(0 - env_xz) + ";.1"
    brr["data"]["matrix"][2][1] = str(0 - tunnel_height) + ";.1;" + str(e_q_z) + ":0:0.9"#12
    # brr["data"]["matrix"][0] = str(3.005) + ";.1, " + str(10.00) + ";.1;" + str(quality_env) + ":0:1.2"#[ 3.005;.1, 10.00;.1;14:0:1.2 ]
    # brr["data"]["matrix"][1] = str(0) + ";.1, " + str(tunnel_length) + ";.1;" + str(quality_env) #[ 0;.1, 8;.1;9 ]
    # brr["data"]["matrix"][2] = str(-13) + ";.1, " + str(-5.250) + ";.1;" + str(quality_env) + ":0:0.933333" #[ -13;.1, -5.250;.1;12:0:0.933333 ]
    with open('bottomRR.yaml', 'w') as outfile:
        yaml.dump(brr, outfile)

if __name__ == "__main__":
    #sys.argv[0] is a script name
    #To call python ./build_tranch.py tunnel_length quality_env
    tunnel_length = float(sys.argv[1])
    tunnel_height = float(sys.argv[2])
    radius_roof = float(sys.argv[3])
    env_xz = float(sys.argv[4])
    env_quality_x = int(sys.argv[5])
    env_quality_y = int(sys.argv[6])
    env_quality_z = int(sys.argv[7])
    # env_y = float(sys.argv[4])
    # env_z = float(sys.argv[5])
    concrete_quality_x = int(sys.argv[8])
    concrete_quality_y = int(sys.argv[9])
    concrete_quality_z = int(sys.argv[10])
    concrete_size = float(sys.argv[11])


    fix_blockTopB(tunnel_length, concrete_quality_x, concrete_quality_y, concrete_quality_z, concrete_size, radius_roof)
    fix_blockTopR(tunnel_length, env_xz, env_quality_x, env_quality_y, env_quality_z, radius_roof, concrete_size)
    fix_blockLB(tunnel_length, tunnel_height, concrete_size, concrete_quality_x, concrete_quality_y, concrete_quality_z)
    fix_blockLR(tunnel_length, tunnel_height, env_quality_x, env_quality_y, env_quality_z, env_xz, concrete_size)
    fix_blockRB(tunnel_length, tunnel_height, concrete_size, concrete_quality_x, concrete_quality_y, concrete_quality_z)
    fix_blockRR(tunnel_length, tunnel_height, env_quality_x, env_quality_y, env_quality_z, env_xz, concrete_size)
    fix_bottomLR(tunnel_length, tunnel_height, env_quality_x, env_quality_y, env_quality_z, env_xz, concrete_size)
    fix_bottomLB(tunnel_length, tunnel_height, env_quality_x, env_quality_y, env_quality_z, env_xz, concrete_size)
    fix_bottomBR(tunnel_length, tunnel_height, env_quality_x, env_quality_y, env_quality_z, env_xz)
    fix_bottomBB(tunnel_length, tunnel_height, env_quality_x, env_quality_y, env_quality_z, env_xz, concrete_size)
    fix_bottomRR(tunnel_length, tunnel_height, env_quality_x, env_quality_y, env_quality_z, env_xz, concrete_size)