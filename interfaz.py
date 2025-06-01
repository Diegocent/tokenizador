import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from tokenizador import Tokenizador

class InterfazTokenizador:
    """
    PARTE DEL TP: Interfaz gráfica opcional para facilitar la interacción con el sistema
    Proporciona una interfaz amigable para cargar conversaciones y ver resultados
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Tokenizador para Contact Centers")
        
        # Centrar la ventana principal
        self.centrar_ventana(900, 700)
        
        # PARTE DEL TP: Inicialización del sistema principal
        # Crear instancia del tokenizador que implementa toda la funcionalidad del TP
        self.tokenizador = Tokenizador()
        
        # Crear interfaz
        self.crear_interfaz()
    
    def centrar_ventana(self, ancho, alto):
        """Centra la ventana principal en la pantalla"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (ancho // 2)
        y = (screen_height // 2) - (alto // 2)
        
        self.root.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def crear_interfaz(self):
        """
        PARTE DEL TP: Interfaz para entrada de datos
        Crea la interfaz gráfica para cargar conversaciones (simula la entrada de audio a texto)
        """
        # Frame principal
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(main_frame, text="Tokenizador para Análisis de Interacciones en Contact Centers", 
                         font=("Arial", 14, "bold"))
        titulo.pack(pady=10)
        
        # PARTE DEL TP: 1.1 Entrada de datos (simula conversión audio a texto)
        # Frame para entrada de texto que simula las transcripciones
        input_frame = tk.LabelFrame(main_frame, text="Conversación", padx=5, pady=5)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Área de texto para la conversación
        self.texto_conversacion = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=10)
        self.texto_conversacion.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botones para cargar y procesar
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # PARTE DEL TP: Funcionalidades de carga de datos
        btn_cargar = tk.Button(btn_frame, text="Cargar conversación", command=self.cargar_conversacion)
        btn_cargar.pack(side=tk.LEFT, padx=5)
        
        btn_ejemplo = tk.Button(btn_frame, text="Cargar ejemplo", command=self.cargar_ejemplo)
        btn_ejemplo.pack(side=tk.LEFT, padx=5)
        
        # PARTE DEL TP: Botón principal que ejecuta todo el procesamiento
        btn_procesar = tk.Button(btn_frame, text="Procesar conversación", command=self.procesar_conversacion)
        btn_procesar.pack(side=tk.LEFT, padx=5)
        
        btn_limpiar = tk.Button(btn_frame, text="Limpiar", command=self.limpiar)
        btn_limpiar.pack(side=tk.LEFT, padx=5)
        
        # PARTE DEL TP: 3. Resultados y Reporte
        # Frame para mostrar los resultados del análisis
        result_frame = tk.LabelFrame(main_frame, text="Resultados", padx=5, pady=5)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Área de texto para los resultados
        self.texto_resultados = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=15)
        self.texto_resultados.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def cargar_conversacion(self):
        """
        PARTE DEL TP: 1.1 Entrada de datos
        Permite cargar conversaciones desde archivos (simula la conversión de audio a texto)
        """
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de conversación",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if archivo:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                self.texto_conversacion.delete(1.0, tk.END)
                self.texto_conversacion.insert(tk.END, contenido)
                messagebox.showinfo("Éxito", "Conversación cargada correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")
    
    def cargar_ejemplo(self):
        """
        PARTE DEL TP: Ejemplo de conversación para demostrar funcionalidad
        Carga una conversación de ejemplo que demuestra todos los aspectos del TP
        """
        ejemplo = """Agente: Hola, bienvenido al servicio de Atención al Cliente. ¿Con quién tengo el gusto de hablar?
Cliente: Buenas, mi nombre es Juan Arias, quiero hacer una consulta acerca de mi factura.
Agente: Claro Juan, cuénteme en qué puedo ayudarle con su factura.
Cliente: Recibí un cobro por un servicio que nunca contraté, estoy muy molesto por esto.
Agente: Entiendo su frustración, vamos a revisar ese cargo y solucionarlo de inmediato.
Cliente: Gracias, espero que puedan resolverlo pronto.
Agente: No se preocupe, ya estoy gestionando la eliminación del cargo. En unos minutos estará resuelto."""
        
        self.texto_conversacion.delete(1.0, tk.END)
        self.texto_conversacion.insert(tk.END, ejemplo)

    def procesar_conversacion(self):
        """
        PARTE DEL TP: Función principal que ejecuta todo el procesamiento
        Integra todas las partes del TP: tokenización, análisis de sentimiento y verificación de protocolo
        """
        conversacion = self.texto_conversacion.get(1.0, tk.END)
        
        if not conversacion.strip():
            messagebox.showwarning("Advertencia", "Por favor, ingrese una conversación para procesar")
            return
        
        try:
            # PARTE DEL TP: Ejecutar procesamiento completo
            # 1. Tokenización de la conversación
            # 2. Análisis de sentimiento
            # 3. Verificación del protocolo de atención
            resultados = self.tokenizador.procesar_conversacion(conversacion)
            
            # PARTE DEL TP: 3. Resultados y Reporte
            # Generar reporte final con todos los análisis
            reporte = self.tokenizador.generar_reporte(resultados)
            
            # Mostrar resultados en la interfaz
            self.texto_resultados.delete(1.0, tk.END)
            self.texto_resultados.insert(tk.END, reporte)
            
            # Mostrar mensaje de éxito con información de correcciones
            if "correcciones_totales" in resultados and resultados["correcciones_totales"]:
                num_correcciones = len(resultados["correcciones_totales"])
                messagebox.showinfo("Procesamiento completado", 
                                  f"Conversación procesada correctamente.\n"
                                  f"Se realizaron {num_correcciones} corrección(es).\n"
                                  f"Consulte el reporte para ver los detalles.")
            else:
                messagebox.showinfo("Éxito", "Conversación procesada correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la conversación: {str(e)}")
    
    def limpiar(self):
        """Limpia los campos de texto"""
        self.texto_conversacion.delete(1.0, tk.END)
        self.texto_resultados.delete(1.0, tk.END)

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazTokenizador(root)
    root.mainloop()
