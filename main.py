import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pickle
import mediapipe as mp
import csv
import re

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
usuarios_dir = 'usuarios'
os.makedirs(usuarios_dir, exist_ok=True)

def carregar_banco():
    try:
        with open('banco_usuarios.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

def salvar_banco(banco):
    try:
        with open('banco_usuarios.pkl', 'wb') as f:
            pickle.dump(banco, f)
    except Exception as e:
        atualizar_msg(f"Erro ao salvar banco de dados: {e}")

def atualizar_msg(msg):
    lbl_msg.config(text=msg)

def exibir_foto(foto):
    altura_max, largura_max = 400, 400
    altura, largura = foto.shape[:2]
    proporcao = min(largura_max / largura, altura_max / altura)
    nova_largura, nova_altura = int(largura * proporcao), int(altura * proporcao)
    foto_rgb = cv2.cvtColor(cv2.resize(foto, (nova_largura, nova_altura)), cv2.COLOR_BGR2RGB)
    foto_tk = ImageTk.PhotoImage(image=Image.fromarray(foto_rgb))
    lbl_foto.config(image=foto_tk)
    lbl_foto.image = foto_tk

def exibir_formulario(nome_usuario):
    frm_cadastro.pack(pady=20)
    lbl_nome.config(text=f"Nome (Usuário: {nome_usuario})")
    ent_nome.delete(0, tk.END)
    ent_email.delete(0, tk.END)
    ent_telefone.delete(0, tk.END)

def esconder_formulario():
    frm_cadastro.pack_forget()

def verificar_email_unico(email):
    banco = carregar_banco()
    for usuario in banco.values():
        if usuario["dados"].get("email") == email:
            return False
    return True

def verificar_email_valido(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

def verificar_campos_validos():
    nome = ent_nome.get().strip()
    email = ent_email.get().strip()
    telefone = ent_telefone.get().strip()
    if not nome or not email or not telefone:
        atualizar_msg("Todos os campos devem ser preenchidos.")
        return False
    if not verificar_email_valido(email):
        atualizar_msg("E-mail inválido.")
        return False
    return True

def cadastrar_usuario(foto, deteccao, idx):
    bboxC = deteccao.location_data.relative_bounding_box
    h, w, _ = foto.shape
    x, y, w_box, h_box = int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h)
    usuario = foto[y:y + h_box, x:x + w_box]
    id_usuario = f'usuario_{idx}'

    banco = carregar_banco()
    if id_usuario in banco:
        dados = banco[id_usuario]["dados"]
        atualizar_msg(f"Usuário {id_usuario} já cadastrado.")
        exibir_foto(foto)
        preencher_campos_usuario(dados)
        return

    atualizar_msg(f"Cadastro do usuário {id_usuario}")
    exibir_formulario(id_usuario)

    def completar_cadastro():
        if not verificar_campos_validos():
            return

        email = ent_email.get()
        if not verificar_email_unico(email):
            atualizar_msg("E-mail já cadastrado.")
            return

        dados_usuario = {
            "nome": ent_nome.get(),
            "email": email,
            "telefone": ent_telefone.get()
        }
        caminho_foto = os.path.join(usuarios_dir, f'{id_usuario}.jpg')
        cv2.imwrite(caminho_foto, usuario)
        banco[id_usuario] = {"foto": caminho_foto, "dados": dados_usuario}
        salvar_banco(banco)
        atualizar_msg(f"Usuário {id_usuario} cadastrado com sucesso.")
        esconder_formulario()
        exibir_foto(foto)

    btn_confirmar.config(command=completar_cadastro)

def preencher_campos_usuario(dados):
    ent_nome.insert(0, dados["nome"])
    ent_email.insert(0, dados["email"])
    ent_telefone.insert(0, dados["telefone"])
    frm_cadastro.pack(pady=20)

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

def editar_usuario(id_usuario):
    banco = carregar_banco()
    if id_usuario in banco:
        info = banco[id_usuario]
        exibir_formulario(id_usuario)
        preencher_campos_usuario(info["dados"])

        def salvar_edicao():
            banco[id_usuario]["dados"] = {
                "nome": ent_nome.get(),
                "email": ent_email.get(),
                "telefone": ent_telefone.get()
            }
            salvar_banco(banco)
            atualizar_msg(f"Usuário {id_usuario} atualizado com sucesso.")
            esconder_formulario()

        btn_confirmar.config(command=salvar_edicao)
    else:
        atualizar_msg(f"Usuário {id_usuario} não encontrado.")

def excluir_usuario(id_usuario):
    resposta = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o usuário {id_usuario}?")
    if resposta:
        banco = carregar_banco()
        if id_usuario in banco:
            caminho_foto = banco[id_usuario]["foto"]
            if os.path.exists(caminho_foto):
                os.remove(caminho_foto)
            del banco[id_usuario]
            salvar_banco(banco)
            atualizar_msg(f"Usuário {id_usuario} excluído com sucesso.")
        else:
            atualizar_msg(f"Usuário {id_usuario} não encontrado.")

def exportar_usuarios_csv():
    banco = carregar_banco()
    if not banco:
        atualizar_msg("Nenhum usuário cadastrado para exportar.")
        return
    caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not caminho:
        return
    try:
        with open(caminho, mode='w', newline='', encoding='utf-8') as arquivo_csv:
            escritor = csv.writer(arquivo_csv)
            escritor.writerow(["ID do Usuário", "Nome", "E-mail", "Telefone"])
            for id_usuario, info in banco.items():
                dados = info["dados"]
                escritor.writerow([id_usuario, dados.get("nome", "N/A"), dados.get("email", "N/A"), dados.get("telefone", "N/A")])
        atualizar_msg(f"Usuários exportados com sucesso para {caminho}.")
        resposta = messagebox.askyesno("Abrir Arquivo", "Deseja abrir o arquivo CSV exportado?")
        if resposta:
            os.startfile(caminho)
    except Exception as e:
        atualizar_msg(f"Erro ao exportar usuários: {str(e)}")

def exibir_usuarios(pesquisa=""):
    banco = carregar_banco()
    if not banco:
        atualizar_msg("Nenhum usuário cadastrado.")
        return
    janela_usuarios = tk.Toplevel(app)
    janela_usuarios.title("Usuários Cadastrados")
    janela_usuarios.geometry("600x400")
    janela_usuarios.config(bg="#f5f5f5")
    
    lbl_titulo = tk.Label(janela_usuarios, text="Usuários Cadastrados", font=("Arial", 14, "bold"), bg="#f5f5f5")
    lbl_titulo.pack(pady=10)
    
    frm_usuarios = tk.Frame(janela_usuarios, bg="#f5f5f5")
    frm_usuarios.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for id_usuario, info in banco.items():
        nome = info["dados"].get("nome", "N/A")
        email = info["dados"].get("email", "N/A")
        telefone = info["dados"].get("telefone", "N/A")
        if pesquisa.lower() in nome.lower() or pesquisa.lower() in email.lower() or pesquisa.lower() in telefone.lower():
            texto_usuario = f"{id_usuario}: {nome} | {email} | {telefone}"
            frm_usuario = tk.Frame(frm_usuarios, bg="#e0e0e0", padx=5, pady=5)
            frm_usuario.pack(fill=tk.X, pady=5)
            lbl_usuario = tk.Label(frm_usuario, text=texto_usuario, font=("Arial", 12), bg="#e0e0e0", anchor="w")
            lbl_usuario.pack(side=tk.LEFT, fill=tk.X, expand=True)
            btn_editar = tk.Button(frm_usuario, text="Editar", font=("Arial", 10), bg="#FFC107", fg="black", 
                                   command=lambda u=id_usuario: editar_usuario(u))
            btn_editar.pack(side=tk.RIGHT, padx=5)
            btn_excluir = tk.Button(frm_usuario, text="Excluir", font=("Arial", 10), bg="#F44336", fg="white", 
                                    command=lambda u=id_usuario: excluir_usuario(u))
            btn_excluir.pack(side=tk.RIGHT, padx=5)

    def buscar_usuarios():
        pesquisa = ent_pesquisa.get().strip()
        exibir_usuarios(pesquisa)

    ent_pesquisa = tk.Entry(janela_usuarios, font=("Arial", 12))
    ent_pesquisa.pack(pady=10)
    btn_pesquisar = tk.Button(janela_usuarios, text="Pesquisar", command=buscar_usuarios, font=("Arial", 12))
    btn_pesquisar.pack()

app = tk.Tk()
app.title("Detector de Usuários")
app.geometry("450x750")
app.config(bg="#f5f5f5")

lbl_titulo = tk.Label(app, text="Detector de Usuários", font=("Arial", 18, "bold"), bg="#f5f5f5")
lbl_titulo.pack(pady=10)

lbl_instr = tk.Label(app, text="Escolha uma foto ou use a câmera", font=("Arial", 12), bg="#f5f5f5")
lbl_instr.pack(pady=5)

btn_escolher = tk.Button(app, text="Escolher Foto", command=escolher_foto, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=5, width=25)
btn_escolher.pack(pady=10)

btn_capturar_ip = tk.Button(app, text="Abrir Câmera", command=capturar_foto_com_webcam, bg="#FFC107", fg="black", font=("Arial", 12, "bold"), relief="raised", bd=5, width=25)
btn_capturar_ip.pack(pady=10)

btn_exibir_usuarios = tk.Button(app, text="Exibir Usuários Cadastrados", command=lambda: exibir_usuarios(), bg="#2196F3", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=5, width=25)
btn_exibir_usuarios.pack(pady=10)

btn_exportar_csv = tk.Button(app, text="Exportar Usuários (CSV)", command=exportar_usuarios_csv, bg="#FF9800", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=5, width=25)
btn_exportar_csv.pack(pady=10)

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
