# Informe del Trabajo Práctico: Análisis de Interacciones en Contact Centers

## 1. Preprocesamiento

### 1.1 Entrada de datos (audio a texto)

**A qué parte del trabajo corresponde:** Punto 1.1 del TP - Conversión de audio en transcripciones de conversaciones

**Qué fue lo que se hizo:** 
- Se implementó una interfaz gráfica que simula la entrada de transcripciones de conversaciones
- Se permite cargar conversaciones desde archivos de texto
- Se incluye un ejemplo predefinido de conversación entre agente y cliente
- La funcionalidad simula el resultado de un motor de reconocimiento de voz

**Código fuente que resuelve este punto:**
```python
def cargar_conversacion(self):
    """Permite cargar conversaciones desde archivos"""
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo de conversación",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
    )
    
def cargar_ejemplo(self):
    """Carga una conversación de ejemplo"""
    ejemplo = """Agente: Hola, bienvenido al servicio de Atención al Cliente...
    Cliente: Buenas, mi nombre es Juan Arias..."""
```

### 1.2 Tokenización

**A qué parte del trabajo corresponde:** Punto 1.2 del TP - Implementación del tokenizador para segmentar transcripciones en palabras

**Qué fue lo que se hizo:**
- Se implementó un tokenizador que divide el texto en lexemas usando expresiones regulares
- Se creó una base de datos SQLite como tabla de símbolos para almacenar palabras válidas
- Se implementó detección de lexemas desconocidos con interfaz interactiva
- Se aplicaron las distancias de Levenshtein y Hamming para sugerir palabras similares
- Se permite expansión dinámica de la tabla de símbolos

**Código fuente que resuelve este punto:**
```python
def tokenizar(self, texto):
    """Tokeniza un texto en palabras y verifica cada una"""
    palabras = re.findall(r'\b\w+\b', texto.lower())
    
    tokens = []
    for palabra in palabras:
        if palabra.lower() in self.palabras:
            token, puntuacion = self.palabras[palabra.lower()]
            tokens.append((palabra, token, puntuacion))
        else:
            # Manejo de palabras desconocidas
            if self.mostrar_popup_palabra_desconocida(palabra, root):
                token, puntuacion = self.palabras[palabra.lower()]
                tokens.append((palabra, token, puntuacion))

def distancia_levenshtein(self, s1, s2):
    """Implementa algoritmo de distancia mínima de edición"""
    
def distancia_hamming(self, s1, s2):
    """Implementa distancia de Hamming para igual longitud"""
```

## 2. Fase de Análisis - Speech Analytics

### 2.1 Análisis de Sentimiento

**A qué parte del trabajo corresponde:** Punto 2.1 del TP - Análisis de sentimiento con tabla de símbolos ponderada

**Qué fue lo que se hizo:**
- Se implementó una tabla de símbolos con puntuaciones para cada palabra (positiva/negativa)
- Se calculó el sentimiento general sumando/restando ponderaciones
- Se identificaron las palabras más positivas y negativas
- Se generó clasificación final: Positivo, Negativo o Neutral

**Código fuente que resuelve este punto:**
```python
def analizar_sentimiento(self, tokens):
    """Analiza el sentimiento de una lista de tokens"""
    puntuacion_total = sum(puntuacion for _, _, puntuacion in tokens)
    palabras_positivas = [(palabra, puntuacion) for palabra, _, puntuacion in tokens if puntuacion > 0]
    palabras_negativas = [(palabra, puntuacion) for palabra, _, puntuacion in tokens if puntuacion < 0]
    
    if puntuacion_total > 0:
        sentimiento = "Positivo"
    elif puntuacion_total < 0:
        sentimiento = "Negativo"
    else:
        sentimiento = "Neutral"
        
    # Palabras iniciales con ponderación en la BD:
    palabras_iniciales = [
        ('bueno', 'positivo', 1),
        ('amable', 'positivo', 2),
        ('problema', 'negativo', -1),
        ('mal', 'negativo', -2),
        ('excelente', 'positivo', 3),
        ('fatal', 'negativo', -3)
    ]
```

### 2.2 Verificación del Protocolo de Atención

**A qué parte del trabajo corresponde:** Punto 2.2 del TP - Verificación de protocolo basada en palabras clave

**Qué fue lo que se hizo:**
- Se implementaron las 4 fases del protocolo especificadas:
  1. Fase de saludo (detectar bienvenida)
  2. Identificación del cliente (verificar solicitud de identificación)
  3. No usar palabras rudas o prohibidas
  4. Despedida amable (cierre cortés)
- Se definieron categorías de tokens para cada fase del protocolo
- Se verificó cumplimiento solo para turnos del agente

**Código fuente que resuelve este punto:**
```python
def verificar_protocolo(self, tokens, es_agente=True):
    """Verifica si se sigue el protocolo de atención"""
    # Categorías definidas en __init__:
    self.categorias_protocolo = {
        'saludo': ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'bienvenido'],
        'identificacion': ['nombre', 'con quién', 'con quien', 'identificarse'],
        'palabras_prohibidas': ['inútil', 'tonto', 'estúpido', 'idiota'],
        'despedida': ['gracias', 'adiós', 'hasta luego', 'que tenga', 'buen día']
    }
    
    # Verificación de cada fase:
    tiene_saludo = any(saludo in texto for saludo in self.categorias_protocolo['saludo'])
    resultados['Fase de saludo'] = "OK" if tiene_saludo else "Faltante"
    
    tiene_identificacion = any(ident in texto for ident in self.categorias_protocolo['identificacion'])
    resultados['Identificación del cliente'] = "OK" if tiene_identificacion else "Faltante"
```

### 2.3 Implementación con Tokenización

**A qué parte del trabajo corresponde:** Punto 2.3 del TP - Integración de tokenización para recorrer palabras y verificar protocolo

**Qué fue lo que se hizo:**
- Se implementó procesamiento completo de conversaciones separando turnos de agente y cliente
- Se aplicó tokenización a cada turno
- Se combinaron tokens para análisis de sentimiento general
- Se separaron tokens del agente para verificación de protocolo

**Código fuente que resuelve este punto:**
```python
def procesar_conversacion(self, conversacion):
    """Procesa una conversación completa"""
    # Dividir en turnos de agente y cliente
    turnos = re.split(r'(Agente:|Cliente:)', conversacion)
    turnos = [t.strip() for t in turnos if t.strip()]
    
    resultados = {
        "tokens_totales": [],  # Para análisis de sentimiento general
        "tokens_agente": [],   # Solo para verificación de protocolo
        "protocolo": None
    }
    
    i = 0
    while i < len(turnos):
        if turnos[i] == "Agente:" and i + 1 < len(turnos):
            tokens = self.tokenizar(turnos[i + 1])
            resultados["tokens_totales"].extend(tokens)
            resultados["tokens_agente"].extend(tokens)
        elif turnos[i] == "Cliente:" and i + 1 < len(turnos):
            tokens = self.tokenizar(turnos[i + 1])
            resultados["tokens_totales"].extend(tokens)
```

## 3. Resultados y Reporte

### 3.1 Detección de Sentimiento

**A qué parte del trabajo corresponde:** Punto 3.1 del TP - Reporte de sentimiento con formato especificado

**Qué fue lo que se hizo:**
- Se generó reporte mostrando si la conversación fue positiva, neutral o negativa
- Se incluyó la ponderación final y conteo de palabras positivas/negativas
- Se identificaron las palabras más positivas y negativas con sus puntuaciones

**Código fuente que resuelve este punto:**
```python
def generar_reporte(self, resultados):
    """Genera reporte de sentimiento"""
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
```

### 3.2 Verificación del Protocolo de Atención

**A qué parte del trabajo corresponde:** Punto 3.2 del TP - Reporte de cumplimiento de protocolo

**Qué fue lo que se hizo:**
- Se generó reporte indicando si el agente siguió el protocolo
- Se mostró el estado de cada fase: OK o Faltante
- Se detectaron y reportaron palabras rudas utilizadas

**Código fuente que resuelve este punto:**
```python
def generar_reporte(self, resultados):
    """Genera reporte de protocolo"""
    if resultados.get("protocolo"):
        reporte += "VERIFICACIÓN DEL PROTOCOLO DE ATENCIÓN (AGENTE):\n"
        for fase, estado in resultados["protocolo"].items():
            reporte += f"{fase}: {estado}\n"
            
    # Ejemplo de salida:
    # Fase de saludo: OK
    # Identificación del cliente: OK  
    # Uso de palabras rudas: Ninguna detectada
    # Despedida amable: Faltante
```

## Tecnologías y Herramientas Utilizadas

- **Python 3.x** como lenguaje principal
- **SQLite** para la base de datos de palabras (tabla de símbolos)
- **Tkinter** para la interfaz gráfica
- **Expresiones regulares (re)** para tokenización
- **Algoritmos de distancia** (Levenshtein y Hamming) para sugerencias

## Funcionalidades Implementadas

1. ✅ Tokenización completa con manejo de palabras desconocidas
2. ✅ Base de datos expandible dinámicamente
3. ✅ Análisis de sentimiento con ponderaciones
4. ✅ Verificación completa del protocolo de atención
5. ✅ Sugerencias de palabras similares usando distancias
6. ✅ Interfaz gráfica intuitiva
7. ✅ Reportes detallados de resultados
8. ✅ Separación de análisis por rol (agente/cliente)

## Observaciones

- El sistema maneja eficientemente palabras desconocidas permitiendo expansión de vocabulario
- La implementación de ambas distancias (Levenshtein y Hamming) mejora las sugerencias
- La separación de tokens por rol permite análisis específicos según el contexto
- La interfaz gráfica facilita la interacción y visualización de resultados
```

