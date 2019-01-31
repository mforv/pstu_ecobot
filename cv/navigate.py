import sys
from math import *
from cv.student import *

class Navigate(object):
    """visual navigation"""

    k_lat = (58.054694 - 58.04844) / 696
    k_lon = (56.226025 - 56.22257) / 202

    obj_list = dict(
        copter = dict(
            lat = 0,
            lon = 29,
            azm = radians(60),
        ),
        door = dict(
            lat = 21,
            lon = 54,
            azm = radians(15),
        ),
        truck = dict(
            lat = 56,
            lon = 33,
            azm = radians(-64),
        ),
        tank = dict(
            lat = 55,
            lon = 8,
            azm = radians(-108),
        ),
    )

    pnt_list = {
        -30: {
            -10: 2,
              0: 3,
             10: 5,
        },
          0: {
            -10: 2,
              0: 3,
             10: 5,
        },
         30: {
            -10: 2,
              0: 3,
             10: 5,
        },
    }

    zero_lat = 58.04844
    zero_lon = 56.22257

    azm      = 0.0

    bins_lat = 58.054694
    bins_lon = 56.226025
    sns_lat  = 58.054694
    sns_lon  = 56.226025

    use_bins = True

    def __init__(self, obj_list, pnt_list, azm, bins_lat = None, bins_lon = None, sns_lat = None, sns_lon = None):
        self.obj_list = obj_list
        self.pnt_list = pnt_list
        self.azm      = azm
        self.bins_lat = bins_lat
        self.bins_lon = bins_lon
        self.sns_lat  = sns_lat
        self.sns_lon  = sns_lon

        try:
            bins_lat * bins_lon * sns_lat * sns_lon
            self.use_bins = True
        except TypeError:
            self.use_bins = False

    def get_MISMP_pos(self):
        K = list(self.obj_list.keys())
        lat, lon = [], []
        for i in range(len(K)-1):
            obj0, obj1 = self.obj_list[K[i]], self.obj_list[K[i+1]]
            print(K[i],K[i+1], file=sys.stderr)
            tgu0 = tan(obj0['azm'] + self.azm)
            tgu1 = tan(obj1['azm'] + self.azm)
            lat1 = obj1['lat']
            lat0 = obj0['lat']
            lon0 = obj0['lon']
            lon1 = obj1['lon']
            lon.append(
                (lat1 - lat0 + (tgu0*lon0) - (tgu1*lon1)) / (tgu0 - tgu1)
            )
            lat.append((tgu0*lon[-1]) - (tgu0*lon0) + lat0)

        print([round(x,2) for x in lon], file = sys.stderr)
        print([round(x,2) for x in lat], file = sys.stderr)
        Slon, Slat = Student(lon+lon,0.95,6), Student(lat+lat,0.95,6)
        return str(Slon), str(Slat)

    def get_walls(self):
        pass

    def get_obstacles(self):
        pass

                     
if __name__ == "__main__":
    obj_list = dict(
        copter = dict(
            lat = 0,
            lon = 29,
            azm = radians(-60),
        ),
        door = dict(
            lat = 21,
            lon = 54,
            azm = radians(-15),
        ),
        truck = dict(
            lat = 56,
            lon = 33,
            azm = radians(64),
        ),
        tank = dict(
            lat = 55,
            lon = 8,
            azm = radians(108),
        ),
    )

    pnt_list = {
        -30: {
            -10: 2,
              0: 3,
             10: 5,
        },
          0: {
            -10: 2,
              0: 3,
             10: 5,
        },
         30: {
            -10: 2,
              0: 3,
             10: 5,
        },
    }

    print(Navigate(obj_list, pnt_list, radians(0)).get_MISMP_pos())


"""

k_lat = (58.054694 - 58.04844) / 696
k_lon = (56.226025 - 56.22257) / 202

#2: y = ((x - x1)*tgu) + y1

2-> M-PM-= = 
Unrecognized character.
2-> y = ((x - x2)*tgu) + y1

#3: y = ((x - x2)*tgu) + y1

3-> ((x - x1)*tgu) + y1 = ((x - x2)*tgu) + y1

#4: ((x - x1)*tgu) + y1 = ((x - x2)*tgu) + y1

4-> x
This equation is independent of the solve variable.
Solve failed for equation space #4.
4-> solve x
This equation is independent of the solve variable.
Solve failed for equation space #4.
4-> ((x - x1)*tgu1) + y1 = ((x - x2)*tgu2) + y1 

#5: ((x - x1)*tgu1) + y1 = ((x - x2)*tgu2) + y1

5-> solve x                                     
Solve successful:

        ((x1*tgu1) - (x2*tgu2))
#5: x = -----------------------
             (tgu1 - tgu2)

5-> ((x - x1)*tgu1) + y1 = ((x - x2)*tgu2) + y2 = ((x - x3)*tgu3) + y3 

Error: "((x - x3)*tgu3) + y3" not required on input line.
Extra characters or unrecognized argument.
5-> ((x - x1)*tgu1) + y1 = ((x - x2)*tgu2) + y2 = ((x - x3)*tgu3) + y3

Error: "((x - x3)*tgu3) + y3" not required on input line.
Extra characters or unrecognized argument.
5-> ((x - x1)*tgu1) + y1 = ((x - x2)*tgu2) + y2                       

#6: ((x - x1)*tgu1) + y1 = ((x - x2)*tgu2) + y2

6-> solve x                                                            
Solve successful:

        (y2 - y1 + (x1*tgu1) - (x2*tgu2))
#6: x = ---------------------------------
                  (tgu1 - tgu2)

6-> y = ((x - x2)*tgu) + y1                                            

#7: y = ((x - x2)*tgu) + y1

7-> solve y
Solve successful:

#7: y = ((x - x2)*tgu) + y1

7-> y = ((x - x2)*tgu2) + y1 

#8: y = ((x - x2)*tgu2) + y1

8-> solve y                  
Solve successful:

#8: y = ((x - x2)*tgu2) + y1

8-> y = ((x - x2)*tgu2) + y2

#9: y = ((x - x2)*tgu2) + y2

9-> solve y                  
Solve successful:

#9: y = ((x - x2)*tgu2) + y2

9-> x = (y2 - y1 + (x1*tgu1) - (x2*tgu2)) / ((tgu1 - tgu2))

         (y2 - y1 + (x1*tgu1) - (x2*tgu2))
#10: x = ---------------------------------
                   (tgu1 - tgu2)

10-> y=(((y2 - y1 + (x1*tgu1) - (x2*tgu2)) / ((tgu1 - tgu2)) - x2)*tgu2)+y2)
                                                                           ^ Unmatched parenthesis: too many )
10-> y=(((y2 - y1 + (x1*tgu1) - (x2*tgu2)) / ((tgu1 - tgu2)) - x2)*tgu2)+y2 

           (y2 - y1 + (x1*tgu1) - (x2*tgu2))
#11: y = ((--------------------------------- - x2)*tgu2) + y2
                     (tgu1 - tgu2)

11-> solve y                                                                 
Solve successful:

           (y2 - y1 + (x1*tgu1) - (x2*tgu2))
#11: y = ((--------------------------------- - x2)*tgu2) + y2
                     (tgu1 - tgu2)

11-> 

import scipy as sp
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# читаем данные
data = sp.genfromtxt("data.tsv", delimiter="\t")
#print(data[:10]) # часть данных можно напечатать, чтобы убедиться, что всё в порядке

# берём срезы: первую и вторую колонку нашего файла
x = data[:,0]
y = data[:,1]

# настраиваем детали отрисовки графиков
plt.figure(figsize=(8, 6))
plt.title("Installations")
plt.xlabel("Days")
plt.ylabel("Installations")
#plt.xticks([...], [...]) # можно назначить свои тики
plt.autoscale(tight=True)

# рисуем исходные точки
plt.scatter(x, y)

legend = []
# аргументы для построения графиков моделей: исходный интервал + 60 дней
fx = sp.linspace(x[0], x[-1] + 60, 1000)
for d in range(1, 6):
    # получаем параметры модели для полинома степени d
    fp, residuals, rank, sv, rcond = sp.polyfit(x, y, d, full=True)
    #print("Параметры модели: %s" % fp1)
    # функция-полином, если её напечатать, то увидите математическое выражение
    f = sp.poly1d(fp)
    #print(f)
    # рисуем график модельной функции
    plt.plot(fx, f(fx), linewidth=2)
    legend.append("d=%i" % f.order)
    f2 = f - 1000 # из полинома можно вычитать
    t = fsolve(f2, x[-1]) # ищем решение уравнения f2(x)=0, отплясывая от точки x[-1]
    print "Полином %d-й степени:" % f.order
    print "- Мы достигнем 1000 установок через %d дней" % (t[0] - x[-1])
    print "- Через 60 дней у нас будет %d установок" % f(x[-1] + 60)
plt.legend(legend, loc="upper left")
plt.grid()
plt.savefig('data.png', dpi=50)
plt.show()


"""


