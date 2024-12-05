import cv2
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pickle
import mediapipe as mp

# Inicializando as variáveis do MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
usuarios_dir = 'usuarios'
os.makedirs(usuarios_dir, exist_ok=True)

# Funções auxiliares de banco de dados
def carregar_banco():
    """Carrega o banco de dados de usuários, retornando um dicionário vazio se não encontrar o arquivo."""
    try:
        with open('banco_usuarios.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

def salvar_banco(banco):
    """Salva o banco de dados em um arquivo binário."""
    with open('banco_usuarios.pkl', 'wb') as f:
        pickle.dump(banco, f)

# Funções de interface
def atualizar_msg(msg):
    """Atualiza a mensagem exibida na interface."""
    lbl_msg.config(text=msg)

def exibir_foto(foto):
    """Exibe a foto no formato correto dentro da interface."""
    altura_max, largura_max = 400, 400
    altura, largura = foto.shape[:2]
    proporcao = min(largura_max / largura, altura_max / altura)
    nova_largura, nova_altura = int(largura * proporcao), int(altura * proporcao)
    foto_rgb = cv2.cvtColor(cv2.resize(foto, (nova_largura, nova_altura)), cv2.COLOR_BGR2RGB)
    foto_tk = ImageTk.PhotoImage(image=Image.fromarray(foto_rgb))
    lbl_foto.config(image=foto_tk)
    lbl_foto.image = foto_tk

def exibir_formulario(nome_usuario):
    """Exibe o formulário de cadastro de usuário."""
    frm_cadastro.pack(pady=20)
    lbl_nome.config(text=f"Nome (Usuário: {nome_usuario})")
    ent_nome.delete(0, tk.END)
    ent_email.delete(0, tk.END)
    ent_telefone.delete(0, tk.END)

def esconder_formulario():
    """Esconde o formulário de cadastro."""
    frm_cadastro.pack_forget()

# Função para cadastrar um novo usuário
def cadastrar_usuario(foto, deteccao, idx):
    """Realiza o cadastro de um novo usuário detectado na foto."""
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

    # Função interna para concluir o cadastro
    def completar_cadastro():
        dados_usuario = {
            "nome": ent_nome.get(),
            "email": ent_email.get(),
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

# Função para preencher os campos do formulário com dados de um usuário
def preencher_campos_usuario(dados):
    """Preenche os campos de nome, email e telefone com os dados existentes de um usuário."""
    ent_nome.insert(0, dados["nome"])
    ent_email.insert(0, dados["email"])
    ent_telefone.insert(0, dados["telefone"])
    frm_cadastro.pack(pady=20)

# Função para processar a foto e realizar a detecção de rostos
def processar_foto(foto):
    """Processa a foto para detectar rostos e cadastrar os usuários detectados."""
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

# Função para escolher uma foto do sistema de arquivos
def escolher_foto():
    """Permite ao usuário escolher uma foto do sistema de arquivos para processar."""
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

# Função para capturar foto via webcam
def capturar_foto_com_webcam():
    """Captura uma foto da webcam e a processa."""
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
        atualizar_msg(f"Erro ao acessar a câmera: {str(e)}")

# Funções para editar, excluir e exibir usuários cadastrados
def editar_usuario(id_usuario):
    """Permite editar os dados de um usuário cadastrado."""
    banco = carregar_banco()
    if id_usuario in banco:
        info = banco[id_usuario]
        exibir_formulario(id_usuario)
        preencher_campos_usuario(info["dados"])

        # Função interna para salvar a edição
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
    """Exclui um usuário do banco de dados."""
    banco = carregar_banco()
    if id_usuario in banco:
        del banco[id_usuario]
        salvar_banco(banco)
        atualizar_msg(f"Usuário {id_usuario} excluído com sucesso.")
    else:
        atualizar_msg(f"Usuário {id_usuario} não encontrado.")

def exibir_usuarios():
    """Exibe uma lista de todos os usuários cadastrados em uma nova janela."""
    banco = carregar_banco()
    if not banco:
        atualizar_msg("Nenhum usuário cadastrado.")
        return

    janela_usuarios = tk.Toplevel(app)
    janela_usuarios.title("Usuários Cadastrados")
    janela_usuarios.geometry("500x400")
    janela_usuarios.config(bg="#f5f5f5")

    lbl_titulo = tk.Label(janela_usuarios, text="Usuários Cadastrados", font=("Arial", 14, "bold"), bg="#f5f5f5")
    lbl_titulo.pack(pady=10)

    frm_usuarios = tk.Frame(janela_usuarios, bg="#f5f5f5")
    frm_usuarios.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for id_usuario, info in banco.items():
        nome = info["dados"].get("nome", "N/A")
        email = info["dados"].get("email", "N/A")
        telefone = info["dados"].get("telefone", "N/A")
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

# Função principal da interface
app = tk.Tk()
app.title("Detector de Usuários")
app.geometry("450x700")
app.config(bg="#f5f5f5")

# Layout principal da interface
lbl_titulo = tk.Label(app, text="Detector de Usuários", font=("Arial", 18, "bold"), bg="#f5f5f5")
lbl_titulo.pack(pady=10)

lbl_instr = tk.Label(app, text="Escolha uma foto ou use a câmera", font=("Arial", 12), bg="#f5f5f5")
lbl_instr.pack(pady=5)

btn_escolher = tk.Button(app, text="Escolher Foto", command=escolher_foto, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), relief="raised", bd=5)
btn_escolher.pack(pady=20)

btn_capturar_ip = tk.Button(app, text="Abrir Câmera", command=capturar_foto_com_webcam, bg="#FFC107", fg="black", font=("Arial", 14, "bold"), relief="raised", bd=5)
btn_capturar_ip.pack(pady=20)

btn_exibir_usuarios = tk.Button(app, text="Exibir Usuários Cadastrados", command=exibir_usuarios, bg="#2196F3", fg="white", font=("Arial", 14, "bold"), relief="raised", bd=5)
btn_exibir_usuarios.pack(pady=20)

lbl_msg = tk.Label(app, text="", font=("Arial", 12), bg="#f5f5f5", fg="blue")
lbl_msg.pack(pady=10)

lbl_foto = tk.Label(app, bg="#f5f5f5")
lbl_foto.pack(pady=20)

# Formulário de cadastro de usuário
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
