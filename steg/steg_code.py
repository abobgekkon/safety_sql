__author__= 'S.N. Pastuhov'
__copyright__= 'Copyright (c) 2019, S.N. Pastuhov'
__license__= 'Apache License, Version 2.0'


from PIL import Image, ImageDraw
from random import randint
import math


class steganography:

    def img_gen(self, data):
        amount_of_pixels = len(data) * 3
        if amount_of_pixels < 40000:
            amount_of_pixels = 40000
        side = int(math.sqrt(amount_of_pixels)) + 1
        newimg = Image.new("RGB", (side, side))
        w = newimg.size[0]
        (x, y) = (0, 0)

        # генерируем случайные значения для каждого канала
        def rpix():
            return randint(0, 255), randint(0, 255), randint(0, 255)

        # записываем значения пикселей
        for i in range(pow(side, 2)):
            newimg.putpixel((x, y), rpix())
            if (x == w - 1):
                x = 0
                y += 1
            else:
                x += 1

        return newimg

        # рисуем крестики нолики поверх картинки
        # просто для имитации, вы сами можете придумать узор

    def draw_lines(self, img):
        (x, y) = img.size
        draw = ImageDraw.Draw(img)
        for i in range(0, x, x // 10):
            draw.line((i, 0, i, y), (0, 0, 0))
        for i in range(0, y, y // 10):
            draw.line((0, i, x, i), (0, 0, 0))

        for i in range(0, x, x // 10):
            for j in range(0, y, y // 10):
                if (randint(0, 1) == 1):
                    draw.line((i, j, i + x // 10, j + y // 10), (0, 0, 0))
                    draw.line((i, j + y // 10, i + x // 10, j), (0, 0, 0))
                else:
                    draw.ellipse((i, j, i + x // 10, j + y // 10), outline=(0, 0, 0))
        return img

        # создаем бинарный список всех символов сообщения

    def genData(self, data):
        newd = []

        for i in data:
            #newd.append(format(ord(i), '08b'))
            newd.append(format(i, '08b'))
        return newd

        # модификация пикселей на основе списка бинарного представления символов

    def modPix(self, pix, data):
        datalist = self.genData(data)
        lendata = len(datalist)
        imdata = iter(pix)

        for i in range(lendata):

            pix = [value for value in imdata.__next__()[:3] +
                   imdata.__next__()[:3] +
                   imdata.__next__()[:3]]

            # делаем значения нечетными для 1
            # четными для 0
            for j in range(0, 8):
                if (datalist[i][j] == '0') and (pix[j] % 2 != 0):
                    if pix[j] != 0:
                        pix[j] -= 1
                    elif pix[j] == 0:
                        pix[j] += 2

                elif (datalist[i][j] == '1') and (pix[j] % 2 == 0):
                    if pix[j] != 0:
                        pix[j] -= 1
                    elif pix[j] == 0:
                        pix[j] = 1

            # если сообщение окончено, то значение
            # последнего канала - 0
            # если продолжаем чтение, то 1
            if (i == lendata - 1):
                if (pix[-1] % 2 == 0):
                    if pix[-1] == 0:
                        pix[-1] += 1
                    elif pix[-1] == 1:
                        pix[-1] += 2
                    else:
                        pix[-1] -= 1
            else:
                if (pix[-1] % 2 != 0):
                    pix[-1] -= 1

            pix = tuple(pix)
            yield pix[0:3]
            yield pix[3:6]
            yield pix[6:9]

    def encode_enc(self, newimg, data):
        w = newimg.size[0]
        (x, y) = (0, 0)

        for pixel in self.modPix(newimg.getdata(), data):

            newimg.putpixel((x, y), pixel)
            if (x == w - 1):
                x = 0
                y += 1
            else:
                x += 1

    def encode(self, data, filename):
        if (len(data) == 0):
            raise ValueError('steg encode - ошибка приема данных')

        img = self.img_gen(data)
        newimg = self.draw_lines(img)
        self.encode_enc(newimg, data)

        newimg.save(filename)


    def decode(self, filename):
        image = Image.open(filename, 'r')

        data = ''
        imgdata = iter(image.getdata())

        while (True):
            pixels = [value for value in imgdata.__next__()[:3] +
                      imgdata.__next__()[:3] +
                      imgdata.__next__()[:3]]

            binstr = ''

            for i in pixels[:8]:
                if (i % 2 == 0):
                    binstr += '0'
                else:
                    binstr += '1'

            data += chr(int(binstr, 2))
            if (pixels[-1] % 2 != 0):
                return bytes(data, "UTF-8")
