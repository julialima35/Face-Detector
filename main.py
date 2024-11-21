import cv2
import os
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
import pickle
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
pasta_usuarios = 'usuarios'

if not os.path.exists(pasta_usuarios):
    os.makedirs(pasta_usuarios)

def carregar_banco():
    if os.path.exists('banco_usuarios.pkl'):
        with open('banco_usuarios.pkl', 'rb') as f:
            return pickle.load(f)
    return {}

def salvar_banco(banco):
    with open('banco_usuarios.pkl', 'wb') as f:
        pickle.dump(banco, f)

def mostrar_foto(foto):
    altura_max, largura_max = 400, 400
    altura, largura = foto.shape[:2]
    proporcao = min(largura_max / largura, altura_max / altura)
    nova_largura, nova_altura = int(largura * proporcao), int(altura * proporcao)
    foto_rgb = cv2.cvtColor(cv2.resize(foto, (nova_largura, nova_altura)), cv2.COLOR_BGR2RGB)
    foto_tk = ImageTk.PhotoImage(image=Image.fromarray(foto_rgb))
    lbl_foto.config(image=foto_tk)
    lbl_foto.image = foto_tk

def atualizar_msg(msg):
    lbl_msg.config(text=msg)

def exibir_formulario(nome_usuario):
    """Exibe o formulário de cadastro se o usuário não estiver cadastrado."""
    if not frm_cadastro.winfo_ismapped():
        frm_cadastro.pack(pady=20)

    lbl_nome.config(text=f"Nome (Usuário: {nome_usuario})")
    ent_nome.delete(0, tk.END)
    ent_email.delete(0, tk.END)
    ent_telefone.delete(0, tk.END)

def esconder_formulario():
    """Esconde o formulário de cadastro após completar o cadastro."""
    frm_cadastro.pack_forget()

def cadastrar_usuario(foto, deteccao, idx):
    bboxC = deteccao.location_data.relative_bounding_box
    h, w, _ = foto.shape
    x, y, w_box, h_box = (int(bboxC.xmin * w), int(bboxC.ymin * h),
                          int(bboxC.width * w), int(bboxC.height * h))
    usuario = foto[y:y + h_box, x:x + w_box]
    id_usuario = f'usuario_{idx}'

    banco = carregar_banco()
    if id_usuario in banco:
        atualizar_msg(f"Usuário {id_usuario} já cadastrado.")
        mostrar_foto(foto)
        return

    atualizar_msg(f"Cadastro do usuário {id_usuario}")
    exibir_formulario(id_usuario)

    def completar_cadastro():
        """Completa o cadastro após preencher o formulário."""
        nome = ent_nome.get()
        email = ent_email.get()
        telefone = ent_telefone.get()

        dados_usuario = {"nome": nome, "email": email, "telefone": telefone}

        caminho_foto = os.path.join(pasta_usuarios, f'{id_usuario}.jpg')
        cv2.imwrite(caminho_foto, usuario)
        banco[id_usuario] = {"foto": caminho_foto, "dados": dados_usuario}
        salvar_banco(banco)
        atualizar_msg(f"Usuário {id_usuario} cadastrado com sucesso.")
        esconder_formulario()
        mostrar_foto(foto)

    btn_confirmar.config(command=completar_cadastro)

def processar_foto(foto):
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        foto_rgb = cv2.cvtColor(foto, cv2.COLOR_BGR2RGB)
        resultado = face_detection.process(foto_rgb)
        if not resultado.detections:
            atualizar_msg("Nenhum rosto detectado.")
            return

        for idx, deteccao in enumerate(resultado.detections):
            cadastrar_usuario(foto, deteccao, idx)
            mp_drawing.draw_detection(foto, deteccao)
        mostrar_foto(foto)

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

def capturar_foto_com_webcam_local():
    try:
        captura = cv2.VideoCapture(0)  # Usando o índice 0 para a câmera local
        if not captura.isOpened():
            atualizar_msg("Não foi possível acessar a câmera local.")
            return

        atualizar_msg("Pressione 'Espaço' para capturar a foto ou 'Esc' para sair.")
        while True:
            ret, frame = captura.read()
            if not ret:
                atualizar_msg("Erro ao capturar a imagem.")
                break

            cv2.imshow("Captura de Foto - Pressione 'Espaço' para capturar", frame)
            key = cv2.waitKey(1)
            if key == 27:  # Pressione 'Esc' para sair
                break
            elif key == 32:  # Pressione 'Espaço' para capturar a foto
                captura.release()
                cv2.destroyAllWindows()
                processar_foto(frame)
                break
    except Exception as e:
        atualizar_msg(f"Erro ao acessar a câmera local: {str(e)}")


app = tk.Tk()
app.title("Detector de Usuários")
app.geometry("450x600")
app.config(bg="#f5f5f5")

lbl_titulo = tk.Label(app, text="Detector de Usuários", font=("Arial", 18, "bold"), bg="#f5f5f5")
lbl_titulo.pack(pady=10)

lbl_instr = tk.Label(app, text="Escolha uma foto ou use a câmera para detectar usuários", font=("Arial", 12), bg="#f5f5f5")
lbl_instr.pack(pady=5)

btn_escolher = tk.Button(app, text="Escolher Foto", command=escolher_foto, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), relief="raised", bd=5)
btn_escolher.pack(pady=20)

btn_capturar_ip = tk.Button(app, text="Abrir Câmera", command=capturar_foto_com_webcam_local, bg="#FFC107", fg="black", font=("Arial", 14, "bold"), relief="raised", bd=5)
btn_capturar_ip.pack(pady=20)

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

btn_confirmar = tk.Button(frm_cadastro, text="Confirmar Cadastro", font=("Arial", 12), bg="#4CAF50", fg="white", relief="raised", bd=5)
btn_confirmar.grid(row=3, column=0, columnspan=2, pady=10)

app.mainloop()
