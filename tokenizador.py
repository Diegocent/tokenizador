import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import re
import os
import numpy as np
from collections import defaultdict
from tkinter import ttk

class TokenDialog(tk.Toplevel):
    """
    PARTE DEL TP: 1.2 Tokenización - Detección de lexemas
    Diálogo personalizado para manejar palabras desconocidas y asignar tokens
    """
    def __init__(self, parent, title, prompt, tokens_disponibles):
        super().__init__(parent)
        self.title(title)
        self.attributes('-topmost', True)
        self.resizable(False, False)
        
        # Configuración para centrar la ventana
        window_width = 450
        window_height = 180
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        self.result = None
        self.tokens_disponibles = tokens_disponibles
        
        # Frame principal para mejor organización
        main_frame = tk.Frame(self, padx=15, pady=15)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Etiqueta con la pregunta
        lbl_prompt = tk.Label(main_frame, text=prompt, wraplength=400, justify=tk.LEFT)
        lbl_prompt.pack(pady=(0, 10), anchor=tk.W)
        
        # Combobox con estilo mejorado
        self.combo = ttk.Combobox(main_frame)
        self.combo.pack(fill=tk.X, pady=5)
        self.combo['values'] = list(tokens_disponibles)
        self.combo.set("")
        self.combo.focus_set()
        
        # Frame para botones
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=(10, 0))
        
        # Botones con mejor estilo
        btn_aceptar = ttk.Button(btn_frame, text="Aceptar", command=self.on_accept)
        btn_aceptar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(btn_frame, text="Cancelar", command=self.on_cancel)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        # Configurar autocompletado
        self.combo.bind('<KeyRelease>', self.autocomplete)
        self.bind('<Return>', lambda e: self.on_accept())
        self.bind('<Escape>', lambda e: self.on_cancel())
    
    def autocomplete(self, event):
        """Implementa autocompletado para facilitar la selección de tokens"""
        value = event.widget.get()
        if value == '':
            self.combo['values'] = list(self.tokens_disponibles)
        else:
            data = []
            for item in self.tokens_disponibles:
                if value.lower() in item.lower():
                    data.append(item)
            self.combo['values'] = data
    
    def on_accept(self):
        self.result = self.combo.get()
        self.destroy()
    
    def on_cancel(self):
        self.destroy()

class SugerenciasDialog(tk.Toplevel):
    """
    PARTE DEL TP: 1.2 Tokenización - Diálogo para seleccionar sugerencias de palabras similares
    Permite seleccionar una palabra del dropdown de sugerencias o mantener la original
    """
    def __init__(self, parent, palabra_original, sugerencias):
        super().__init__(parent)
        self.title("Palabra desconocida - Seleccionar corrección")
        self.attributes('-topmost', True)
        self.resizable(False, False)
        
        # Configuración para centrar la ventana
        window_width = 500
        window_height = 280
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        self.result = None
        self.palabra_original = palabra_original
        self.sugerencias = sugerencias
        
        # Frame principal
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Título y explicación
        titulo = tk.Label(main_frame, 
                         text=f"La palabra '{palabra_original}' no existe en la base de datos",
                         font=("Arial", 12, "bold"),
                         fg="red")
        titulo.pack(pady=(0, 10))
        
        explicacion = tk.Label(main_frame,
                              text="Seleccione una opción del menú desplegable:",
                              wraplength=450)
        explicacion.pack(pady=(0, 15))
        
        # Frame para el combobox
        combo_frame = tk.LabelFrame(main_frame, text="Opciones disponibles", padx=10, pady=10)
        combo_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Preparar opciones para el combobox
        opciones = [f"Mantener '{palabra_original}' (agregar como nueva palabra)"]
        
        if sugerencias:
            for sugerencia in sugerencias:
                opciones.append(f"Reemplazar por '{sugerencia}'")
        else:
            opciones.append("(No hay sugerencias disponibles)")
        
        # Combobox con las opciones
        self.combo = ttk.Combobox(combo_frame, state="readonly", width=60)
        self.combo.pack(fill=tk.X, pady=5)
        self.combo['values'] = opciones
        self.combo.set(opciones[0])  # Seleccionar la primera opción por defecto
        self.combo.focus_set()
        
        # Frame para botones
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=(10, 0))
        
        # Botones
        btn_aceptar = ttk.Button(btn_frame, text="Aceptar", command=self.on_accept)
        btn_aceptar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(btn_frame, text="Cancelar", command=self.on_cancel)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        # Configurar teclas
        self.bind('<Return>', lambda e: self.on_accept())
        self.bind('<Escape>', lambda e: self.on_cancel())
    
    def on_accept(self):
        seleccion = self.combo.get()
        
        if seleccion.startswith("Mantener"):
            # Si se seleccionó mantener la palabra original
            self.result = self.palabra_original
        elif seleccion.startswith("Reemplazar por"):
            # Extraer la palabra de la opción seleccionada
            # Formato: "Reemplazar por 'palabra'"
            import re
            match = re.search(r"'([^']+)'", seleccion)
            if match:
                self.result = match.group(1)
            else:
                self.result = self.palabra_original
        else:
            # Caso por defecto
            self.result = self.palabra_original
            
        self.destroy()
    
    def on_cancel(self):
        self.result = None
        self.destroy()

class Tokenizador:
    """
    CLASE PRINCIPAL QUE IMPLEMENTA EL SISTEMA COMPLETO DEL TRABAJO PRÁCTICO
    """
    def __init__(self):
        # PARTE DEL TP: 1.2 Tokenización - Base de datos (tabla de símbolos)
        # Inicializar la base de datos para almacenar lexemas y tokens
        self.inicializar_bd()
        
        # Cargar palabras desde la base de datos
        self.cargar_palabras()
        
        # PARTE DEL TP: 2.2 Verificación del Protocolo de Atención
        # Definir categorías de tokens para el protocolo de atención al cliente
        self.categorias_protocolo = {
            'saludo': ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'bienvenido'],
            'identificacion': ['nombre', 'con quién', 'con quien', 'identificarse', 'quién es', 'quien es'],
            'palabras_prohibidas': ['inútil', 'tonto', 'estúpido', 'idiota', 'molesto', 'incompetente'],
            'despedida': ['gracias', 'adiós', 'hasta luego', 'que tenga', 'buen día', 'buenas tardes']
        }

    def inicializar_bd(self):
        """
        PARTE DEL TP: 1.2 Tokenización - Base de datos (tabla de símbolos)
        Crea la base de datos SQLite con palabras iniciales y sus puntuaciones
        """
        if not os.path.exists('tokenizador.db'):
            conn = sqlite3.connect('tokenizador.db')
            cursor = conn.cursor()
            
            # Crear tabla de palabras con lexema, token y puntuación
            cursor.execute('''
            CREATE TABLE palabras (
                id INTEGER PRIMARY KEY,
                lexema TEXT UNIQUE,
                token TEXT,
                puntuacion INTEGER
            )
            ''')
            
            # PARTE DEL TP: 2.1 Análisis de Sentimiento - Tabla de símbolos con ponderación
            # Insertar palabras iniciales con sus puntuaciones para análisis de sentimiento
            palabras_iniciales = [
                ('bueno', 'positivo', 1),
                ('amable', 'positivo', 2),
                ('problema', 'negativo', -1),
                ('mal', 'negativo', -2),
                ('excelente', 'positivo', 3),
                ('fatal', 'negativo', -3),
                ('hola', 'saludo', 1),
                ('bienvenido', 'saludo', 1),
                ('gracias', 'despedida', 1),
                ('nombre', 'identificacion', 0),
                ('inútil', 'prohibida', -3),
                ('tonto', 'prohibida', -3),
                ('al', 'articulo', 0),
                ('el', 'articulo', 0),
                ('la', 'articulo', 0),
                ('de', 'preposicion', 0),
                ('en', 'preposicion', 0),
                ('con', 'preposicion', 0)
            ]
            
            cursor.executemany('INSERT INTO palabras (lexema, token, puntuacion) VALUES (?, ?, ?)', 
                              palabras_iniciales)
            
            conn.commit()
            conn.close()
            print("Base de datos inicializada con palabras de ejemplo.")
    
    def cargar_palabras(self):
        """
        PARTE DEL TP: 1.2 Tokenización - Carga de tabla de símbolos
        Carga todas las palabras de la base de datos en memoria
        """
        self.palabras = {}
        conn = sqlite3.connect('tokenizador.db')
        cursor = conn.cursor()
        cursor.execute('SELECT lexema, token, puntuacion FROM palabras')
        for lexema, token, puntuacion in cursor.fetchall():
            self.palabras[lexema.lower()] = (token, puntuacion)
        conn.close()
        print(f"Se cargaron {len(self.palabras)} palabras de la base de datos.")
    
    def agregar_palabra(self, lexema, token, puntuacion):
        """
        PARTE DEL TP: 1.2 Tokenización - Expansión dinámica de la tabla de símbolos
        Permite agregar nuevas palabras a la base de datos durante la ejecución
        """
        conn = sqlite3.connect('tokenizador.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO palabras (lexema, token, puntuacion) VALUES (?, ?, ?)',
                          (lexema, token, puntuacion))
            conn.commit()
            self.palabras[lexema.lower()] = (token, puntuacion)
            print(f"Palabra '{lexema}' agregada con token '{token}' y puntuación {puntuacion}")
            return True
        except sqlite3.IntegrityError:
            print(f"La palabra '{lexema}' ya existe en la base de datos")
            return False
        finally:
            conn.close()
    
    def distancia_levenshtein(self, s1, s2):
        """
        PARTE DEL TP: 1.2 Tokenización - Sugerencia de lexemas usando distancia de Levenshtein
        Implementa el algoritmo de distancia mínima de edición para sugerir palabras similares
        """
        if len(s1) < len(s2):
            return self.distancia_levenshtein(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def distancia_hamming(self, s1, s2):
        """
        PARTE DEL TP: 1.2 Tokenización - Sugerencia de lexemas usando distancia de Hamming
        Implementa la distancia de Hamming para palabras de igual longitud
        """
        # Igualar longitudes añadiendo espacios (como especifica el TP)
        if len(s1) < len(s2):
            s1 = s1 + ' ' * (len(s2) - len(s1))
        elif len(s2) < len(s1):
            s2 = s2 + ' ' * (len(s1) - len(s2))
        
        # Calcular distancia
        return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))
    
    def sugerir_palabras_similares(self, palabra):
        """
        PARTE DEL TP: 1.2 Tokenización - Sistema de sugerencias para palabras no válidas
        Combina ambas distancias para sugerir palabras similares cuando se encuentra un lexema no válido
        """
        sugerencias = []
        
        for lexema in self.palabras.keys():
            # Calcular ambas distancias como especifica el TP
            dist_lev = self.distancia_levenshtein(palabra.lower(), lexema.lower())
            dist_ham = self.distancia_hamming(palabra.lower(), lexema.lower())
            
            # Usar el mínimo de ambas distancias
            dist = min(dist_lev, dist_ham)
            
            # Si la distancia es pequeña, agregar a sugerencias
            if dist <= 2:  # Umbral ajustable
                sugerencias.append((lexema, dist))
        
        # Ordenar por distancia (menor primero)
        sugerencias.sort(key=lambda x: x[1])
        
        # Devolver hasta 5 sugerencias
        return [s[0] for s in sugerencias[:5]]
    
    def procesar_palabra_con_sugerencia(self, palabra_seleccionada, root):
        """
        PARTE DEL TP: Procesar palabra seleccionada (original o sugerencia) 
        y asignar token y puntuación
        """
        # Obtener tokens disponibles
        tokens_disponibles = set(token for token, _ in self.palabras.values())
        
        # Crear y mostrar diálogo para asignar token
        token_dialog = TokenDialog(root, "Asignar token", 
                        f"¿A qué token pertenece '{palabra_seleccionada}'?\nSeleccione uno existente o escriba uno nuevo:",
                        tokens_disponibles)
        root.wait_window(token_dialog)
        
        token = token_dialog.result
        
        if token:
            # Pedir puntuación para análisis de sentimiento
            puntuacion = simpledialog.askinteger("Asignar puntuación", 
                                        f"¿Qué puntuación de sentimiento tiene '{palabra_seleccionada}'?\n(Número positivo o negativo)",
                                        parent=root)
            
            if puntuacion is not None:
                # Agregar palabra a la base de datos
                self.agregar_palabra(palabra_seleccionada, token, puntuacion)
                return True
        
        return False

    def mostrar_popup_palabra_desconocida(self, palabra, root=None):
        """
        PARTE DEL TP: 1.2 Tokenización - Manejo interactivo de palabras desconocidas
        Implementa el flujo mejorado: mostrar sugerencias en lista seleccionable,
        permitir reemplazo y registro de correcciones
        """
        # Crear una ventana temporal si no se proporciona una
        temp_root = None
        if root is None:
            temp_root = tk.Tk()
            temp_root.withdraw()  # Ocultar ventana principal
            root = temp_root
    
        # Hacer que la ventana temporal sea transitoria y capturar el foco
        root.attributes('-topmost', True)
    
        # Obtener sugerencias usando las distancias implementadas
        sugerencias = self.sugerir_palabras_similares(palabra)
    
        # Crear y mostrar el diálogo de sugerencias
        dialog = SugerenciasDialog(root, palabra, sugerencias)
        root.wait_window(dialog)
    
        palabra_seleccionada = dialog.result
    
        if palabra_seleccionada is None:
            # Si se canceló
            if temp_root is not None:
                temp_root.destroy()
            return None, False, None  # palabra_final, procesada, correccion_info
    
        # Determinar si es corrección o palabra nueva
        es_correccion = palabra_seleccionada != palabra
        correccion_info = None
        
        if es_correccion:
            # Es una corrección - la palabra seleccionada ya existe en la BD
            correccion_info = {
                'palabra_original': palabra,
                'palabra_corregida': palabra_seleccionada,
                'token': self.palabras[palabra_seleccionada.lower()][0],
                'puntuacion': self.palabras[palabra_seleccionada.lower()][1]
            }
            
            if temp_root is not None:
                temp_root.destroy()
            return palabra_seleccionada, True, correccion_info
        else:
            # Es palabra nueva - necesita asignar token y puntuación
            procesada = self.procesar_palabra_con_sugerencia(palabra_seleccionada, root)
            
            if temp_root is not None:
                temp_root.destroy()
            return palabra_seleccionada, procesada, None
    
    def tokenizar(self, texto):
        """
        PARTE DEL TP: 1.2 Tokenización - Segmentación en palabras/lexemas
        Implementa el tokenizador principal que divide el texto en palabras y las cataloga
        Ahora incluye manejo de correcciones sin modificar el texto original
        """
        # Dividir el texto en palabras usando expresiones regulares
        palabras = re.findall(r'\b\w+\b', texto.lower())

        # Crear ventana temporal para los popups
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        root.attributes('-topmost', True)  # Asegurar que esté encima

        tokens = []
        correcciones_realizadas = []  # Para llevar registro de las correcciones

        for palabra in palabras:
            if palabra.lower() in self.palabras:
                # Si la palabra existe en la tabla de símbolos, obtener su token y puntuación
                token, puntuacion = self.palabras[palabra.lower()]
                tokens.append((palabra, token, puntuacion))
            else:
                # Si no existe, aplicar el flujo de manejo de palabras desconocidas
                palabra_resultado, procesada, correccion_info = self.mostrar_popup_palabra_desconocida(palabra, root)
            
                if procesada and palabra_resultado:
                    if correccion_info:
                        # Se realizó una corrección
                        correcciones_realizadas.append(correccion_info)
                        print(f"CORRECCIÓN: '{palabra}' → '{palabra_resultado}'")
                    
                    # Obtener token y puntuación de la palabra (original o corregida)
                    token, puntuacion = self.palabras[palabra_resultado.lower()]
                    tokens.append((palabra_resultado, token, puntuacion))
                else:
                    # Si no se procesó o se canceló, marcar como desconocida
                    tokens.append((palabra, "desconocido", 0))

        root.destroy()

        return tokens, correcciones_realizadas  # Retornar también las correcciones
    
    def analizar_sentimiento(self, tokens):
        """
        PARTE DEL TP: 2.1 Análisis de Sentimiento
        Implementa el cálculo de sentimiento basado en la ponderación de palabras
        """
        # Calcular puntuación total sumando/restando ponderaciones
        puntuacion_total = sum(puntuacion for _, _, puntuacion in tokens)
        
        # Separar palabras positivas y negativas
        palabras_positivas = [(palabra, puntuacion) for palabra, _, puntuacion in tokens if puntuacion > 0]
        palabras_negativas = [(palabra, puntuacion) for palabra, _, puntuacion in tokens if puntuacion < 0]
        
        # Determinar sentimiento general según especificación del TP
        if puntuacion_total > 0:
            sentimiento = "Positivo"
        elif puntuacion_total < 0:
            sentimiento = "Negativo"
        else:
            sentimiento = "Neutral"
        
        # Encontrar palabras más positivas y negativas
        palabra_mas_positiva = max(palabras_positivas, key=lambda x: x[1]) if palabras_positivas else None
        palabra_mas_negativa = min(palabras_negativas, key=lambda x: x[1]) if palabras_negativas else None
        
        return {
            "sentimiento": sentimiento,
            "puntuacion_total": puntuacion_total,
            "palabras_positivas": len(palabras_positivas),
            "palabras_negativas": len(palabras_negativas),
            "palabra_mas_positiva": palabra_mas_positiva,
            "palabra_mas_negativa": palabra_mas_negativa
        }
    
    def verificar_protocolo(self, tokens, es_agente=True):
        """
        PARTE DEL TP: 2.2 Verificación del Protocolo de Atención
        Implementa la verificación de las 4 fases del protocolo especificadas en el TP
        """
        if not es_agente:
            return None  # No verificar protocolo para el cliente
        
        # Convertir tokens a texto para búsqueda de patrones
        texto = " ".join(palabra for palabra, _, _ in tokens).lower()
        
        # Verificar cada fase del protocolo como especifica el TP
        resultados = {}
        
        # FASE 1: Fase de saludo - Detectar bienvenida
        tiene_saludo = any(saludo in texto for saludo in self.categorias_protocolo['saludo'])
        resultados['Fase de saludo'] = "OK" if tiene_saludo else "Faltante"
        
        # FASE 2: Identificación del cliente - Verificar si pide identificación
        tiene_identificacion = any(ident in texto for ident in self.categorias_protocolo['identificacion'])
        resultados['Identificación del cliente'] = "OK" if tiene_identificacion else "Faltante"
        
        # FASE 3: No usar palabras rudas o prohibidas - Detectar palabras no permitidas
        palabras_prohibidas_usadas = [palabra for palabra in self.categorias_protocolo['palabras_prohibidas'] if palabra in texto]
        if palabras_prohibidas_usadas:
            resultados['Uso de palabras rudas'] = f"Detectadas: {', '.join(palabras_prohibidas_usadas)}"
        else:
            resultados['Uso de palabras rudas'] = "Ninguna detectada"
        
        # FASE 4: Despedida amable - Comprobar cierre cortés
        tiene_despedida = any(despedida in texto for despedida in self.categorias_protocolo['despedida'])
        resultados['Despedida amable'] = "OK" if tiene_despedida else "Faltante"
        
        return resultados
    
    def procesar_conversacion(self, conversacion):
        """
        PARTE DEL TP: 2.3 Implementación con Tokenización
        Procesa una conversación completa separando turnos de agente y cliente
        """
        # Dividir la conversación en turnos de agente y cliente
        turnos = re.split(r'(Agente:|Cliente:)', conversacion)
        turnos = [t.strip() for t in turnos if t.strip()]
        
        resultados = {
            "tokens_totales": [],  # Para el análisis de sentimiento general
            "tokens_agente": [],   # Solo para verificación de protocolo
            "protocolo": None,
            "correcciones_totales": []  # Para llevar registro de todas las correcciones
        }
        
        i = 0
        while i < len(turnos):
            if turnos[i] == "Agente:" and i + 1 < len(turnos):
                # Procesar turno del agente
                tokens, correcciones = self.tokenizar(turnos[i + 1])
                resultados["tokens_totales"].extend(tokens)
                resultados["tokens_agente"].extend(tokens)  # Guardamos aparte para protocolo
                resultados["correcciones_totales"].extend(correcciones)
                i += 2
            elif turnos[i] == "Cliente:" and i + 1 < len(turnos):
                # Procesar turno del cliente
                tokens, correcciones = self.tokenizar(turnos[i + 1])
                resultados["tokens_totales"].extend(tokens)
                resultados["correcciones_totales"].extend(correcciones)
                i += 2
            else:
                i += 1
        
        # PARTE DEL TP: 2.1 Análisis de Sentimiento - Análisis general (combinando agente y cliente)
        if resultados["tokens_totales"]:
            resultados["sentimiento_general"] = self.analizar_sentimiento(resultados["tokens_totales"])
        
        # PARTE DEL TP: 2.2 Verificación del Protocolo - Solo con los tokens del agente
        if resultados["tokens_agente"]:
            resultados["protocolo"] = self.verificar_protocolo(resultados["tokens_agente"], es_agente=True)
        
        return resultados
    
    def generar_reporte(self, resultados):
        """
        PARTE DEL TP: 3. Resultados y Reporte
        Genera el reporte final con sentimiento y verificación de protocolo
        """
        reporte = "=== REPORTE DE ANÁLISIS DE CONVERSACIÓN ===\n\n"
        
        # PARTE DEL TP: 3.1 Detección de Sentimiento - Reporte de sentimiento
        if "sentimiento_general" in resultados:
            s = resultados["sentimiento_general"]
            reporte += "SENTIMIENTO GENERAL DE LA CONVERSACIÓN:\n"
            reporte += f"Sentimiento general: {s['sentimiento']} ({s['puntuacion_total']})\n"
            reporte += f"Palabras positivas: {s['palabras_positivas']}\n"
            if s['palabra_mas_positiva']:
                reporte += f"Palabra más positiva: {s['palabra_mas_positiva'][0]}, +{s['palabra_mas_positiva'][1]}\n"
            reporte += f"Palabras negativas: {s['palabras_negativas']}\n"
            if s['palabra_mas_negativa']:
                reporte += f"Palabra más negativa: {s['palabra_mas_negativa'][0]}, {s['palabra_mas_negativa'][1]}\n"
            reporte += "\n"
        
        # PARTE DEL TP: 3.2 Verificación del Protocolo de Atención - Reporte de protocolo
        if resultados.get("protocolo"):
            reporte += "VERIFICACIÓN DEL PROTOCOLO DE ATENCIÓN (AGENTE):\n"
            for fase, estado in resultados["protocolo"].items():
                reporte += f"{fase}: {estado}\n"
            reporte += "\n"
        
        # PARTE DEL TP: Reporte de correcciones realizadas
        if "correcciones_totales" in resultados and resultados["correcciones_totales"]:
            reporte += "=== CORRECCIONES REALIZADAS ===\n"
            for correccion in resultados["correcciones_totales"]:
                reporte += f"Palabra mal escrita: '{correccion['palabra_original']}'\n"
                reporte += f"Corrección seleccionada: '{correccion['palabra_corregida']}'\n"
                reporte += f"Token asignado: {correccion['token']}\n"
                reporte += f"Puntuación: {correccion['puntuacion']}\n"
                reporte += "-" * 40 + "\n"
        
        return reporte

# Ejemplo de uso
if __name__ == "__main__":
    tokenizador = Tokenizador()
    
    # Ejemplo de conversación para demostrar funcionalidad
    conversacion = """
    Agente: Hola, bienvenido al servicio de Atención al Cliente. ¿Con quién tengo el gusto de hablar?
    Cliente: Buenas, mi nombre es Juan Arias, quiero hacer una consulta acerca de mi factura.
    Agente: Claro Juan, cuénteme en qué puedo ayudarle con su factura.
    Cliente: Recibí un cobro por un servicio que nunca contraté, estoy muy molesto por esto.
    Agente: Entiendo su frustración, vamos a revisar ese cargo y solucionarlo de inmediato.
    Cliente: Gracias, espero que puedan resolverlo pronto.
    Agente: No se preocupe, ya estoy gestionando la eliminación del cargo. En unos minutos estará resuelto.
    """
    
    print("Procesando conversación de ejemplo...")
    resultados = tokenizador.procesar_conversacion(conversacion)
    
    # Generar y mostrar reporte
    reporte = tokenizador.generar_reporte(resultados)
    print("\n" + reporte)
