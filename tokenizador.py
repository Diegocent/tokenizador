import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import re
import os
import numpy as np
from collections import defaultdict

class Tokenizador:
    def __init__(self):
        # Inicializar la base de datos
        self.inicializar_bd()
        
        # Cargar palabras desde la base de datos
        self.cargar_palabras()
        
        # Definir categorías de tokens para el protocolo
        self.categorias_protocolo = {
            'saludo': ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'bienvenido'],
            'identificacion': ['nombre', 'con quién', 'con quien', 'identificarse', 'quién es', 'quien es'],
            'palabras_prohibidas': ['inútil', 'tonto', 'estúpido', 'idiota', 'molesto', 'incompetente'],
            'despedida': ['gracias', 'adiós', 'hasta luego', 'que tenga', 'buen día', 'buenas tardes']
        }

    def inicializar_bd(self):
        """Inicializa la base de datos si no existe"""
        if not os.path.exists('tokenizador.db'):
            conn = sqlite3.connect('tokenizador.db')
            cursor = conn.cursor()
            
            # Crear tabla de palabras
            cursor.execute('''
            CREATE TABLE palabras (
                id INTEGER PRIMARY KEY,
                lexema TEXT UNIQUE,
                token TEXT,
                puntuacion INTEGER
            )
            ''')
            
            # Insertar algunas palabras iniciales con sus puntuaciones
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
                ('tonto', 'prohibida', -3)
            ]
            
            cursor.executemany('INSERT INTO palabras (lexema, token, puntuacion) VALUES (?, ?, ?)', 
                              palabras_iniciales)
            
            conn.commit()
            conn.close()
            print("Base de datos inicializada con palabras de ejemplo.")
    
    def cargar_palabras(self):
        """Carga las palabras desde la base de datos"""
        self.palabras = {}
        conn = sqlite3.connect('tokenizador.db')
        cursor = conn.cursor()
        cursor.execute('SELECT lexema, token, puntuacion FROM palabras')
        for lexema, token, puntuacion in cursor.fetchall():
            self.palabras[lexema.lower()] = (token, puntuacion)
        conn.close()
        print(f"Se cargaron {len(self.palabras)} palabras de la base de datos.")
    
    def agregar_palabra(self, lexema, token, puntuacion):
        """Agrega una nueva palabra a la base de datos"""
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
        """Calcula la distancia de Levenshtein entre dos cadenas"""
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
        """Calcula la distancia de Hamming entre dos cadenas"""
        # Igualar longitudes añadiendo espacios
        if len(s1) < len(s2):
            s1 = s1 + ' ' * (len(s2) - len(s1))
        elif len(s2) < len(s1):
            s2 = s2 + ' ' * (len(s1) - len(s2))
        
        # Calcular distancia
        return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))
    
    def sugerir_palabras_similares(self, palabra):
        """Sugiere palabras similares basadas en distancias de Levenshtein y Hamming"""
        sugerencias = []
        
        for lexema in self.palabras.keys():
            # Calcular distancias
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
    
    def mostrar_popup_palabra_desconocida(self, palabra, root=None):
        """Muestra un popup para confirmar si una palabra desconocida está bien escrita"""
        # Crear una ventana temporal si no se proporciona una
        if root is None:
            temp_root = tk.Tk()
            temp_root.withdraw()  # Ocultar ventana principal
        else:
            temp_root = root
        
        # Obtener sugerencias
        sugerencias = self.sugerir_palabras_similares(palabra)
        
        # Crear mensaje
        if sugerencias:
            mensaje = f"La palabra '{palabra}' no existe en la base de datos.\n\n¿Está bien escrita?\n\nSugerencias similares:\n" + "\n".join(sugerencias)
        else:
            mensaje = f"La palabra '{palabra}' no existe en la base de datos.\n\n¿Está bien escrita?"
        
        # Mostrar diálogo de confirmación
        respuesta = messagebox.askyesno("Palabra desconocida", mensaje)
        
        if respuesta:  # Si la palabra está bien escrita
            # Pedir token
            tokens_disponibles = set(token for token, _ in self.palabras.values())
            tokens_str = ", ".join(tokens_disponibles)
            
            token = simpledialog.askstring("Asignar token", 
                                          f"¿A qué token pertenece '{palabra}'?\n\nTokens existentes: {tokens_str}\n(Puede escribir uno nuevo)")
            
            if token:
                # Pedir puntuación
                puntuacion = simpledialog.askinteger("Asignar puntuación", 
                                                    f"¿Qué puntuación de sentimiento tiene '{palabra}'?\n(Número positivo o negativo)")
                
                if puntuacion is not None:
                    # Agregar palabra a la base de datos
                    self.agregar_palabra(palabra, token, puntuacion)
                    
                    if root is None:
                        temp_root.destroy()
                    return True
        
        # Si se canceló o no está bien escrita
        if root is None:
            temp_root.destroy()
        return False
    
    def tokenizar(self, texto):
        """Tokeniza un texto en palabras y verifica cada una"""
        # Dividir el texto en palabras
        palabras = re.findall(r'\b\w+\b', texto.lower())
        
        # Crear ventana temporal para los popups
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        
        tokens = []
        for palabra in palabras:
            if palabra.lower() in self.palabras:
                # Si la palabra existe, obtener su token y puntuación
                token, puntuacion = self.palabras[palabra.lower()]
                tokens.append((palabra, token, puntuacion))
            else:
                # Si no existe, mostrar popup
                if self.mostrar_popup_palabra_desconocida(palabra, root):
                    # Si se agregó correctamente, obtener su token y puntuación
                    token, puntuacion = self.palabras[palabra.lower()]
                    tokens.append((palabra, token, puntuacion))
                else:
                    # Si no se agregó, marcar como desconocida
                    tokens.append((palabra, "desconocido", 0))
        
        root.destroy()
        return tokens
    
    def analizar_sentimiento(self, tokens):
        """Analiza el sentimiento de una lista de tokens"""
        puntuacion_total = sum(puntuacion for _, _, puntuacion in tokens)
        palabras_positivas = [(palabra, puntuacion) for palabra, _, puntuacion in tokens if puntuacion > 0]
        palabras_negativas = [(palabra, puntuacion) for palabra, _, puntuacion in tokens if puntuacion < 0]
        
        # Determinar sentimiento general
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
        """Verifica si se sigue el protocolo de atención"""
        if not es_agente:
            return None  # No verificar protocolo para el cliente
        
        # Convertir tokens a texto para búsqueda
        texto = " ".join(palabra for palabra, _, _ in tokens).lower()
        
        # Verificar cada fase del protocolo
        resultados = {}
        
        # Fase de saludo
        tiene_saludo = any(saludo in texto for saludo in self.categorias_protocolo['saludo'])
        resultados['Fase de saludo'] = "OK" if tiene_saludo else "Faltante"
        
        # Identificación del cliente
        tiene_identificacion = any(ident in texto for ident in self.categorias_protocolo['identificacion'])
        resultados['Identificación del cliente'] = "OK" if tiene_identificacion else "Faltante"
        
        # Palabras prohibidas
        palabras_prohibidas_usadas = [palabra for palabra in self.categorias_protocolo['palabras_prohibidas'] if palabra in texto]
        if palabras_prohibidas_usadas:
            resultados['Uso de palabras rudas'] = f"Detectadas: {', '.join(palabras_prohibidas_usadas)}"
        else:
            resultados['Uso de palabras rudas'] = "Ninguna detectada"
        
        # Despedida amable
        tiene_despedida = any(despedida in texto for despedida in self.categorias_protocolo['despedida'])
        resultados['Despedida amable'] = "OK" if tiene_despedida else "Faltante"
        
        return resultados
    
    def procesar_conversacion(self, conversacion):
        """Procesa una conversación completa"""
        # Dividir la conversación en turnos de agente y cliente
        turnos = re.split(r'(Agente:|Cliente:)', conversacion)
        turnos = [t.strip() for t in turnos if t.strip()]
        
        resultados = {
            "tokens_agente": [],
            "tokens_cliente": [],
            "sentimiento_agente": None,
            "sentimiento_cliente": None,
            "protocolo": None
        }
        
        i = 0
        while i < len(turnos):
            if turnos[i] == "Agente:" and i + 1 < len(turnos):
                # Procesar turno del agente
                tokens_agente = self.tokenizar(turnos[i + 1])
                resultados["tokens_agente"].extend(tokens_agente)
                i += 2
            elif turnos[i] == "Cliente:" and i + 1 < len(turnos):
                # Procesar turno del cliente
                tokens_cliente = self.tokenizar(turnos[i + 1])
                resultados["tokens_cliente"].extend(tokens_cliente)
                i += 2
            else:
                i += 1
        
        # Analizar sentimiento
        if resultados["tokens_agente"]:
            resultados["sentimiento_agente"] = self.analizar_sentimiento(resultados["tokens_agente"])
        
        if resultados["tokens_cliente"]:
            resultados["sentimiento_cliente"] = self.analizar_sentimiento(resultados["tokens_cliente"])
        
        # Verificar protocolo
        if resultados["tokens_agente"]:
            resultados["protocolo"] = self.verificar_protocolo(resultados["tokens_agente"])
        
        return resultados
    
    def generar_reporte(self, resultados):
        """Genera un reporte basado en los resultados del procesamiento"""
        reporte = "=== REPORTE DE ANÁLISIS DE CONVERSACIÓN ===\n\n"
        
        # Reporte de sentimiento del agente
        if resultados["sentimiento_agente"]:
            s = resultados["sentimiento_agente"]
            reporte += "SENTIMIENTO DEL AGENTE:\n"
            reporte += f"Sentimiento general: {s['sentimiento']} ({s['puntuacion_total']})\n"
            reporte += f"Palabras positivas: {s['palabras_positivas']}\n"
            if s['palabra_mas_positiva']:
                reporte += f"Palabra más positiva: {s['palabra_mas_positiva'][0]}, +{s['palabra_mas_positiva'][1]}\n"
            reporte += f"Palabras negativas: {s['palabras_negativas']}\n"
            if s['palabra_mas_negativa']:
                reporte += f"Palabra más negativa: {s['palabra_mas_negativa'][0]}, {s['palabra_mas_negativa'][1]}\n"
            reporte += "\n"
        
        # Reporte de sentimiento del cliente
        if resultados["sentimiento_cliente"]:
            s = resultados["sentimiento_cliente"]
            reporte += "SENTIMIENTO DEL CLIENTE:\n"
            reporte += f"Sentimiento general: {s['sentimiento']} ({s['puntuacion_total']})\n"
            reporte += f"Palabras positivas: {s['palabras_positivas']}\n"
            if s['palabra_mas_positiva']:
                reporte += f"Palabra más positiva: {s['palabra_mas_positiva'][0]}, +{s['palabra_mas_positiva'][1]}\n"
            reporte += f"Palabras negativas: {s['palabras_negativas']}\n"
            if s['palabra_mas_negativa']:
                reporte += f"Palabra más negativa: {s['palabra_mas_negativa'][0]}, {s['palabra_mas_negativa'][1]}\n"
            reporte += "\n"
        
        # Reporte de protocolo
        if resultados["protocolo"]:
            reporte += "VERIFICACIÓN DEL PROTOCOLO DE ATENCIÓN:\n"
            for fase, estado in resultados["protocolo"].items():
                reporte += f"{fase}: {estado}\n"
        
        return reporte

# Ejemplo de uso
if __name__ == "__main__":
    tokenizador = Tokenizador()
    
    # Ejemplo de conversación
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