# Este archivo contiene variables y configuraciones que usaremos en otros scripts.

STOP_WORDS_ES = [
    # Artículos
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'lo',

    # Preposiciones
    'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'durante',
    'en', 'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'segun',
    'sin', 'so', 'sobre', 'tras', 'versus', 'via',

    # Conjunciones y Adverbios
    'y', 'e', 'o', 'u', 'ni', 'pero', 'mas', 'sino', 'aunque', 'como',
    'que', 'cuando', 'donde', 'mientras', 'si', 'porque', 'pues', 'asi',
    'muy', 'mucho', 'tambien', 'ademas', 'ya', 'no',

    # Pronombres
    'yo', 'tu', 'el', 'ella', 'ello', 'nosotros', 'nosotras', 'vosotros',
    'vosotras', 'ellos', 'ellas', 'me', 'te', 'se', 'nos', 'os', 'le',
    'les', 'mi', 'ti', 'si', 'conmigo', 'contigo', 'consigo', 'su', 'sus',
    'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra',
    'vuestros', 'vuestras',

    # Verbos comunes (en infinitivo y algunas conjugaciones)
    'ser', 'estar', 'haber', 'tener', 'es', 'esta', 'estan', 'son', 'soy',
    'eres', 'somos', 'sido', 'siente', 'sienten', 'siento', 'sientes',
    'tiene', 'tienen', 'tengo', 'tienes', 'hemos', 'han', 'hay',

    # Palabras comunes en ofertas de empleo (RUÍDO ESPECÍFICO DEL DOMINIO)
    'empresa', 'importante', 'reconocida', 'lider', 'solicita', 'requiere',
    'busca', 'buscamos', 'necesita', 'contratar', 'incorporar', 'puesto',
    'vacante', 'cargo', 'posicion', 'area', 'gerencia', 'unidad', 'equipo',
    'experiencia', 'minima', 'anos', 'meses', 'comprobada', 'demostrable',
    'conocimiento', 'conocimientos', 'manejo', 'dominio', 'nivel',
    'avanzado', 'intermedio', 'basico', 'excluyente', 'deseable',
    'requisitos', 'funciones', 'responsabilidades', 'ofrecemos', 'beneficios',
    'sueldo', 'salario', 'acorde', 'mercado', 'ingreso', 'planilla',
    'disponibilidad', 'inmediata', 'horario', 'completo', 'tiempo', 'parcial',
    'lunes', 'viernes', 'sabado', 'trabajo', 'laboral', 'profesional',
    'oportunidad', 'desarrollo', 'linea', 'carrera', 'ambiente', 'agradable',
    'clima', 'distrito', 'zona', 'sede', 'formar', 'parte', 'nuestro',
    'queremos', 'talento', 'unete', 'postula', 'ref', 'referencia', 'etc',
    'formacion', 'titulo', 'profesional', 'egresado', 'bachiller', 'tecnico',
    'universitario', 'estudios', 'culminados', 'indispensable', 'residir',
    'contar', 'con', 'sin', 'al', 'del', 'se', 'del', 'por', 'ti', "Urgente"

   # --- Distritos de Lima Metropolitana (Ruido Geográfico) ---
    'ancon', 'ate', 'barranco', 'brena', 'carabayllo', 'chaclacayo',
    'chorrillos', 'cieneguilla', 'comas', 'el agustino', 'independencia',
    'jesus maria', 'la molina', 'la victoria', 'lince', 'los olivos',
    'lurigancho', 'chosica', 'lurin', 'magdalena del mar', 'magdalena',
    'miraflores', 'pachacamac', 'pucusana', 'pueblo libre', 'puente piedra',
    'punta hermosa', 'punta negra', 'rimac', 'san bartolo', 'san borja',
    'san isidro', 'san juan de lurigancho', 'sjl', 'san juan de miraflores', 'sjm',
    'san luis', 'san martin de porres', 'smp', 'san miguel', 'santa anita',
    'santa maria del mar', 'santa rosa', 'santiago de surco', 'surco',

    'surquillo', 'villa el salvador', 'ves', 'villa maria del triunfo', 'vmt',
    'cercado de lima',

    # --- Departamentos del Perú (Ruido Geográfico) ---
    'amazonas', 'ancash', 'apurimac', 'arequipa', 'ayacucho', 'cajamarca',
    'callao', 'cusco', 'huancavelica', 'huanuco', 'ica', 'junin',
    'la libertad', 'lambayeque', 'lima', 'loreto', 'madre de dios',
    'moquegua', 'pasco', 'piura', 'puno', 'san martin', 'tacna', 'tumbes',
    'ucayali', 'peru'

    # --- Ciudades del Perú (Ruido Geográfico) ---
    'lima', 'trujillo', 'arequipa', 'piura', 'chiclayo', 'cusco', 'callao',
    'huancayo', 'chimbote', 'pucallpa', 'ica', 'sullana', 'tarapoto',
    'cajamarca', 'moquegua', 'tacna', "Lurín"

    #-- otras palabras comunes que pueden aparecer en ofertas de empleo
    'trabajar', 'trabajando', 'trabajadora', 'trabajador', 'trabajadores',
    'cerca', 'jockey', 'plaza'
]
API_KEYS = {
    'ADZUNA_API_KEY': 'TU_API_KEY_AQUI'
}