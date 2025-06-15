import cv2
import numpy as np
from PIL import Image


##FILTROS CALCULADOS
def aplicar_filtro_mediana(imagen, ancho, alto):
    imagen_np = np.array(imagen)  # convertir la imagen a un array de numpy
    imagen_mediana = np.zeros_like(imagen_np)  # crear un array vacio para la nueva imagen

    for y in range(alto):
        for x in range(ancho):
            for canal in range(imagen_np.shape[2]): #para agregar un bucle para los canales de color => al ser RGB es una tupla de 3 valores iguales
                vecinos = []
                #Ahora se calculara los pixeles vecinos del pixel_central
                #Por tanto, recorrera los vecinos en una ventana 3x3  => por tanto tambien el pixel central
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < ancho and 0 <= ny < alto: #para asegurar que el vecino este dentro de los limites de la imagen
                            vecinos.append(imagen_np[ny, nx, canal])
                
                #Aplicar el filtro de la mediana al pixel
                vecinos.sort()
                mid = len(vecinos) // 2
                if len(vecinos) % 2 == 0:
                    imagen_mediana[y, x, canal] = (vecinos[mid-1] + vecinos[mid]) // 2
                else:
                    imagen_mediana[y, x, canal] = vecinos[mid]
                

    #Convertir el array de numpy de nuevo a una imagen de PIL para mostrar en streamlit
    return Image.fromarray(imagen_mediana)

def aplicar_filtro_media(imagen, ancho, alto, mascara):
    imagen_np = np.array(imagen)  
    imagen_media = np.zeros_like(imagen_np)  # crear un array vacio para la nueva imagen

    #Definición de máscaras como matrices 3x3
    mascara1 = np.array([1/9, 1/9, 1/9, 1/9, 1/9, 1/9, 1/9, 1/9, 1/9]).reshape(3, 3)
    mascara2 = np.array([1/16, 2/16, 1/16, 2/16, 4/16, 2/16, 1/16, 2/16, 1/16]).reshape(3, 3)

    if mascara == 1:
        mascara = mascara1
    elif mascara == 2:
        mascara = mascara2

    for y in range(alto):
        for x in range(ancho):
            for canal in range(imagen_np.shape[2]):
                suma = 0  
                #Ahora se calculara los pixeles vecinos del pixel_central
                #Por tanto, recorrera los vecinos en una ventana 3x3
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < ancho and 0 <= ny < alto:
                            valor_pixel = imagen_np[ny, nx, canal]
                        else:
                            valor_pixel = 0  #para que si se salen de los borden cuenten como cero
                        #print(f"{valor_pixel} x {mascara[dy + 1, dx + 1]} = {valor_pixel*mascara[dy + 1, dx + 1]}")
                        suma += valor_pixel * mascara[dy + 1, dx + 1]
                    #print(suma)

                # Asignar el nuevo valor al pixel
                #imagen_media[y, x, canal] = int(np.clip(suma, 0, 255))
                imagen_media[y, x, canal] = int(np.floor(suma + 0.5)) #no funciono np.round() porque redondea al mas cercano => 2.5 = 2 
                #imagen_media[y, x] = int(np.floor(suma + 0.5))  
                #print(imagen_media[y, x])
                

    #Convertir el array de numpy de nuevo a una imagen de PIL para mostrar en streamlit
    return Image.fromarray(imagen_media)


#Para considerar a color
'''
def aplicar_filtro_laplaciano(imagen, ancho, alto, mascara):
    imagen_np = np.array(imagen)  

    #definicion de máscaras como matrices 3x3
    mascara1 = np.array([0, 1, 0, 1, -4, 1, 0, 1, 0]).reshape(3, 3)
    mascara2 = np.array([0, -1, 0, -1, 4, -1, 0, -1, 0]).reshape(3, 3)
    mascara3 = np.array([1, 1, 1, 1, -8, 1, 1, 1, 1]).reshape(3, 3)
    mascara4 = np.array([-1, -1, -1, -1, 8, -1, -1, -1, -1]).reshape(3, 3)

    if mascara == 1:
        mascara = mascara1
    elif mascara == 2:
        mascara = mascara2
    elif mascara == 3:
        mascara = mascara3
    elif mascara == 4:
        mascara = mascara4

    escalar = np.zeros((alto, ancho, imagen_np.shape[2]), dtype=float)

    for y in range(alto):
        for x in range(ancho):
            for canal in range(imagen_np.shape[2]):
                suma = 0  
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < ancho and 0 <= ny < alto:
                            valor_pixel = imagen_np[ny, nx, canal]
                        else:
                            valor_pixel = 0
                        suma += valor_pixel * mascara[dy + 1, dx + 1]
                escalar[y, x, canal] = suma

    #Hallamos la recta que pasa por (x1; 0) y (x2; 7) ya que 𝐿 = 256 y lo que se quiere es reescalar al intervalo [𝟎; 𝑳 − 𝟏]
    #Seria un sistema de ecuaciones
    #y = xm + b
    #0 = x1m + b  =>  0  = -x1x2m - x2b
    #7 = x2m + b  => 7x1 =  x1x2m + x1b

    # 7x1 = (x1-x2)b
    # b = 7x1 / (x1-x2)

    #m =  -(7x1 / (x1-x2)) / x1

    x1, x2 = escalar.min(), escalar.max()
    m = 255 / (x2 - x1) if x2 != x1 else 0
    b = -m * x1

    for y in range(alto):
        for x in range(ancho):
            for canal in range(imagen_np.shape[2]):
                escalar[y, x, canal] = int(np.floor(m * escalar[y, x, canal] + b + 0.5))

    return Image.fromarray(escalar.astype(np.uint8))
'''

#Para tonos de grises
def aplicar_filtro_laplaciano(imagen, ancho, alto, mascara):
    imagen = np.array(imagen.convert('L'))  

    # definición de máscaras como matrices 3x3
    mascara1 = np.array([0, 1, 0, 1, -4, 1, 0, 1, 0]).reshape(3, 3)
    mascara2 = np.array([0, -1, 0, -1, 4, -1, 0, -1, 0]).reshape(3, 3)
    mascara3 = np.array([1, 1, 1, 1, -8, 1, 1, 1, 1]).reshape(3, 3)
    mascara4 = np.array([-1, -1, -1, -1, 8, -1, -1, -1, -1]).reshape(3, 3)

    if mascara == 1:
        mascara = mascara1
    elif mascara == 2:
        mascara = mascara2
    elif mascara == 3:
        mascara = mascara3
    elif mascara == 4:
        mascara = mascara4

    escalar = np.zeros((alto, ancho), dtype=float)

    for y in range(1, alto-1):  # Ajusta los límites para manejar bordes
        for x in range(1, ancho-1):
            suma = 0  
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    ny, nx = y + dy, x + dx
                    if 0 <= nx < ancho and 0 <= ny < alto:
                        valor_pixel = imagen[ny, nx]
                    else:
                        valor_pixel = 0
                    suma += valor_pixel * mascara[dy + 1, dx + 1]
            escalar[y, x] = suma


    #Hallamos la recta que pasa por (x1; 0) y (x2; 7) ya que 𝐿 = 256 y lo que se quiere es reescalar al intervalo [𝟎; 𝑳 − 𝟏]
    #Seria un sistema de ecuaciones
    #y = xm + b
    #0 = x1m + b  =>  0  = -x1x2m - x2b
    #7 = x2m + b  => 7x1 =  x1x2m + x1b

    # 7x1 = (x1-x2)b
    # b = 7x1 / (x1-x2)

    #m =  -(7x1 / (x1-x2)) / x1

    x1, x2 = escalar.min(), escalar.max()
    m = 255 / (x2 - x1) if x2 != x1 else 0
    b = -m * x1

    for y in range(alto):
        for x in range(ancho):
            escalar[y, x] = np.clip(int(np.floor(m * escalar[y, x] + b + 0.5)), 0, 255)

    return Image.fromarray(escalar.astype(np.uint8))
    

'''
def aplicar_filtro_sobel(imagen, ancho, alto):
    imagen_np = np.array(imagen)  

    #Definicion de máscaras como matrices 3x3 para Sobel
    mascarax = np.array([-1, -2, -1, 0, 0, 0, 1, 2, 1]).reshape(3, 3)
    mascaray = np.array([-1, 0, 1, -2, 0, 2, -1, 0, 1]).reshape(3, 3)
    
    # Preparar el array para almacenar el resultado del filtro Sobel
    escalar = np.zeros((alto, ancho, imagen_np.shape[2]), dtype=float)

    for y in range(alto):
        for x in range(ancho):
            for canal in range(imagen_np.shape[2]):
                sumax = 0  
                sumay = 0
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < ancho and 0 <= ny < alto:
                            valor_pixel = imagen_np[ny, nx, canal]
                        else:
                            valor_pixel = 0 
                        sumax += valor_pixel * mascarax[dy + 1, dx + 1]
                        sumay += valor_pixel * mascaray[dy + 1, dx + 1]
                # Calcular la magnitud del gradiente en el punto (x, y)
                escalar[y, x, canal] = sumax
                escalar[y, x, canal] = sumay
                #escalar[y, x, canal] = np.sqrt(sumax**2 + sumay**2)  #Por teoria 
                escalar[y, x, canal] = np.sum(sumax + sumay) #Por teoria

    
    #Hallamos la recta que pasa por (x1; 0) y (x2; 7) ya que 𝐿 = 256 y lo que se quiere es reescalar al intervalo [𝟎; 𝑳 − 𝟏]
    #Seria un sistema de ecuaciones
    #y = xm + b
    #0 = x1m + b  =>  0  = -x1x2m - x2b
    #7 = x2m + b  => 7x1 =  x1x2m + x1b

    # 7x1 = (x1-x2)b
    # b = 7x1 / (x1-x2)

    #m =  -(7x1 / (x1-x2)) / x1
    
    #reescalado del resultado para visualización
    x1, x2 = escalar.min(), escalar.max()
    m = 255 / (x2 - x1) if x2 != x1 else 0
    b = -m * x1

    for y in range(alto):
        for x in range(ancho):
            for canal in range(imagen_np.shape[2]):
                escalar[y, x, canal] = np.clip(int(np.floor(m * escalar[y, x, canal] + b + 0.5)), 0, 255)

    return Image.fromarray(escalar.astype(np.uint8))
'''

#Filtro en tonos de grises
def aplicar_filtro_sobel(imagen, ancho, alto):
    imagen_np = np.array(imagen.convert('L')) 

    # Definición de máscaras como matrices 3x3 para Sobel
    mascarax = np.array([-1, 0, 1, -2, 0, 2, -1, 0, 1]).reshape(3, 3)
    mascaray = np.array([-1, -2, -1, 0, 0, 0, 1, 2, 1]).reshape(3, 3)
    
    escalar = np.zeros((alto, ancho), dtype=float)

    for y in range(1, alto-1):  #comienza en 1 y terminar en alto-1 para evitar bordes
        for x in range(1, ancho-1):
            sumax = 0
            sumay = 0
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    #se asegura de que el índice está dentro de los límites de la imagen
                    if 0 <= nx < ancho and 0 <= ny < alto:
                        valor_pixel = imagen_np[ny, nx]
                    else:
                        valor_pixel = 0 
                    sumax += valor_pixel * mascarax[dy + 1, dx + 1]
                    sumay += valor_pixel * mascaray[dy + 1, dx + 1]
            #combina las sumas para obtener la magnitud del gradiente
            escalar[y, x] = np.sqrt(sumax**2 + sumay**2)

    # Reescalado del resultado para visualización
    x1, x2 = escalar.min(), escalar.max()
    m = 255 / (x2 - x1) if x2 != x1 else 0
    b = -m * x1

    for y in range(alto):
        for x in range(ancho):
            escalar[y, x] = np.clip(int(np.floor(m * escalar[y, x] + b + 0.5)), 0, 255)

    return Image.fromarray(escalar.astype(np.uint8))
