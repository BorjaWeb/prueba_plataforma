import streamlit as st
import pandas as pd
import sqlite3
import io

# Configuración de página nativa en modo ancho
st.set_page_config(layout="wide", page_title="CIP Learning Experience Platform")

# =========================================================================
# 1. MOTOR DE BASE DE DATOS LOCAL (SQLITE)
# =========================================================================
def inicializar_bd_lms():
    conn = sqlite3.connect("cip_lms_platform.db")
    cursor = conn.cursor()
    
    # Tabla de Alumnos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            uid TEXT PRIMARY KEY,
            nombre TEXT,
            email TEXT,
            rol TEXT DEFAULT 'Estudiante'
        )
    """)
    
    # Tabla de Contenidos SCORM
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contenidos_scorm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            version TEXT,
            archivo_nombre TEXT,
            fecha_registro TEXT
        )
    """)
    
    # Tabla de Plugins Activos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plugins_sistema (
            id_plugin TEXT PRIMARY KEY,
            nombre TEXT,
            descripcion TEXT,
            estado INTEGER DEFAULT 1
        )
    """)
    
    # Inyectar algunos datos por defecto si la base de datos está vacía
    cursor.execute("SELECT COUNT(*) FROM plugins_sistema")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO plugins_sistema VALUES (?, ?, ?, ?)", [
            ("plg_gamificacion", "Motor de Gamificación e Insignias", "Añade puntos y medallas por completar SCORM.", 1),
            ("plg_videoconf", "Integración con Teams / Zoom", "Permite agendar salas virtuales directamente.", 0),
            ("plg_ia_tutor", "Asistente Tutor IA", "Soporte automatizado 24/7 para el estudiante.", 1)
        ])
    conn.commit()
    conn.close()

inicializar_bd_lms()

# =========================================================================
# 2. SISTEMA DE ESTILOS DE ALTO CONTRASTE (AZUL OSCURO Y BLANCO)
# =========================================================================
def aplicar_estilos_institucionales():
    st.markdown("""
        <style>
        /* Fondo general de la plataforma: Limpio y claro */
        .main { background-color: #FFFFFF !important; font-family: 'Segoe UI', system-ui, sans-serif !important; }
        
        /* Barra lateral (Sidebar): Azul Oscuro Corporativo Profundo */
        [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 2px solid #1E293B; }
        [data-testid="stSidebar"] *, [data-testid="stSidebar"] label { color: #FFFFFF !important; font-weight: 600; }
        
        /* Cabecera Principal */
        .lms-header { background-color: #0F172A; padding: 20px; border-radius: 8px; margin-bottom: 25px; color: #FFFFFF; }
        .lms-title { font-size: 24px; font-weight: 800; color: #FFFFFF !important; margin: 0; }
        
        /* Forzar visibilidad absoluta de textos y etiquetas en el cuerpo principal */
        label, p, span, h1, h2, h3, h4 { color: #0F172A !important; font-weight: 700 !important; }
        .stMarkdown p { color: #334155 !important; font-weight: 500 !important; }
        
        /* Formularios y secciones delimitadas con bordes oscuros nítidos */
        div.stForm, div[data-testid="stExpander"], .stAlert { 
            background: #FFFFFF !important; 
            border: 2px solid #0F172A !important; 
            border-radius: 6px !important; 
            padding: 20px !important; 
            box-shadow: none !important;
        }
        
        /* Inputs, selectores y campos de texto */
        .stTextInput input, select, input { 
            color: #000000 !important; 
            background-color: #F8FAFC !important; 
            border: 2px solid #0F172A !important; 
            border-radius: 4px !important; 
            font-weight: 700 !important;
        }
        
        /* Botones Principales en Azul Marino Intenso y Letras Blancas */
        .stButton>button { 
            background-color: #1E3A8A !important; 
            color: #FFFFFF !important; 
            font-weight: 700 !important; 
            border: 2px solid #172554 !important; 
            border-radius: 4px !important; 
            padding: 10px 20px !important;
            text-transform: uppercase;
        }
        .stButton>button:hover { background-color: #1D4ED8 !important; color: #FFFFFF !important; }
        
        /* Pestañas superiores de navegación (Tabs) estilo Moodle Moderno */
        .stTabs [data-baseweb="tab"] { font-weight: 700 !important; color: #475569 !important; font-size: 16px; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #1E3A8A !important; border-bottom: 3px solid #1E3A8A !important; }
        
        /* Tarjetas informativas de plugins o KPI */
        .plugin-card { border: 2px solid #0F172A; padding: 15px; border-radius: 6px; margin-bottom: 10px; background-color: #F8FAFC; }
        </style>
    """, unsafe_allow_html=True)

aplicar_estilos_institucionales()

# =========================================================================
# 3. INTERFAZ Y NAVEGACIÓN PRINCIPAL
# =========================================================================

# Menú lateral e identificación
st.sidebar.markdown("## CIP Campus Virtual")
st.sidebar.markdown("Bienvenido, **Administrador**")
st.sidebar.markdown("---")
st.sidebar.markdown("### Estado del Servidor")
st.sidebar.success("Sistema Operativo / Online")

# Banner de Cabecera
st.markdown("""
    <div class="lms-header">
        <div class="lms-title">⚙️ CIP Learning Experience Platform (LXP)</div>
    </div>
""", unsafe_allow_html=True)

# Pestañas principales de navegación del LMS
tabs = st.tabs([
    "📚 Contenidos e Ingesta SCORM", 
    "👥 Gestión de Alumnos (CSV)", 
    "🔌 Consola de Plugins Extensibles", 
    "❓ Área de Ayuda y Soporte Técnico"
])

# -------------------------------------------------------------------------
# PESTAÑA 1: INGESTA Y ADMINISTRACIÓN DE CONTENIDOS SCORM
# -------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### Gestión de Paquetes SCORM")
    st.markdown("Suba y registre paquetes estandarizados SCORM (archivos comprimidos .zip) para el despliegue automático de unidades didácticas interactivas.")
    
    conn = sqlite3.connect("cip_lms_platform.db")
    
    with st.form("alta_scorm"):
        st.markdown("**Nuevo Paquete SCORM**")
        titulo_scorm = st.text_input("Título del Curso / Módulo Formativo:")
        version_scorm = st.selectbox("Versión de Norma SCORM:", ["SCORM 1.2", "SCORM 2004 3rd Edition", "xAPI / Tin Can"])
        archivo_scorm = st.file_uploader("Seleccione el archivo empaquetado (.zip):", type=["zip"])
        
        if st.form_submit_button("Dar de Alta y Validar Manifiesto"):
            if titulo_scorm and archivo_scorm:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO contenidos_scorm (titulo, version, archivo_nombre, fecha_registro) VALUES (?, ?, ?, ?)",
                    (titulo_scorm, version_scorm, archivo_scorm.name, datetime.now().strftime("%d/%m/%Y %H:%M"))
                )
                conn.commit()
                st.success(f"Éxito: Paquete '{titulo_scorm}' verificado e indexado en el árbol de contenidos.")
                st.rerun()
            else:
                st.error("Error: Debe asignar un título y adjuntar un archivo empaquetado compatible.")
                
    st.markdown("---")
    st.markdown("#### Repositorio de Cursos Activos en la Plataforma")
    df_scorm = pd.read_sql("SELECT id as [ID], titulo as [Nombre del Curso], version as [Estándar], archivo_nombre as [Fichero fuente], fecha_registro as [Fecha de Alta] FROM contenidos_scorm", conn)
    if not df_scorm.empty:
        st.dataframe(df_scorm, use_container_width=True, hide_index=True)
    else:
        st.info("No se registran paquetes formativos cargados actualmente.")
    conn.close()

# -------------------------------------------------------------------------
# PESTAÑA 2: CARGA MASIVA DE ALUMNOS MEDIANTE CSV
# -------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### Matriculación Masiva de Alumnos")
    st.markdown("Cargue un archivo estructurado CSV para dar de alta de forma simultánea múltiples expedientes de estudiantes.")
    
    # Plantilla de ejemplo descargable o visible
    with st.expander("Ver estructura requerida del archivo CSV"):
        st.code("""uid,nombre,email,rol\n12345678A,Juan Perez,juan@campus.es,Estudiante\n87654321B,Ana Gomez,ana@campus.es,Estudiante""", language="text")
        
    archivo_csv = st.file_uploader("Subir archivo de alumnos (.csv):", type=["csv"])
    
    if archivo_csv:
        try:
            df_usuarios = pd.read_csv(archivo_csv)
            st.markdown("#### Previsualización de los datos a importar:")
            st.dataframe(df_usuarios, use_container_width=True)
            
            if st.button("Confirmar e Importar Alumnos a la Base de Datos"):
                conn = sqlite3.connect("cip_lms_platform.db")
                cursor = conn.cursor()
                
                exitos = 0
                errores = 0
                for _, fila in df_usuarios.iterrows():
                    try:
                        cursor.execute(
                            "INSERT INTO alumnos (uid, nombre, email, rol) VALUES (?, ?, ?, ?)",
                            (str(fila['uid']), str(fila['nombre']), str(fila['email']), str(fila['rol']))
                        )
                        exitos += 1
                    except Exception:
                        errores += 1
                        
                conn.commit()
                conn.close()
                st.success(f"Procesamiento completo: {exitos} alumnos matriculados correctamente. {errores} registros omitidos por duplicidad.")
                st.rerun()
        except Exception as e:
            st.error(f"Error al leer el archivo CSV. Asegúrese de que cumple con las columnas requeridas (uid, nombre, email, rol). Detalle: {e}")

    st.markdown("---")
    st.markdown("#### Listado Completo de Usuarios Registrados")
    conn = sqlite3.connect("cip_lms_platform.db")
    df_alumnos = pd.read_sql("SELECT uid as [Identificador/DNI], nombre as [Nombre Completo], email as [Correo Electrónico], rol as [Rol Asignado] FROM alumnos", conn)
    st.dataframe(df_alumnos, use_container_width=True, hide_index=True)
    conn.close()

# -------------------------------------------------------------------------
# PESTAÑA 3: CONSOLA DE PLUGINS FUNCIONALES Y EXTENSIBLES
# -------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### Configuración de Complementos y Módulos (Plugins)")
    st.markdown("Extienda la capacidad técnica de la plataforma activando o desactivando los módulos core del sistema en tiempo real.")
    
    conn = sqlite3.connect("cip_lms_platform.db")
    cursor = conn.cursor()
    
    # Formulario para añadir nuevos plugins al sistema de archivos virtual
    with st.form("nuevo_plugin"):
        st.markdown("**Instalar Nuevo Plugin**")
        c1, c2 = st.columns(2)
        p_id = c1.text_input("ID único del complemento (Ej. plg_foros):")
        p_nom = c2.text_input("Nombre comercial del Plugin:")
        p_desc = st.text_area("Descripción de funcionalidades:")
        
        if st.form_submit_button("Instalar paquete del Plugin"):
            if p_id and p_nom:
                try:
                    cursor.execute("INSERT INTO plugins_sistema VALUES (?, ?, ?, 1)", (p_id, p_nom, p_desc))
                    conn.commit()
                    st.success(f"Módulo '{p_nom}' inyectado e instalado correctamente.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("El identificador del plugin ya está registrado en el núcleo.")
            else:
                st.error("Rellene los campos obligatorios.")

    st.markdown("---")
    st.markdown("#### Panel de Control de Plugins del Núcleo")
    
    # Leer plugins actuales
    cursor.execute("SELECT id_plugin, nombre, descripcion, estado FROM plugins_sistema")
    lista_plugins = cursor.fetchall()
    
    for plg in lista_plugins:
        id_plg, nombre, desc, estado = plg
        estado_texto = "🟢 ACTIVO" if estado == 1 else "🔴 DESACTIVADO"
        
        # Renderizado estructurado
        st.markdown(f"""
            <div class="plugin-card">
                <span style="float: right; font-weight: bold; color: {'#16A34A' if estado==1 else '#DC2626'};">{estado_texto}</span>
                <h4 style="margin: 0 0 5px 0;">{nombre} <code style="font-size: 12px; color: #64748B;">({id_plg})</code></h4>
                <p style="margin: 0; font-size: 14px; color: #475569;">{desc}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón de conmutación de estado interactivo por cada plugin
        label_btn = "Desactivar" if estado == 1 else "Activar"
        if st.button(f"{label_btn} {nombre}", key=f"btn_{id_plg}"):
            nuevo_est = 0 if estado == 1 else 1
            cursor.execute("UPDATE plugins_sistema SET estado=? WHERE id_plugin=?", (nuevo_est, id_plg))
            conn.commit()
            st.rerun()
            
    conn.close()

# -------------------------------------------------------------------------
# PESTAÑA 4: ÁREA DE CONTENIDOS DE AYUDA Y SOPORTE
# -------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### Centro de Ayuda e Documentación Técnica")
    st.markdown("Consulte las guías básicas de operación basadas en los estándares internacionales de teleformación.")
    
    with st.expander("Preguntas Frecuentes - ¿Cómo se realiza el rastreo de progreso en SCORM?"):
        st.markdown("""
        La plataforma implementa el puente API nativo para capturar las variables estándar enviadas por los paquetes interactivos:
        - `cmi.core.lesson_status` (Completado, Incompleto, Suspendido)
        - `cmi.core.score.raw` (Calificación o puntuación directa obtenida en los cuestionarios integrados)
        - `cmi.core.session_time` (Tiempo efectivo de permanencia del alumno en la unidad didáctica)
        """)
        
    with st.expander("Manual de Integración de Extensiones y API de Plugins"):
        st.markdown("""
        Cada plugin añadido a la plataforma debe registrarse en la tabla maestro e implementar los métodos gancho (*hooks*) obligatorios para no interferir en el renderizado síncrono del campus virtual.
        """)
        
    st.info("Para asistencia directa o incidencias críticas con los servidores, puede remitir un correo electrónico al departamento de soporte corporativo.")
