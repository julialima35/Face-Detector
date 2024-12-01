import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox
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
    h_max, w_max = app.winfo_height(), app.winfo_width()
    h_img, w_img, _ = foto.shape
    proporcao = min(w_max / w_img, h_max / h_img)
    foto_resized = cv2.resize(foto, (int(w_img * proporcao), int(h_img * proporcao)))
    foto_rgb = cv2.cvtColor(foto_resized, cv2.COLOR_BGR2RGB)
    foto_tk = ImageTk.PhotoImage(image=Image.fromarray(foto_rgb))
    lbl_foto.config(image=foto_tk)
    lbl_foto.image = foto_tk


def cadastrar_usuario(foto, bbox):
    x, y, w, h = bbox
    x, y, w, h = max(x, 0), max(y, 0), min(w, foto.shape[1] - x), min(h, foto.shape[0] - y)
    rosto = foto[y:y + h, x:x + w]
    banco = carregar_banco()
    id_usuario = f'usuario_{len(banco) + 1}'
    caminho_foto = os.path.join(usuarios_dir, f'{id_usuario}.jpg')
    cv2.imwrite(caminho_foto, rosto)
    banco[id_usuario] = {"nome": "Desconhecido", "foto": caminho_foto}
    salvar_banco(banco)
    atualizar_msg(f"Usuário {id_usuario} cadastrado.")
    exibir_foto(rosto)


def processar_foto(foto):
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        resultado = face_detection.process(cv2.cvtColor(foto, cv2.COLOR_BGR2RGB))
        if not resultado.detections:
            atualizar_msg("Nenhum rosto detectado.")
            return
        for deteccao in resultado.detections:
            bboxC = deteccao.location_data.relative_bounding_box
            h, w, _ = foto.shape
            bbox = (int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h))
            cadastrar_usuario(foto, bbox)


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

app.mainloop()
