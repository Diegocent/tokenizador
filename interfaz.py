import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from tokenizador import Tokenizador

class InterfazTokenizador:
    def __init__(self, root):
        self.root = root
        self.root.title("Tokenizador para Contact Centers")
        self.root.geometry("900x700")
        
        # Inicializar tokenizador
        self.tokenizador = Tokenizador()
        
        # Crear interfaz
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(main_frame, text="Tokenizador para Análisis de Interacciones en Contact Centers", 
                         font=("Arial", 14, "bold"))
        titulo.pack(pady=10)
        
        # Frame para entrada de texto
        input_frame = tk.LabelFrame(main_frame, text="Conversación", padx=5, pady=5)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Área de texto para la conversación
        self.texto_conversacion = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=10)
        self.texto_conversacion.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botones para cargar y procesar
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        btn_cargar = tk.Button(btn_frame, text="Cargar conversación", command=self.cargar_conversacion)
        btn_cargar.pack(side=tk.LEFT, padx=5)
        
        btn_ejemplo = tk.Button(btn_frame, text="Cargar ejemplo", command=self.cargar_ejemplo)
        btn_ejemplo.pack(side=tk.LEFT, padx=5)
        
        btn_procesar = tk.Button(btn_frame, text="Procesar conversación", command=self.procesar_conversacion)
        btn_procesar.pack(side=tk.LEFT, padx=5)
        
        btn_limpiar = tk.Button(btn_frame, text="Limpiar", command=self.limpiar)
        btn_limpiar.pack(side=tk.LEFT, padx=5)
        
        # Frame para resultados
        result_frame = tk.LabelFrame(main_frame, text="Resultados", padx=5, pady=5)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Área de texto para los resultados
        self.texto_resultados = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=15)
        self.texto_resultados.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def cargar_conversacion(self):
        """Carga una conversación desde un archivo de texto"""
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
        """Carga una conversación de ejemplo"""
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
        """Procesa la conversación y muestra los resultados"""
        conversacion = self.texto_conversacion.get(1.0, tk.END)
        
        if not conversacion.strip():
            messagebox.showwarning("Advertencia", "Por favor, ingrese una conversación para procesar")
            return
        
        try:
            # Procesar la conversación
            resultados = self.tokenizador.procesar_conversacion(conversacion)
            
            # Generar reporte
            reporte = self.tokenizador.generar_reporte(resultados)
            
            # Mostrar resultados
            self.texto_resultados.delete(1.0, tk.END)
            self.texto_resultados.insert(tk.END, reporte)
            
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