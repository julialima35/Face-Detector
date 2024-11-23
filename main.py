import cv2
import os
import tkinter as tk
from tkinter import filedialog, Toplevel
from PIL import Image, ImageTk
import pickle
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
usuarios_dir = 'usuarios'
os.makedirs(usuarios_dir, exist_ok=True)

def carregar_banco():
    if os.path.exists('banco_usuarios.pkl'):
        with open('banco_usuarios.pkl', 'rb') as f:
            return pickle.load(f)
    return {}

def salvar_banco(banco):
    with open('banco_usuarios.pkl', 'wb') as f:
        pickle.dump(banco, f)

def atualizar_msg(msg):
    lbl_msg.config(text=msg)

def exibir_foto(foto):
    altura_max, largura_max = 400, 400
    proporcao = min(largura_max / foto.shape[1], altura_max / foto.shape[0])
    nova_largura, nova_altura = int(foto.shape[1] * proporcao), int(foto.shape[0] * proporcao)
    foto_rgb = cv2.cvtColor(cv2.resize(foto, (nova_largura, nova_altura)), cv2.COLOR_BGR2RGB)
    foto_tk = ImageTk.PhotoImage(image=Image.fromarray(foto_rgb))
    lbl_foto.config(image=foto_tk)
    lbl_foto.image = foto_tk

def exibir_formulario(nome_usuario):
    frm_cadastro.pack(pady=20)
    lbl_nome.config(text=f"Nome (Usuário: {nome_usuario})")
    for campo in [ent_nome, ent_email, ent_telefone]:
        campo.delete(0, tk.END)

def esconder_formulario():
    frm_cadastro.pack_forget()

def cadastrar_usuario(foto, deteccao, idx):
    bboxC = deteccao.location_data.relative_bounding_box
    h, w, _ = foto.shape
    x, y, w_box, h_box = (int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h))
    usuario = foto[y:y + h_box, x:x + w_box]
    id_usuario = f'usuario_{idx}'

    banco = carregar_banco()
    if id_usuario in banco:
        dados = banco[id_usuario]["dados"]
        atualizar_msg(f"Usuário {id_usuario} já cadastrado.")
        exibir_foto(foto)
        for campo, valor in zip([ent_nome, ent_email, ent_telefone], [dados["nome"], dados["email"], dados["telefone"]]):
            campo.insert(0, valor)
        exibir_formulario(id_usuario)
        return

    atualizar_msg(f"Cadastro do usuário {id_usuario}")
    exibir_formulario(id_usuario)

    def completar_cadastro():
        dados_usuario = { "nome": ent_nome.get(), "email": ent_email.get(), "telefone": ent_telefone.get() }
        caminho_foto = os.path.join(usuarios_dir, f'{id_usuario}.jpg')
        caminho_foto_original = os.path.join(usuarios_dir, f'{id_usuario}_original.jpg')
        cv2.imwrite(caminho_foto, usuario)
        cv2.imwrite(caminho_foto_original, foto)
        banco[id_usuario] = { "foto": caminho_foto, "foto_original": caminho_foto_original, "dados": dados_usuario }
        salvar_banco(banco)
        atualizar_msg(f"Usuário {id_usuario} cadastrado com sucesso.")
        esconder_formulario()
        exibir_foto(foto)

    btn_confirmar.config(command=completar_cadastro)

def processar_foto(foto):
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        foto_rgb = cv2.cvtColor(foto, cv2.COLOR_BGR2RGB)
        resultado = face_detection.process(foto_rgb)
        if not resultado.detections:
            atualizar_msg("Nenhum rosto detectado.")
            return
        for idx, deteccao in enumerate(resultado.detections):
            cadastrar_usuario(foto, deteccao, idx)
            mp_drawing.draw_detection(foto, deteccao)
        exibir_foto(foto)

def escolher_foto():
    caminho = filedialog.askopenfilename(title="Selecione uma foto", filetypes=[("Imagens", "*.jpg;*.jpeg;*.png")])
    if caminho:
        try:
            foto = cv2.imread(caminho)
            if foto is None:
                atualizar_msg(f"Não foi possível carregar a foto: {caminho}")
                return
            processar_foto(foto)
        except Exception as e:
            atualizar_msg(f"Erro ao processar a foto: {str(e)}")

def capturar_foto_com_webcam():
    try:
        captura = cv2.VideoCapture(0)
        if not captura.isOpened():
            atualizar_msg("Não foi possível acessar a câmera.")
            return

        atualizar_msg("Pressione 'Espaço' para capturar a foto ou 'Esc' para sair.")
        while True:
            ret, frame = captura.read()
            if not ret:
                atualizar_msg("Erro ao capturar a imagem.")
                break

            cv2.imshow("Captura de Foto", frame)
            key = cv2.waitKey(1)
            if key == 27: 
                break
            elif key == 32: 
                captura.release()
                cv2.destroyAllWindows()
                processar_foto(frame)
                break
    except Exception as e:
        atualizar_msg(f"Erro ao acessar a câmera: {str(e)}")

def visualizar_banco():
    banco = carregar_banco()
    janela_banco = Toplevel()
    janela_banco.title("Banco de Dados de Usuários")
    janela_banco.geometry("500x600")

    lbl_titulo_banco = tk.Label(janela_banco, text="Usuários Cadastrados", font=("Arial", 16, "bold"))
    lbl_titulo_banco.pack(pady=10)

    for id_usuario, info in banco.items():
        usuario = info["dados"]
        foto_usuario = cv2.imread(info["foto_original"])
        proporcao = min(100 / foto_usuario.shape[1], 100 / foto_usuario.shape[0])
        nova_largura, nova_altura = int(foto_usuario.shape[1] * proporcao), int(foto_usuario.shape[0] * proporcao)
        foto_usuario_resized = cv2.cvtColor(cv2.resize(foto_usuario, (nova_largura, nova_altura)), cv2.COLOR_BGR2RGB)
        foto_usuario_tk = ImageTk.PhotoImage(image=Image.fromarray(foto_usuario_resized))

        frame_usuario = tk.Frame(janela_banco)
        frame_usuario.pack(pady=10)

        lbl_foto_usuario = tk.Label(frame_usuario, image=foto_usuario_tk)
        lbl_foto_usuario.image = foto_usuario_tk
        lbl_foto_usuario.grid(row=0, column=0, padx=10)

        lbl_info_usuario = tk.Label(frame_usuario, text=f"Nome: {usuario['nome']}\nE-mail: {usuario['email']}\nTelefone: {usuario['telefone']}",
                                    font=("Arial", 12))
        lbl_info_usuario.grid(row=0, column=1, padx=10)

app = tk.Tk()
app.title("Detector de Usuários")
app.geometry("450x600")
app.config(bg="#f5f5f5")

lbl_titulo = tk.Label(app, text="Detector de Usuários", font=("Arial", 18, "bold"), bg="#f5f5f5")
lbl_titulo.pack(pady=10)

btn_escolher = tk.Button(app, text="Escolher Foto", command=escolher_foto, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"))
btn_escolher.pack(pady=20)

btn_capturar_ip = tk.Button(app, text="Abrir Câmera", command=capturar_foto_com_webcam, bg="#FFC107", fg="black", font=("Arial", 14, "bold"))
btn_capturar_ip.pack(pady=20)

btn_ver_banco = tk.Button(app, text="Ver Banco de Dados", command=visualizar_banco, bg="#2196F3", fg="white", font=("Arial", 14, "bold"))
btn_ver_banco.pack(pady=20)

lbl_msg = tk.Label(app, text="", font=("Arial", 12), bg="#f5f5f5", fg="blue")
lbl_msg.pack(pady=10)

lbl_foto = tk.Label(app, bg="#f5f5f5")
lbl_foto.pack(pady=20)

frm_cadastro = tk.Frame(app, bg="#f5f5f5")
lbl_nome = tk.Label(frm_cadastro, text="Nome", font=("Arial", 12), bg="#f5f5f5")
lbl_nome.grid(row=0, column=0, padx=10, pady=5)
ent_nome = tk.Entry(frm_cadastro, font=("Arial", 12))
ent_nome.grid(row=0, column=1, padx=10, pady=5)

lbl_email = tk.Label(frm_cadastro, text="E-mail", font=("Arial", 12), bg="#f5f5f5")
lbl_email.grid(row=1, column=0, padx=10, pady=5)
ent_email = tk.Entry(frm_cadastro, font=("Arial", 12))
ent_email.grid(row=1, column=1, padx=10, pady=5)

lbl_telefone = tk.Label(frm_cadastro, text="Telefone", font=("Arial", 12), bg="#f5f5f5")
lbl_telefone.grid(row=2, column=0, padx=10, pady=5)
ent_telefone = tk.Entry(frm_cadastro, font=("Arial", 12))
ent_telefone.grid(row=2, column=1, padx=10, pady=5)

btn_confirmar = tk.Button(frm_cadastro, text="Confirmar Cadastro", font=("Arial", 12), bg="#4CAF50", fg="white")
btn_confirmar.grid(row=3, column=0, columnspan=2, pady=10)

app.mainloop()
