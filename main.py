import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import pickle


diretorio_imagens = 'fotos_usuarios'
if not os.path.exists(diretorio_imagens):
    os.makedirs(diretorio_imagens)


def carregar_imagem(caminho_imagem):
    imagem = cv2.imread(caminho_imagem)
    if imagem is None:
        raise ValueError(f"Não foi possível carregar a imagem do caminho: {caminho_imagem}")
    return imagem


def converter_para_cinza(imagem):
    return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)


def carregar_classificador():
    return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')


def detectar_rosto(imagem_cinza, classificador):
    return classificador.detectMultiScale(imagem_cinza, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))



def verificar_rosto_no_banco(imagem_rosto, rosto_id):
    arquivo_banco = 'banco_de_dados_faces.pkl'
    if os.path.exists(arquivo_banco):
        with open(arquivo_banco, 'rb') as f:
            banco_de_dados = pickle.load(f)
        if rosto_id in banco_de_dados:
            return True
    return False


def salvar_rosto_no_banco(imagem_rosto, rosto_id):
    arquivo_banco = 'banco_de_dados_faces.pkl'
    if os.path.exists(arquivo_banco):
        with open(arquivo_banco, 'rb') as f:
            banco_de_dados = pickle.load(f)
    else:
        banco_de_dados = {}


    caminho_foto = os.path.join(diretorio_imagens, f'{rosto_id}.jpg')
    cv2.imwrite(caminho_foto, imagem_rosto)
    banco_de_dados[rosto_id] = caminho_foto

    with open(arquivo_banco, 'wb') as f:
        pickle.dump(banco_de_dados, f)


def exibir_imagem(imagem):
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    plt.imshow(imagem_rgb)
    plt.axis('off')
    plt.show()


def selecionar_imagem():
    caminho_imagem = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=[("Arquivos de Imagem", "*.jpg;*.jpeg;*.png")])
    if caminho_imagem:
        try:
            imagem = carregar_imagem(caminho_imagem)
            imagem_cinza = converter_para_cinza(imagem)

            classificador = carregar_classificador()
            rostos = detectar_rosto(imagem_cinza, classificador)

            if len(rostos) == 0:
                messagebox.showinfo("Informação", "Nenhum rosto detectado na imagem.")
                return

            for (x, y, w, h) in rostos:
                rosto_id = f'rosto_{x}_{y}'  # ID único baseado na posição do rosto
                imagem_rosto = imagem[y:y+h, x:x+w]

                if verificar_rosto_no_banco(imagem_rosto, rosto_id):
                    messagebox.showinfo("Reconhecimento", "Rosto já está no banco de dados.")
                else:
                    salvar_rosto_no_banco(imagem_rosto, rosto_id)
                    messagebox.showinfo("Novo Rosto", "Novo rosto salvo no banco de dados.")

            exibir_imagem(imagem)

        except ValueError as ve:
            messagebox.showerror("Erro", f"Erro de valor: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar a imagem: {str(e)}")


root = tk.Tk()
root.title("Detecção e Armazenamento de Rostos")
root.geometry("450x400")
root.config(bg="#f5f5f5")

titulo = tk.Label(root, text="Detector de Rostos", font=("Arial", 18, "bold"), bg="#f5f5f5")
titulo.pack(pady=10)

rotulo_instrucoes = tk.Label(root, text="Selecione uma imagem para detectar e salvar rostos", font=("Arial", 12), bg="#f5f5f5")
rotulo_instrucoes.pack(pady=5)

botao_selecionar = tk.Button(root, text="Selecionar Imagem", command=selecionar_imagem,
                             bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), relief="raised", bd=5)
botao_selecionar.pack(pady=20)

root.mainloop()
