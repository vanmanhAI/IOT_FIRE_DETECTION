import math

def TinhToan(x: float, y: float):  # x, y là tọa độ đã chuẩn hóa
    # const
    hCamera = 30   # chiều cao của camera so với mặt đất - cm
    d = 23.0       # chiều dài của góc nhìn của camera - cm
    r = 18.0       # chiều rộng của góc nhìn của camera - cm
    hServo = 28    # chiều cao của servo2 so với mặt đất - cm
    y1 = 1         # hình chiếu của servo2 xuống mặt đất - đã chuẩn hóa
    hNen = 6       # chiều cao cây nến muốn đạt được

    # góc 1 - góc quay của servo 1
    angle1 = 90  # angle1 là góc quay của servo1
    # mặc định là ban đầu 90 độ
    # thẳng đứng so với mặt đất
    alpha_radian = math.atan(abs(0.5 - x) * r / hCamera)  # góc theo radian
    delta = 5 * math.tan(alpha_radian) / d
    if x < 0.5:
        x += delta
    else:
        x -= delta
    alpha_radian = math.atan(abs(0.5 - x) * r / hCamera)  # góc theo radian

    alpha_degree = math.degrees(alpha_radian)             # góc theo độ

    # nếu hình chiếu của x lên mặt phẳng mà quá 0.5 thì góc > 90 độ
    if x < 0.5:
        angle1 -= alpha_degree
    else:
        angle1 += alpha_degree

    # góc 2 - góc quay của servo 2
    angle2 = 90
    # khoảng cách thực tế từ điểm cháy đến chân hình chiếu
    deltaY = (y1 - y) * d
    ch = math.sqrt(hServo ** 2 + deltaY ** 2)  # cạnh huyền của tam giác
    # góc quay alpha là góc quay với lửa ở vị trí đó, cao = 0cm
    alpha_radian = math.atan(deltaY / hServo)
    alpha_degree = math.degrees(alpha_radian)
    c = math.sqrt(hNen ** 2 + ch ** 2 - 2 * hNen * hServo)
    # góc quay beta là góc quay với lửa ở độ cao hNen
    beta_radian = math.acos((ch ** 2 + c ** 2 - hNen ** 2)/(2 * ch * c))
    beta_degree = math.degrees(beta_radian)

    # góc nhỏ hơn là góc 90 - alpha - beta
    angle2From = angle2 - alpha_degree - beta_degree

    # góc lớn hơn là góc 90 - alpha
    angle2To = angle2 - alpha_degree

    # print(alpha_degree)
    # print(beta_degree)
    print(angle1)
    # print(angle2From)
    # print(angle2To)
    # print("*********")

    return {
        "goc1": int(angle1) + 8,
        "goc2From": int(angle2From),
        "goc2To": int(angle2To)
    }