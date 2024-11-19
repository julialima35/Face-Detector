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
    else:
        nome = simpledialog.askstring("Nome", "Digite o nome do usuário:")
        email = simpledialog.askstring("E-mail", "Digite o e-mail do usuário:")
        telefone = simpledialog.askstring("Telefone", "Digite o telefone do usuário:")
        dados_usuario = {"nome": nome, "email": email, "telefone": telefone}

        caminho_foto = os.path.join(pasta_usuarios, f'{id_usuario}.jpg')
        cv2.imwrite(caminho_foto, usuario)
        banco[id_usuario] = {"foto": caminho_foto, "dados": dados_usuario}
        salvar_banco(banco)
        atualizar_msg(f"Usuário {id_usuario} cadastrado com sucesso.")

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

def capturar_foto_ip_webcam():
    try:
        captura = cv2.VideoCapture("http://192.168.1.35:8080/video")
        if not captura.isOpened():
            atualizar_msg("Não foi possível acessar o IP Webcam.")
            return

        atualizar_msg("Pressione 'Espaço' para capturar a foto ou 'Esc' para sair.")
        while True:
            ret, frame = captura.read()
            if not ret:
                atualizar_msg("Erro ao capturar a imagem.")
                break

            cv2.imshow("Captura de Foto - Pressione 'Espaço' para capturar", frame)
            key = cv2.waitKey(1)
            if key == 27: 
                break
            elif key == 32: 
                captura.release()
                cv2.destroyAllWindows()
                processar_foto(frame)
                break
    except Exception as e:
        atualizar_msg(f"Erro ao acessar o IP Webcam: {str(e)}")

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

btn_capturar_ip = tk.Button(app, text="Capturar Foto com IP Webcam", command=capturar_foto_ip_webcam, bg="#FFC107", fg="black", font=("Arial", 14, "bold"), relief="raised", bd=5)
btn_capturar_ip.pack(pady=20)

lbl_msg = tk.Label(app, text="", font=("Arial", 12), bg="#f5f5f5", fg="blue")
lbl_msg.pack(pady=10)

lbl_foto = tk.Label(app, bg="#f5f5f5")
lbl_foto.pack(pady=20)

app.mainloop()
