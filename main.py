import cv2
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox


class ImageProcessor:
    def __init__(self, image_path):
        self.image = self.load_image(image_path)
        self.gray_image = self.convert_to_gray(self.image)
        self.equalized_image = self.equalize_histogram(self.gray_image)

    @staticmethod
    def load_image(path):
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"Não foi possível carregar a imagem do caminho: {path}")
        return image

    @staticmethod
    def convert_to_gray(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def equalize_histogram(gray_image):
        return cv2.equalizeHist(gray_image)

    def detect_elements(self, classifier_type):
        classifier = ClassifierLoader.load_classifier(classifier_type)
        return classifier.detectMultiScale(self.equalized_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    def draw_detected_elements(self, elements):
        for (x, y, w, h) in elements:
            cv2.rectangle(self.image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    def save_image(self):
        path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if path:
            cv2.imwrite(path, self.image)
            messagebox.showinfo("Sucesso", "Imagem salva com sucesso!")

    def display_image(self):
        rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        plt.imshow(rgb_image)
        plt.axis('off')
        plt.show()


class ClassifierLoader:
    classifiers = {
        'rosto': 'haarcascade_frontalface_alt2.xml',
        'olho': 'haarcascade_eye.xml',
        'boca': 'haarcascade_smile.xml'
    }

    @staticmethod
    def load_classifier(type):
        if type not in ClassifierLoader.classifiers:
            raise ValueError(f"Tipo desconhecido de classificador: {type}")
        return cv2.CascadeClassifier(cv2.data.haarcascades + ClassifierLoader.classifiers[type])


class GUI:
    def __init__(self, root):
        self.root = root
        self.checkboxes = []
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Detecção de Elementos")
        self.root.geometry("450x400")
        self.root.config(bg="#f5f5f5")

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.root, text="Detector de Elementos", font=("Arial", 18, "bold"), bg="#f5f5f5")
        title_label.pack(pady=10)

        instructions_label = tk.Label(self.root, text="Escolha os tipos de detecção e selecione uma imagem", font=("Arial", 12), bg="#f5f5f5")
        instructions_label.pack(pady=5)

        self.create_checkboxes()

        select_button = tk.Button(self.root, text="Selecionar Imagem", command=self.select_image,
                                  bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), relief="raised", bd=5)
        select_button.pack(pady=20)

    def create_checkboxes(self):
        for classifier in ['rosto', 'olho', 'boca']:
            var = tk.StringVar(value=classifier)
            checkbox = tk.Checkbutton(self.root, text=classifier.capitalize(), variable=var, onvalue=classifier, offvalue="")
            checkbox.pack(anchor="w")
            self.checkboxes.append(var)

    def select_image(self):
        image_path = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=[("Arquivos de Imagem", "*.jpg;*.jpeg;*.png")])
        if image_path:
            try:
                selected_types = [var.get() for var in self.checkboxes if var.get()]
                image_processor = ImageProcessor(image_path)

                for detection_type in selected_types:
                    elements = image_processor.detect_elements(detection_type)
                    image_processor.draw_detected_elements(elements)

                image_processor.display_image()

                if messagebox.askyesno("Salvar imagem", "Deseja salvar a imagem processada?"):
                    image_processor.save_image()

            except ValueError as e:
                messagebox.showerror("Erro", f"Erro: {str(e)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao processar a imagem: {str(e)}")


def run_gui():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
