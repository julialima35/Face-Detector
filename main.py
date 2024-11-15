import cv2
import matplotlib.pyplot as plt


def carregar_imagem(caminho_imagem):
    imagem = cv2.imread(caminho_imagem)
    if imagem is None:
        raise ValueError(f"Não foi possível carregar a imagem do caminho: {caminho_imagem}")
    return imagem


def converter_para_cinza(imagem):
    return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)


def detectar_rostos(imagem_cinza, face_cascade):
    return face_cascade.detectMultiScale(imagem_cinza, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))


def desenhar_rostos(imagem, rostos):
    for (x, y, w, h) in rostos:
        cv2.rectangle(imagem, (x, y), (x + w, y + h), (255, 0, 0), 2)


def exibir_imagem(imagem):
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    plt.imshow(imagem_rgb)
    plt.axis('off')
    plt.show()


def detectar_rostos_na_imagem(caminho_imagem):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    imagem = carregar_imagem(caminho_imagem)
    imagem_cinza = converter_para_cinza(imagem)
    rostos = detectar_rostos(imagem_cinza, face_cascade)
    desenhar_rostos(imagem, rostos)
    exibir_imagem(imagem)


caminho_imagem = 'imagem.jpg'
detectar_rostos_na_imagem(caminho_imagem)
