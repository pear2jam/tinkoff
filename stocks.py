import csv


# модель для ответа
class StockModel:
    def __init__(self):
        self.ans = []

    # функции работы с массивами
    @staticmethod
    def _mul(a, v): # умножение вектора на число
        return [i * v for i in a]

    @staticmethod
    def _sub(a, b):  # сложение векторов
        if len(a) != len(b):
            raise Exception("Length error")
        return [a[i] + b[i] for i in range(len(a))]

    def _grad(self, a):  # вычисляем "градиент"
        """
        # принимает [l1, r1, l2, r2, l3, r3 ... ln, rn]
        # возвращает [d(l1)/dt, d(r1)/dt ... d(rn)/dt]
        """
        n = len(self.data)
        g = [0 for i in range(len(a))]  # итоговый "градиент"
        g = self._sub(g, [80 * (j + 1) * (a[j] < 0) for j in range(len(a))])  # если значения выходят за границы слева
        g = self._sub(g, [-80 * (j + 1) * (a[j] > n - 1) for j in range(len(a))])  # и справа
        for i in range(len(a) - 1):  # раздвигаем значения если нарушается структура
            if a[i] >= a[i + 1]:
                g[i] -= 20
                g[i + 1] += 20
        sign = -1
        for i in range(len(a)):  # считаем градиент исходя из линейности локального участка функции
            if round(a[i]) == n - 1:
                g[i] += (self.data[round(a[i])][2] - self.data[round(a[i]) - 1][2]) * sign
            elif 0 <= a[i] < n - 1:
                g[i] += (self.data[round(a[i]) + 1][2] - self.data[round(a[i])][2]) * sign
            sign *= -1
        return g

    def _f(self, a):  # значение прибыли при тактике 'a'
        n = len(self.data)
        res = 0
        for i in range(len(a) - 1):
            if a[i] >= a[i + 1]:
                return 0
        sign = -1
        for i in range(len(a)):
            if a[i] < 0:
                res += self.data[0][2] * sign
            elif a[i] > n - 1:
                res += self.data[n - 1][2] * sign
            else:
                res += self.data[round(a[i])][2] * sign
            sign *= -1
        return res

    def _optim(self, e, est, iterations=200):  # градиентный спуск, параметры: lr, начальное значение, кол-во итераций
        best_est = [0 for i in range(len(est))]
        best = -1e9
        for i in range(iterations):
            eps = e / (2 ** int(i / 60))  # после того как сошлись к локальному максимуму, уменьшаем разброс
            est = self._sub(est, self._mul(self._grad(est), e))
            if self._f(est) > best:
                best = self._f(est)
                best_est = est
        return best_est

    def _compress(self, data, ratio):  # сжатие данных с частотой ratio
        data_res = []
        i = 0
        while i < len(data):
            data_res.append(data[i])
            i += ratio
        return data_res

    # обучение модели, парам: данные, кол-во транзакций, частота сжатия данных, количество 'эпох'
    def fit(self, data, k, power=3, epochs=8):
        if power < 2:
            power = 2
        power = int(power)
        self.data = data
        best = -1e9
        best_est = [0, 0]
        start_n = len(self.data)
        new_start = False
        for ep in range(epochs):
            self.data = data
            while len(self.data) > 20*k:  # пока имеет смысл сжимаем данные
                n = len(self.data)
                e_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.85, 1, 1.15, 1.25, 1.35, 1.5, 1.75, 2, 2.5, 3, 3.5,
                          4, 5, 6, 7, 10, 20, 30, 50, 70, 100, 150, 200, 300, 400, 500, 750]  # какие lr попробуем
                est = [(i + 1)*(int(n/(k+2))) for i in range(k)]
                if new_start:
                    est = best_est
                for e in e_list:
                    res = self._optim(e, est, 80)
                    if self._f(res) > best:
                        best_est = self._mul(res, start_n/len(self.data))
                        best = self._f(res)
                self.data = self._compress(self.data, power)
            self.ans = best_est
            new_start = True
        self.data = data

    def strategy(self, start_cap):  # исходя из начальных инвестиций, выдаем план покупок/продаж
        t = True
        dif = 0
        for i in self.ans:
            if t:
                print("Время покупки:", self.data[round(i)][0], self.data[round(i)][1], "Стоимость акции:",
                      self.data[round(i)][2])
                dif = self.data[round(i)][2]
            else:
                print("Время продажи:", self.data[round(i)][0], self.data[round(i)][1], "Стоимость акции:",
                      self.data[round(i)][2])
                print("#Разница:", round((self.data[round(i)][2] - dif)*start_cap))
            t = not t


# предобработка данных
data0 = []
with open('data.csv', 'r') as file:
    file_iter = csv.reader(file)
    next(file_iter)  # пропускаем строку 'date time price'
    first_data = next(file_iter)  # добавляем первое значение чтобы потом сжать данные
    data0.append([int(first_data[1]), int(first_data[2]), float(first_data[3])])
    for line in file_iter:
        if float(line[3]) != data0[-1][2]:
            data0.append([int(line[1]), int(line[2]), float(line[3])])

answer = StockModel()
n = int(input("Введите количество покупок/продаж: "))
cap = int(input("Введите стартовый капитал: "))
print("Ожидайте:")
answer.fit(data0, 2*n, 2, 20)
answer.strategy(cap)
 
