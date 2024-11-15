import cv2
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog


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
    """Carrega o classificador de acordo com o tipo selecionado"""
    if tipo == 'rosto':
        return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    elif tipo == 'olho':
        return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    elif tipo == 'boca':
        return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    else:
        raise ValueError("Tipo desconhecido de classificador.")


def detectar_elementos(imagem_cinza, classificador):
    """Detecta os elementos na imagem de acordo com o classificador fornecido"""
    return classificador.detectMultiScale(imagem_cinza, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))


def desenhar_elementos(imagem, elementos):
    """Desenha retângulos ao redor dos elementos detectados"""
    for (x, y, w, h) in elementos:
        cv2.rectangle(imagem, (x, y), (x + w, y + h), (255, 0, 0), 2)


def exibir_imagem(imagem):
    """Exibe a imagem processada com o Matplotlib"""
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    plt.imshow(imagem_rgb)
    plt.axis('off')
    plt.show()


def salvar_imagem(imagem):
    """Permite salvar a imagem com os elementos detectados"""
    caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
    if caminho_arquivo:
        cv2.imwrite(caminho_arquivo, imagem)
        messagebox.showinfo("Sucesso", "Imagem salva com sucesso!")


def selecionar_imagem():
    """Função chamada quando o usuário seleciona uma imagem"""
    caminho_imagem = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=[("Arquivos de Imagem", "*.jpg;*.jpeg;*.png")])
    if caminho_imagem:
        try:
            tipos_detecao = tipo_deteccao.get().split(',')
            classificador_map = {'rosto': 'haarcascade_frontalface_alt2.xml', 'olho': 'haarcascade_eye.xml', 'boca': 'haarcascade_smile.xml'}
            imagem = carregar_imagem(caminho_imagem)

            imagem_cinza = converter_para_cinza(imagem)
            imagem_cinza = equalizar_histograma(imagem_cinza)

            for tipo in tipos_detecao:
                classificador = carregar_classificador(tipo)
                elementos = detectar_elementos(imagem_cinza, classificador)
                desenhar_elementos(imagem, elementos)

            exibir_imagem(imagem)

            # Perguntar ao usuário se deseja salvar a imagem
            resposta = messagebox.askyesno("Salvar imagem", "Deseja salvar a imagem processada?")
            if resposta:
                salvar_imagem(imagem)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar a imagem: {str(e)}")


def ajustar_zoom(imagem):
    """Permite ao usuário ajustar o zoom da imagem"""
    fator_zoom = simpledialog.askfloat("Zoom", "Digite o fator de zoom (ex: 1.0 para normal, 1.5 para 50% maior):", minvalue=0.1, maxvalue=10.0)
    if fator_zoom:
        altura, largura = imagem.shape[:2]
        nova_largura = int(largura * fator_zoom)
        nova_altura = int(altura * fator_zoom)
        imagem_zoomin = cv2.resize(imagem, (nova_largura, nova_altura))
        exibir_imagem(imagem_zoomin)


root = tk.Tk()
root.title("Detecção de Elementos")
root.geometry("450x400")  
root.config(bg="#f5f5f5")

titulo = tk.Label(root, text="Detector de Elementos", font=("Arial", 18, "bold"), bg="#f5f5f5")
titulo.pack(pady=10)

rotulo_instrucoes = tk.Label(root, text="Escolha os tipos de detecção e selecione uma imagem", font=("Arial", 12), bg="#f5f5f5")
rotulo_instrucoes.pack(pady=5)

tipo_deteccao = tk.StringVar(value="rosto")
opcoes_deteccao = tk.OptionMenu(root, tipo_deteccao, "rosto", "olho", "boca", "rosto,olho", "rosto,boca", "olho,boca", "rosto,olho,boca")
opcoes_deteccao.config(font=("Arial", 12), relief="raised", width=15)
opcoes_deteccao.pack(pady=10)

botao_selecionar = tk.Button(root, text="Selecionar Imagem", command=selecionar_imagem,
                             bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), relief="raised", bd=5)
botao_selecionar.pack(pady=20)

botao_zoom = tk.Button(root, text="Ajustar Zoom", command=lambda: ajustar_zoom(cv2.imread(filedialog.askopenfilename())) ,
                       bg="#2196F3", fg="white", font=("Arial", 14, "bold"), relief="raised", bd=5)
botao_zoom.pack(pady=10)

root.mainloop()
