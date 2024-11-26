import cv2
import os
import tkinter as tk
from tkinter import filedialog, Toplevel, messagebox
from PIL import Image, ImageTk
import pickle
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
usuarios_dir = 'usuarios'
os.makedirs(usuarios_dir, exist_ok=True)

def carregar_banco():
    return pickle.load(open('banco_usuarios.pkl', 'rb')) if os.path.exists('banco_usuarios.pkl') else {}

def salvar_banco(banco):
    pickle.dump(banco, open('banco_usuarios.pkl', 'wb'))

def atualizar_msg(msg):
    lbl_msg.config(text=msg)

def exibir_foto(foto):
    h_max, w_max = app.winfo_screenheight(), app.winfo_screenwidth()
    h_img, w_img, _ = foto.shape
    proporcao = min(w_max / w_img, h_max / h_img)
    foto_resized = cv2.resize(foto, (int(w_img * proporcao), int(h_img * proporcao)))
    foto_rgb = cv2.cvtColor(foto_resized, cv2.COLOR_BGR2RGB)
    foto_tk = ImageTk.PhotoImage(image=Image.fromarray(foto_rgb))
    lbl_foto.config(image=foto_tk)
    lbl_foto.image = foto_tk

def cadastrar_usuario(foto, bbox, id_usuario):
    x, y, w, h = bbox
    usuario = foto[y:y + h, x:x + w]
    atualizar_msg(f"Cadastrar usuário {id_usuario}")
    frm_cadastro.pack(pady=20)

    def confirmar_cadastro():
        banco = carregar_banco()
        dados_usuario = {"nome": ent_nome.get(), "email": ent_email.get(), "telefone": ent_telefone.get()}
        caminho_foto = os.path.join(usuarios_dir, f'{id_usuario}.jpg')
        cv2.imwrite(caminho_foto, usuario)
        banco[id_usuario] = {"foto": caminho_foto, "dados": dados_usuario}
        salvar_banco(banco)
        atualizar_msg(f"Usuário {id_usuario} cadastrado com sucesso.")
        frm_cadastro.pack_forget()
        exibir_foto(foto)

    btn_confirmar.config(command=confirmar_cadastro)

def processar_foto(foto):
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        resultado = face_detection.process(cv2.cvtColor(foto, cv2.COLOR_BGR2RGB))
        if not resultado.detections:
            atualizar_msg("Nenhum rosto detectado.")
            return
        banco = carregar_banco()
        for idx, deteccao in enumerate(resultado.detections):
            bboxC = deteccao.location_data.relative_bounding_box
            h, w, _ = foto.shape
            bbox = (int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h))
            id_usuario = f'usuario_{idx}'
            if id_usuario not in banco:
                cadastrar_usuario(foto, bbox, id_usuario)
                return
        atualizar_msg("O usuário já está cadastrado.")

def escolher_foto():
    caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg;*.jpeg;*.png")])
    if caminho:
        foto = cv2.imread(caminho)
        if foto is not None:
            processar_foto(foto)
        else:
            atualizar_msg("Não foi possível carregar a foto.")

def capturar_foto_com_webcam():
    captura = cv2.VideoCapture(0)
    if not captura.isOpened():
        atualizar_msg("Não foi possível acessar a câmera.")
        return
    atualizar_msg("Pressione 'Espaço' para capturar ou 'Esc' para sair.")
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

app = tk.Tk()
app.title("Detector de Usuários")
app.state('zoomed')
app.config(bg="#f5f5f5")

tk.Label(app, text="Detector de Usuários", font=("Arial", 18, "bold"), bg="#f5f5f5").pack(pady=10)
tk.Button(app, text="Escolher Foto", command=escolher_foto, bg="#4CAF50", fg="white", font=("Arial", 14, "bold")).pack(pady=20)
tk.Button(app, text="Abrir Câmera", command=capturar_foto_com_webcam, bg="#FFC107", fg="black", font=("Arial", 14, "bold")).pack(pady=20)
lbl_msg = tk.Label(app, text="", font=("Arial", 12), bg="#f5f5f5", fg="blue")
lbl_msg.pack(pady=10)
lbl_foto = tk.Label(app, bg="#f5f5f5")
lbl_foto.pack(pady=20)

frm_cadastro = tk.Frame(app, bg="#f5f5f5")
ent_nome, ent_email, ent_telefone = (tk.Entry(frm_cadastro, font=("Arial", 12)) for _ in range(3))
for idx, (texto, entrada) in enumerate(zip(["Nome", "E-mail", "Telefone"], [ent_nome, ent_email, ent_telefone])):
    tk.Label(frm_cadastro, text=texto, font=("Arial", 12), bg="#f5f5f5").grid(row=idx, column=0, padx=10, pady=5)
    entrada.grid(row=idx, column=1, padx=10, pady=5)
btn_confirmar = tk.Button(frm_cadastro, text="Confirmar Cadastro", font=("Arial", 12), bg="#4CAF50", fg="white")
btn_confirmar.grid(row=3, column=0, columnspan=2, pady=10)

app.mainloop()
