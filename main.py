import cv2
import matplotlib.pyplot as plt

def detectar_rostos(caminho_imagem):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    imagem = cv2.imread(caminho_imagem)
    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    rostos = face_cascade.detectMultiScale(imagem_cinza, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in rostos:
        cv2.rectangle(imagem, (x, y), (x + w, y + h), (255, 0, 0), 2)

    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    plt.imshow(imagem_rgb)
    plt.axis('off')
    plt.show()

caminho_imagem = 'imagem.jpg'
detectar_rostos(caminho_imagem)
