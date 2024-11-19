import cv2
import os
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
import numpy as np
import pickle


pasta_usuarios = 'usuarios'
if not os.path.exists(pasta_usuarios):
    os.makedirs(pasta_usuarios)


def carregar_foto(caminho):
    foto = cv2.imread(caminho)
    if foto is None:
        raise ValueError(f"Não foi possível carregar a foto: {caminho}")
    return foto

def foto_cinza(foto):
    return cv2.cvtColor(foto, cv2.COLOR_BGR2GRAY)

def carregar_modelo():
    return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')

def detectar_usuarios(foto_cinza, modelo):
    return modelo.detectMultiScale(foto_cinza, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

def carregar_banco():
    arquivo_banco = 'banco_usuarios.pkl'
    if os.path.exists(arquivo_banco):
        with open(arquivo_banco, 'rb') as f:
            return pickle.load(f)
    return {}

def salvar_banco(banco):
    arquivo_banco = 'banco_usuarios.pkl'
    with open(arquivo_banco, 'wb') as f:
        pickle.dump(banco, f)

def usuario_no_banco(id_usuario):
    banco = carregar_banco()
    return id_usuario in banco

def salvar_usuario(usuario, id_usuario, dados_usuario):
    banco = carregar_banco()

    caminho_foto = os.path.join(pasta_usuarios, f'{id_usuario}.jpg')
    cv2.imwrite(caminho_foto, usuario)

    banco[id_usuario] = {
        "foto": caminho_foto,
        "dados": dados_usuario
    }

    salvar_banco(banco)

def exibir_dados_usuario():
    banco = carregar_banco()
    if not banco:
        atualizar_msg("Nenhum usuário cadastrado.")
        return
    
    janela_dados = tk.Toplevel(app)
    janela_dados.title("Dados dos Usuários")
    janela_dados.geometry("400x400")
    janela_dados.config(bg="#f5f5f5")

    texto = tk.Text(janela_dados, wrap=tk.WORD, font=("Arial", 12), bg="#f5f5f5")
    texto.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    for id_usuario, info in banco.items():
        dados = info["dados"]
        texto.insert(tk.END, f"ID: {id_usuario}\n")
        texto.insert(tk.END, f"Nome: {dados['nome']}\n")
        texto.insert(tk.END, f"E-mail: {dados['email']}\n")
        texto.insert(tk.END, f"Telefone: {dados['telefone']}\n")
        texto.insert(tk.END, "-" * 40 + "\n")

    texto.config(state=tk.DISABLED)

def atualizar_msg(msg):
    lbl_msg.config(text=msg)

def mostrar_foto(foto):
    largura_max = 400
    altura_max = 400
    
    altura, largura = foto.shape[:2]
    proporcao = min(largura_max / largura, altura_max / altura)
    nova_largura = int(largura * proporcao)
    nova_altura = int(altura * proporcao)
    
    foto_redimensionada = cv2.resize(foto, (nova_largura, nova_altura))
    
    foto_rgb = cv2.cvtColor(foto_redimensionada, cv2.COLOR_BGR2RGB)
    foto_pil = Image.fromarray(foto_rgb)
    foto_tk = ImageTk.PhotoImage(foto_pil)

    lbl_foto.config(image=foto_tk)
    lbl_foto.image = foto_tk


def escolher_foto():
    caminho = filedialog.askopenfilename(title="Selecione uma foto", filetypes=[("Imagens", "*.jpg;*.jpeg;*.png")])
    if caminho:
        try:
            foto = carregar_foto(caminho)
            cinza = foto_cinza(foto)

            modelo = carregar_modelo()
            usuarios = detectar_usuarios(cinza, modelo)

            if len(usuarios) == 0:
                atualizar_msg("Nenhum usuário detectado.")
                return

            for (x, y, w, h) in usuarios:
                id_usuario = f'usuario_{x}_{y}'
                usuario = foto[y:y+h, x:x+w]

                if usuario_no_banco(id_usuario):
                    atualizar_msg("Usuário já cadastrado.")
                else:
                    nome = simpledialog.askstring("Nome", "Digite o nome do usuário:")
                    email = simpledialog.askstring("E-mail", "Digite o e-mail do usuário:")
                    telefone = simpledialog.askstring("Telefone", "Digite o telefone do usuário:")

                    dados_usuario = {
                        "nome": nome,
                        "email": email,
                        "telefone": telefone
                    }

                    salvar_usuario(usuario, id_usuario, dados_usuario)
                    atualizar_msg("Novo usuário cadastrado com sucesso.")

            mostrar_foto(foto)

        except ValueError as ve:
            atualizar_msg(f"Erro: {str(ve)}")
        except Exception as e:
            atualizar_msg(f"Erro ao processar: {str(e)}")


app = tk.Tk()
app.title("Detector de Usuários")
app.geometry("450x600")
app.config(bg="#f5f5f5")

lbl_titulo = tk.Label(app, text="Detector de Usuários", font=("Arial", 18, "bold"), bg="#f5f5f5")
lbl_titulo.pack(pady=10)

lbl_instr = tk.Label(app, text="Escolha uma foto para detectar usuários", font=("Arial", 12), bg="#f5f5f5")
lbl_instr.pack(pady=5)

btn_escolher = tk.Button(app, text="Escolher Foto", command=escolher_foto, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), relief="raised", bd=5)
btn_escolher.pack(pady=20)

btn_exibir = tk.Button(app, text="Exibir Dados dos Usuários", command=exibir_dados_usuario, bg="#2196F3", fg="white", font=("Arial", 14, "bold"), relief="raised", bd=5)
btn_exibir.pack(pady=10)

lbl_msg = tk.Label(app, text="", font=("Arial", 12), bg="#f5f5f5", fg="blue")
lbl_msg.pack(pady=10)

lbl_foto = tk.Label(app, bg="#f5f5f5")
lbl_foto.pack(pady=20)

app.mainloop()
