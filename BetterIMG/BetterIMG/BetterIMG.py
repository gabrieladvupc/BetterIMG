import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
from filtros_calculados import aplicar_filtro_media, aplicar_filtro_mediana, aplicar_filtro_laplaciano, aplicar_filtro_sobel

class Filtroimg:
    def __init__(self, root):
        self.root = root
        self.root.title("Betterimg")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        self.imagen_original = None
        self.imagen_actual = None
        self.image_path = None 

        self.filtro_seleccionado = tk.StringVar()
        self.mascara_media = tk.IntVar(value=1)
        self.mascara_laplaciano = tk.IntVar(value=1)

        self.crear_widgets()
        
    def crear_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.crear_pagina_inicio()
        self.crear_pagina_funcionamiento()
        self.crear_pagina_filtros()
        self.crear_pagina_integrantes()


    def crear_pagina_inicio(self):
        marco_portada = tk.Frame(self.notebook, bg="#7FFFD4")  # verde agua
        self.notebook.add(marco_portada, text="Portada")

        etiqueta_titulo = tk.Label(marco_portada, text="BETTERIMG",
                                   font=("Cal Sans", 48, "bold"),
                                   fg="white", bg="#7FFFD4")
        etiqueta_titulo.pack(pady=50)

        etiqueta_subtitulo = tk.Label(marco_portada, text="App para filtrado de imágenes",
                                      font=("Cal Sans", 30),
                                      fg="white", bg="#7FFFD4")
        etiqueta_subtitulo.pack(pady=10)

        boton1 = tk.Button(marco_portada, text="Funcionamiento",
                           command=lambda: self.notebook.select(1),
                           fg="white", bg="#5AC8B3")
        boton1.pack(pady=10)

        boton2 = tk.Button(marco_portada, text="Filtros",
                           command=lambda: self.notebook.select(2),
                           fg="white", bg="#5AC8B3")
        boton2.pack(pady=10)

        boton3 = tk.Button(marco_portada, text="Integrantes",
                           command=lambda: self.notebook.select(3),
                           fg="white", bg="#5AC8B3")
        boton3.pack(pady=10)
    
    def crear_pagina_funcionamiento(self):
        marco_conceptos = ttk.Frame(self.notebook)
        self.notebook.add(marco_conceptos, text="Funcionamiento")

        widget_texto = tk.Text(marco_conceptos, wrap=tk.WORD, font=("Arial", 11))
        widget_texto.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        widget_texto.insert(tk.END, "\nBetterIMG: Mejora de imágenes clínicas\n", "titulo")
        widget_texto.insert(tk.END, "\nBetterIMG es una aplicación cuyo objetivo es ayudar a mejorar la calidad de imágenes médicas mediante filtros de suavizado y agudizamiento, facilitando así el diagnóstico y análisis clínico.\n")

        # Subtítulos y descripciones
        filtros = {
            "Filtro de Mediana": " Cuando trabajas con radiografías óseas, el filtro de Mediana de BetterIMG elimina eficazmente el ruido tipo 'sal y pimienta' que aparece durante la captura. Al utilizar este filtro, notarás cómo se preservan los bordes de los huesos de las fracturas, proporcionando una imagen más limpia y nitida para el diagnóstico.",
            "Filtro de Media": "Para imágenes de resonancia magnética cerebral donde hay dificultad en la visualización de estructuras cerebrales complejas, el filtro de media que ofrece BetterIMG, permite que imágenes como de los ventrículos cerebrales y otros tejidos blandos se aprecien con mayor facilidad.",
            "Filtro Laplaciano": "Resalta bordes abruptos y estructuras con cambios bruscos de intensidad. Muy útil en tomografías para detectar bordes de órganos o estructuras internas.",
            "Filtro Sobel": "Detecta bordes en dirección horizontal y vertical. En imágenes médicas permite identificar contornos de tejidos o anomalías estructurales en ecografías o tomografías."
        }

        for titulo, descripcion in filtros.items():
            widget_texto.insert(tk.END, f"\n{titulo}\n", "subtitulo")
            widget_texto.insert(tk.END, f"{descripcion}\n")

        pasos = [
            "Carga tu imagen - Presiona 'Cargar imagen' y selecciona una imagen médica (JPG, JPEG, PNG).",
            "Selecciona el filtro a aplicar desde el menú desplegable.",
            "Si es necesario, selecciona la máscara correspondiente.",
            "Presiona 'Aplicar Filtro' para procesar la imagen.",
            "Puedes comparar los resultados con la imagen original y guardar la imagen filtrada."
        ]

        widget_texto.insert(tk.END, "\nPasos de uso:\n", "titulo")
        for i, paso in enumerate(pasos, 1):
            widget_texto.insert(tk.END, f"{i}. {paso}\n")

        widget_texto.tag_config("titulo", font=("Arial", 13, "bold"))
        widget_texto.tag_config("subtitulo", font=("Arial", 12, "bold"))
        widget_texto.config(state=tk.DISABLED)
    
    def crear_pagina_filtros(self):
        marco_suavizado = ttk.Frame(self.notebook)
        self.notebook.add(marco_suavizado, text="Filtros")

        # Crear canvas y scrollbar
        canvas = tk.Canvas(marco_suavizado)
        scrollbar = ttk.Scrollbar(marco_suavizado, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Empaquetar correctamente
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame interno dentro del canvas
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Ajustar el ancho dinámicamente al contenedor padre
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Forzar que el frame interno use todo el ancho disponible
        def resize_canvas(event):
            canvas.itemconfig(canvas_frame, width=event.width)

        canvas.bind("<Configure>", resize_canvas)

        # CONTENIDO DENTRO DEL SCROLLABLE FRAME (igual que antes)
        marco_control = ttk.LabelFrame(scrollable_frame, text="Controles")
        marco_control.pack(fill=tk.X, padx=10, pady=10)

        boton_cargar = ttk.Button(marco_control, text="Cargar Imagen", command=self.cargar_imagen)
        boton_cargar.pack(side=tk.LEFT, padx=5, pady=10)

        filtro_frame = ttk.Frame(scrollable_frame)
        filtro_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(filtro_frame, text="Selecciona un filtro:").pack(side=tk.LEFT, padx=5)
        opciones_filtro = ["Mediana", "Media", "Laplaciano", "Sobel"]
        combo_filtro = ttk.Combobox(filtro_frame, textvariable=self.filtro_seleccionado, values=opciones_filtro, state="readonly")
        combo_filtro.pack(side=tk.LEFT, padx=5)
        combo_filtro.bind("<<ComboboxSelected>>", self.mostrar_opciones_filtro)

        self.opciones_filtro_frame = ttk.Frame(scrollable_frame)
        self.opciones_filtro_frame.pack(fill=tk.X, padx=20, pady=10)

        self.imagen_mascara_label = ttk.Label(scrollable_frame)
        self.imagen_mascara_label.pack(pady=5)

        self.boton_aplicar = ttk.Button(scrollable_frame, text="Aplicar Filtro", command=self.aplicar_filtro)
        self.boton_aplicar.pack(pady=5)

        self.etiqueta_estado = ttk.Label(scrollable_frame, text="Seleccionar imagen:")
        self.etiqueta_estado.pack(padx=10, anchor=tk.E)

        self.marco_imagenes = ttk.Frame(scrollable_frame)
        self.marco_imagenes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.marco_original = ttk.LabelFrame(self.marco_imagenes, text="Imagen Original")
        self.marco_original.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.marco_filtrada = ttk.LabelFrame(self.marco_imagenes, text="Imagen Filtrada")
        self.marco_filtrada.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.label_imagen_original = ttk.Label(self.marco_original)
        self.label_imagen_original.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.label_imagen_filtrada = ttk.Label(self.marco_filtrada)
        self.label_imagen_filtrada.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        marco_botones = ttk.Frame(scrollable_frame)
        marco_botones.pack(pady=10)

        btn_restaurar = tk.Button(marco_botones, text="Restaurar Imagen", command=self.restaurar_imagen, bg="#e0e0e0", font=("Arial", 10, "bold"))
        btn_restaurar.grid(row=0, column=0, padx=10)

        btn_guardar = tk.Button(marco_botones, text="Guardar Imagen", command=self.guardar_imagen, bg="#a8d5ba", font=("Arial", 10, "bold"))
        btn_guardar.grid(row=0, column=1, padx=10)

    def mostrar_opciones_filtro(self, event):
        for widget in self.opciones_filtro_frame.winfo_children():
            widget.destroy()

        filtro = self.filtro_seleccionado.get()
        imagen_path = None

        if filtro == "Media":
            ttk.Label(self.opciones_filtro_frame, text="Selecciona máscara de media:").pack(side=tk.LEFT, padx=5)
            ttk.Combobox(self.opciones_filtro_frame, textvariable=self.mascara_media, values=[1, 2], width=5).pack(side=tk.LEFT, padx=5)
            imagen_path = "mascaras/media.png"

        elif filtro == "Laplaciano":
            ttk.Label(self.opciones_filtro_frame, text="Selecciona máscara de Laplaciano:").pack(side=tk.LEFT, padx=5)
            ttk.Combobox(self.opciones_filtro_frame, textvariable=self.mascara_laplaciano, values=[1, 2, 3, 4], width=5).pack(side=tk.LEFT, padx=5)
            imagen_path = "mascaras/laplaciano.png"

        elif filtro == "Sobel":
            imagen_path = "mascaras/sobel.png"

        if imagen_path:
            img = Image.open(imagen_path)
            img.thumbnail((400, 400))
            img_tk = ImageTk.PhotoImage(img)
            self.imagen_mascara_label.config(image=img_tk)
            self.imagen_mascara_label.image = img_tk
        else:
            self.imagen_mascara_label.config(image='')
            self.imagen_mascara_label.image = None

    def crear_pagina_integrantes(self):
        marco_integrantes = ttk.Frame(self.notebook)
        self.notebook.add(marco_integrantes, text="Integrantes")
        
        etiqueta_titulo = ttk.Label(marco_integrantes, text="INTEGRANTES:", 
                               font=("Cal sans", 16, "bold"))
        etiqueta_titulo.pack(pady=20)
        
        integrantes = [
            "Durand Valente, Gabriela Andrea - U202311957",
            "Gamboa Avendaño, Diego Anderson - U202120374",
            "Medina Vilca, Magaly Yefrith - U202514300",
            "Palacios Valentin, Sebastian Wilfredo Yosue - U20231B463",
            "Soto Villar, Diego Fabrizio Fernando - U202217023",
        ]
        
        for i, integrante in enumerate(integrantes):
            ttk.Label(marco_integrantes, text=f"{i+1}. {integrante}", 
                     font=("Arial", 12)).pack(pady=10)
    
    def cargar_imagen(self):
        ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp")])
        if ruta_archivo:
            self.imagen_original = cv2.imread(ruta_archivo)
            if self.imagen_original is None:
                return
            self.imagen_original = cv2.cvtColor(self.imagen_original, cv2.COLOR_BGR2RGB)
            self.imagen_actual = self.imagen_original.copy()
            self.mostrar_en_gui(self.imagen_original, self.label_imagen_original)
            self.etiqueta_estado.config(text=f"Imagen subida: {ruta_archivo.split('/')[-1]}")

    def mostrar_en_gui(self, imagen, label):
        if imagen is None:
            return

        # Esperar a que se actualice el tamaño del widget
        self.root.update_idletasks()

        ancho_label = label.winfo_width()
        alto_label = label.winfo_height()

        # Forzar tamaño mínimo si aún no se ha renderizado
        if ancho_label < 100 or alto_label < 100:
            ancho_label = 500
            alto_label = 400

        alto_img, ancho_img = imagen.shape[:2]
        ratio = min(ancho_label / ancho_img, alto_label / alto_img)

        nuevo_ancho = max(1, int(ancho_img * ratio))
        nuevo_alto = max(1, int(alto_img * ratio))

        imagen_redim = cv2.resize(imagen, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)

        img_pil = Image.fromarray(imagen_redim)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        label.image = img_tk
        label.config(image=img_tk)

    def aplicar_filtro(self):
        if self.imagen_original is None:
            return
        imagen_pil = Image.fromarray(self.imagen_original)
        filtro = self.filtro_seleccionado.get()
        if filtro == "Mediana":
            resultado = aplicar_filtro_mediana(imagen_pil, imagen_pil.width, imagen_pil.height)
            self.etiqueta_estado.config(text="Filtro de mediana aplicado")
        elif filtro == "Media":
            resultado = aplicar_filtro_media(imagen_pil, imagen_pil.width, imagen_pil.height, mascara=self.mascara_media.get())
            self.etiqueta_estado.config(text="Filtro de media aplicado")
        elif filtro == "Laplaciano":
            resultado = aplicar_filtro_laplaciano(imagen_pil, imagen_pil.width, imagen_pil.height, mascara=self.mascara_laplaciano.get())
            self.etiqueta_estado.config(text="Filtro Laplaciano aplicado")
        elif filtro == "Sobel":
            resultado = aplicar_filtro_sobel(imagen_pil, imagen_pil.width, imagen_pil.height)
            self.etiqueta_estado.config(text="Filtro Sobel aplicado")
        else:
            return
        self.imagen_actual = np.array(resultado)
        self.mostrar_en_gui(self.imagen_actual, self.label_imagen_filtrada)

    def restaurar_imagen(self):
        if self.imagen_original is not None:
            self.imagen_actual = self.imagen_original.copy()
            self.mostrar_en_gui(self.imagen_actual, self.label_imagen_filtrada)
            self.etiqueta_estado.config(text="La imagen fue restaurada")

    def guardar_imagen(self):
        if self.imagen_actual is not None:
            ruta_guardado = filedialog.asksaveasfilename(defaultextension=".jpg",
                filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp")])
            if ruta_guardado:
                imagen_bgr = cv2.cvtColor(self.imagen_actual, cv2.COLOR_RGB2BGR)
                cv2.imwrite(ruta_guardado, imagen_bgr)
                self.etiqueta_estado.config(text=f"Imagen guardada como: {ruta_guardado.split('/')[-1]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Filtroimg(root)
    root.mainloop()