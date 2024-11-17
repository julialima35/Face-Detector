import cv2
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox

def carregar_imagem(caminho_imagem):
    imagem = cv2.imread(caminho_imagem)
    if imagem is None:
        raise ValueError(f"Não foi possível carregar a imagem do caminho: {caminho_imagem}")
    return imagem

def converter_para_cinza(imagem):
    return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

def equalizar_histograma(imagem_cinza):
    return cv2.equalizeHist(imagem_cinza)

def carregar_classificador(tipo):
    classificadores = {
        'rosto': 'haarcascade_frontalface_alt2.xml',
        'olho': 'haarcascade_eye.xml',
        'boca': 'haarcascade_smile.xml'
    }
    if tipo not in classificadores:
        raise ValueError("Tipo desconhecido de classificador.")
    return cv2.CascadeClassifier(cv2.data.haarcascades + classificadores[tipo])

def detectar_elementos(imagem_cinza, classificador):
    return classificador.detectMultiScale(imagem_cinza, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

def desenhar_elementos(imagem, elementos):
    for (x, y, w, h) in elementos:
        cv2.rectangle(imagem, (x, y), (x + w, y + h), (255, 0, 0), 2)

def exibir_imagem(imagem):
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    plt.imshow(imagem_rgb)
    plt.axis('off')
    plt.show()

def salvar_imagem(imagem):
    caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
    if caminho_arquivo:
        cv2.imwrite(caminho_arquivo, imagem)
        messagebox.showinfo("Sucesso", "Imagem salva com sucesso!")

def selecionar_imagem():
    caminho_imagem = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=[("Arquivos de Imagem", "*.jpg;*.jpeg;*.png")])
    if caminho_imagem:
        try:
            tipos_detecao = [tipo.get() for tipo in checkboxes if tipo.get()]
            imagem = carregar_imagem(caminho_imagem)

            imagem_cinza = converter_para_cinza(imagem)
            imagem_cinza = equalizar_histograma(imagem_cinza)

            for tipo in tipos_detecao:
                classificador = carregar_classificador(tipo)
                elementos = detectar_elementos(imagem_cinza, classificador)
                desenhar_elementos(imagem, elementos)

            exibir_imagem(imagem)

            if messagebox.askyesno("Salvar imagem", "Deseja salvar a imagem processada?"):
                salvar_imagem(imagem)

        except ValueError as ve:
            messagebox.showerror("Erro", f"Erro de valor: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar a imagem: {str(e)}")

root = tk.Tk()
root.title("Detecção de Elementos")
root.geometry("450x400")
root.config(bg="#f5f5f5")

titulo = tk.Label(root, text="Detector de Elementos", font=("Arial", 18, "bold"), bg="#f5f5f5")
titulo.pack(pady=10)

rotulo_instrucoes = tk.Label(root, text="Escolha os tipos de detecção e selecione uma imagem", font=("Arial", 12), bg="#f5f5f5")
rotulo_instrucoes.pack(pady=5)

checkboxes = []

def criar_checkbox(tipo):
    var = tk.StringVar(value=tipo)
    checkbox = tk.Checkbutton(root, text=tipo.capitalize(), variable=var, onvalue=tipo, offvalue="")
    checkbox.pack(anchor="w")
    checkboxes.append(var)

criar_checkbox("rosto")
criar_checkbox("olho")
criar_checkbox("boca")

botao_selecionar = tk.Button(root, text="Selecionar Imagem", command=selecionar_imagem,
                             bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), relief="raised", bd=5)
botao_selecionar.pack(pady=20)

root.mainloop()
