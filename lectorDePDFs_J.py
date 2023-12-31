import os
import pdfplumber
import csv
import re
from datetime import datetime
import pandas as pd

# Carpeta que contiene los archivos PDF
#carpeta_raiz = "C:/Users/nacho/Downloads/davud/Autofinal/CORRECCIOES_PREDIOS_ANTES/"
carpeta_raiz = "C:/Users/PORTATIL LENOVO/Downloads/Pruebas_autom/26-12-2023/"


soloPH = True                                      #Poner true si se quieren solo las anotaciones de PH





# Nombre del archivo CSV de salida
if soloPH:
    archivo_csv = carpeta_raiz+"soloPH.csv"
else:
    archivo_csv = carpeta_raiz+"nombres_cedulas.csv"
# Cargar el archivo CSV
df = pd.read_csv('Data_generos.csv', sep=';')


def dividir_nombres(nombre):
    nombres = nombre.split()
    todojunto = ["","","",""]
    conta = 0
    
    i = 0
    while i < len(nombres):
        if nombres[i] in ["DE", "DEL", "LA", "LAS"] and conta < 4:
            if nombres[i+1] in ["DE", "DEL", "LA", "LAS"]:
                todojunto[conta] += nombres[i] + " " + nombres[i + 1] + " " + nombres[i + 2]
                i += 3
            elif i + 1 < len(nombres):
                todojunto[conta] += nombres[i] + " " + nombres[i + 1]
                i += 2
            else:
                todojunto[conta] += nombres[i]
                i += 1
        elif conta < 4:
            todojunto[conta] += nombres[i]
            i += 1
        else:
            todojunto[3] += " " + nombres[i]
            i+=1
        conta += 1
        # else:
        #     break
    #print (todojunto)
    #nameylastname = todojunto.spl
    return todojunto[2], todojunto[3], todojunto[0], todojunto[1]

def dividir_por_delimitadores(delimitadores, texto):
    porc = ""
    for delimitador in delimitadores:
        if delimitador in texto:
            partes = texto.rsplit(delimitador, 1)
            if "X" in delimitador:    
                temporal = texto.split(" X")
            else:
                temporal = partes[1].split(" X")
            
            if "X" in texto:
                if "X" not in delimitador:
                    cedula = temporal[0].strip()
                else:
                    cedula = ""
                #partes[1].split("X")[0].strip()
                try:
                    if "%" in temporal[1] or "/" in temporal[1]:
                        resultado= re.search(r"\b(.*?)[\s%]", temporal[1])
                        if resultado:
                            if "/" in temporal[1]:
                                porc = "=100*"+resultado.group(1)
                            else:
                                porc = resultado.group(1)
                except:
                    print("")            
            else:
                cedula = partes[1].strip()

            return partes[0], cedula,porc
    return texto, "",""

# Listas para almacenar los nombres y cédulas
primer_nombre  = []
segundo_nombre = []
primer_apellido = []
segundo_apellido = []
anotacionesfuera = [
                    "CANCELACION",
                    "PARCIAL",
                    "PARCILA",
                    " PA ",
                    "EMBARGO",
                    "DEMANDA EN PROCESO",
                    "ACLARACION",
                    #"FALSA TRADICION",
                    "ESTA ANOTACION NO TIENE VALIDEZ",
                    "PATRIMONIO DE FAMILIA",
                    "DECLARACION DE MEJORAS",
                    #"ADJUDICACION EN SUCESION",
                    #"PARTE RESTANTE",
                    "SENTENCIA DE REMATE",
                    " LIQUIDACION JUDICIAL",
                    "COMPRAVENTA DERECHOS DE CUOTA",
                    "% (MODO DE ADQUISICION)",
                    "ENAJENAR",
                    "HIPOTECA",  
                    "OFERTA DE COMPRA",   
                    "NUDA PROPIEDAD",        
                    "USUFRUCTO",
                    ]

if not soloPH:
    anotacionessiosi = [
                        # "COMPRAVENTA (MODO DE ADQUISICION)",
                        # "COMPRAVENTA MODALIDAD: (NOVIS)",
                        "COMPRAVENTA",
                        "LOTEO (OTRO)",
                        "CONSTITUCION DE URBANIZACION",
                        "COMPRAVENTA POSESION",
                        "(FALSA",
                        "EQUIVALENTE A UNA 7/8 PARTE",
                        "JUDICIAL DE PERTENENCIA"
                        # 'CONSTITUCION REGLAMENTO'
                        ]
else:
    anotacionessiosi = [
                        'CONSTITUCION REGLAMENTO'
                        ]

conversiones = {
    "HAS": 10000,  # 1 Ha = 10,000 m2
    "HECT": 10000,
    "HTRS": 10000,
    "HTS": 10000,
    "HA": 10000,
    "HECTAREAS": 10000,
    "M2": 1,        # 1 m2 = 1 m2
    "MTS2": 1,
    "METROS2": 1,
    "MTRS2": 1,
    "METROS C":1
}

servidumbres = [
    "Acueducto",
    "Aguas",
    "Aire",
    "Alcantarillado",
    "Energia",
    "Gas",
    "Legal",
    "Luz",
    "Medianeria",
    "Minera",
    "Oleoducto",
    "Transito"
]
servidumbres = [s.upper() for s in servidumbres]

delimitado_cedula = [" CC "," TI ", " NIT. ","(ME X","(MENOR) X"," (MENOR) X", " X", " # "]

count_pdfs = 0
# Itera a través de los archivos PDF en la carpeta
for subdir, _, archivos in os.walk(carpeta_raiz):
    for archivo_pdf in archivos:
        folio = archivo_pdf.split("-")[1].split(" ")[0] if "-" in archivo_pdf and " " in archivo_pdf else None # Obtener el número del nombre del archivo PDF
        if archivo_pdf.endswith(".pdf") and ("J" in archivo_pdf or "j" in archivo_pdf):
            pdf_path = os.path.join(subdir, archivo_pdf)

            with pdfplumber.open(pdf_path) as pdf:
                page = None  # Página actual
                encontrado_x = False  # Indica si se ha encontrado " X "
                encontrado_an = False # Indica si se ha encontrado "ANOTACION"
                encontrado_de = False # Indica si se ha encontrado un "DE:"
                encontrado_nr2 = False # Indica si ya pasó por la anotacion nro 2
                encontrado_nohaymas = False #Cuando solo queda por validar anotacion 1, este está en true
                count_anotacion = 0 # Contador para contar la cantidad de veces que se encuentra la palabra "ANOTACION"
                count_anotacion_nro_1 = 0 # Contador para contar la cantidad de veces que se encuentra la palabra "ANOTACION"
                anot1 = False
                bool_A = True
                numeros_cancelados = []
                nuevos_numeros = []
                numero = 0
                count_nr1_a = 0
                contador = 0
                texto_lineas = []  # Almacena el texto de las líneas relevantes
                nombres = []  # Lista para almacenar los nombres
                cedulas = []  # Lista para almacenar las cédulas
                porcentajes = []    #Lista para almacenar porcentajes
                ph = "NO"
                # if folio == "33226":
                #     print ("Hola")
                tipo_servidumbre = ""
                area_servidumbre = ""
                compraventa = -10000000            #Para agregar una anotacion solo cuando salga esta palabra
                sianotacion = False
                pag_encontrado = ""             #para guardar la página en la que se encontró la anotacion clave
                entrarsiosi = False             #Para cuando quiero que guarde una anotacion si o si
                resultado = False
                n_anotacion = -100000000
                
                # derechoscuota = False           #Para cuando hay derechos de cuota que toca cambiar 
                # nombres_de = []
                # cedulas_de = []
                
                # if folio == '37251':
                #     print ("hola")
                
                for page in reversed(pdf.pages):
                    # Contar cuántas veces aparece "ANOTACION: Nro 1" y "ANOTACION" en todas las líneas
                    lines = page.extract_text().splitlines()
                    for line in lines:
                        if "ANOTACION: Nro" in line:
                            count_anotacion += 1
                            if " Nro 1 " in line:
                                count_anotacion_nro_1 = True
                            # Extraer el número después de "ANOTACION:"
                            anotacion_match = re.search(r'ANOTACION: Nro (\d+)', line)
                            if anotacion_match and n_anotacion < int(anotacion_match.group(1)):
                                n_anotacion = int(anotacion_match.group(1))
                        if count_anotacion_nro_1 and "A:" in line or count_nr1_a == 0 and "DE:" in line:
                            count_nr1_a += 1    
                        if re.search(r"horizontal", line, re.IGNORECASE):
                            ph = "SI"
                        if any(keyword in line for keyword in anotacionessiosi) and (pag_encontrado == page or sianotacion == False):
                            compraventa = int(anotacion_match.group(1))
                            sianotacion = True
                            pag_encontrado = page
                if n_anotacion == compraventa:
                    encontrado_nohaymas = True
                    entrarsiosi = True
                    encontrado_de = True

                # Comprobar si "ANOTACION: Nro 1" se encontró y "ANOTACION" aparece más de una vez
                resultado = count_anotacion_nro_1 == 1 and count_anotacion == 1
                
                A_encontrado = False
                
                for page in reversed(pdf.pages):
                    if encontrado_x and encontrado_an:
                        encontrado_x = False
                        encontrado_an = False
                        break  # Si " X " ya se encontró, detén la iteración
                    lines = page.extract_text().splitlines()                
                    for line in reversed(lines):
                        if "https" in line or "Consultas VUR" in line:  # Ejemplo de condición
                            continue  # Si el número es par, pasa al siguiente número sin ejecutar el código restante
                        
                        # if folio == "100895":
                        #     print ("tons")
                        if "DE:" in line:           #para poder guardar un párrafo solo cuando tenga "DE:"
                            encontrado_de = True
                        elif any(keyword in line for keyword in anotacionesfuera) and ('SANEAMIENTO' not in line) and encontrado_nohaymas == False:      #CANCELACION", "PARCIAL", "EMBARGO", "DEMANDA EN PROCESO", "ACLARACION", "FALSA TRADICION"
                            encontrado_de = False
                        elif "Se cancela anotación No: " in line:
                            # Buscar números después de "No:"
                            nuevos_numeros = [numero.strip() for numero in line.split("No: ")[1].split(",")]
                            if "1" not in nuevos_numeros:
                                numeros_cancelados = numeros_cancelados + nuevos_numeros
                        
                        if ("A:" in line or "DE:" in line) and encontrado_nr2:                            
                            if "A:" in line:
                                A_encontrado = True
                                encontrado_de = True  
                            elif "DE:" in line and A_encontrado == False:
                                encontrado_de = True    
                            else:
                                encontrado_nr2 = False                            
                                
                        elif not ("A:" in line or "DE:" in line) and encontrado_nr2 and encontrado_de:
                            encontrado_nr2 = False

                            
                            # Verificar si existe "ANOTACION: Nro " seguido de los números cancelados
                        for numero in numeros_cancelados:
                            if f"ANOTACION: Nro {numero}" in line:
                                encontrado_de = False
                                break  # Puedes detener la búsqueda una vez que se cumple la condición
                        
                        if resultado: #PARA LOS CASOS EN QUE NO HAYAN MAS ANOTACIONES MAS QUE LA PRIMERA Y ASEGURAR QUE GUARDE ALGUN PROPIETARIO
                            encontrado_nohaymas = True
                            if bool_A and "DE:" in line:
                                anot1 = True
                            elif "A:" in line:
                                bool_A = False

                        if (" X" in line and "A:" in line) or (resultado and "A:" in line) or anot1 or encontrado_nr2 or (entrarsiosi and "A:" in line):# and not encontrado_x:
                            encontrado_x = True
                            #print (line)

                            # TRATAMIENTO DE DATOS PARA LA CÉDULA Y NOMBRE
                            nombre = line[3:]
                            # if folio == '84642':
                            #     print ("CHAO")
                            nombre, cedula, porcens = dividir_por_delimitadores(delimitado_cedula, nombre)
                            if " I" in cedula:
                                cedula = cedula.split(" I")[0]
                            if resultado: #sirve para cuando solo hay una anotación nro 1.
                                contador += 1
                                if count_nr1_a == contador:
                                    resultado = False
                                    anot1 = False
                                    contador = 0
                                    count_nr1_a = 0
                                    encontrado_de = True

                            nombres.append(nombre)
                            cedulas.append(cedula)
                            porcentajes.append(porcens)
                            texto_lineas.insert(0, line)
                        elif encontrado_x and "ANOTACION:" not in line:
                            texto_lineas.insert(0, line)
                            #print ("texto_lineas ->> ",texto_lineas)
                        elif encontrado_x and "ANOTACION:" in line:
                            bool_ph = False
                            
                            if soloPH:
                                phpruebaaa = "\n".join(texto_lineas)                                                                               #temporaaaaaaaal      
                                if "HORIZONTAL" in phpruebaaa:                                                                                      #temporaaaaaaaal
                                    bool_ph = True
                            elif encontrado_de:
                                    bool_ph = True
                            
                            if bool_ph:
                                encontrado_an = True
                                encontrado_de = False
                                entrarsiosi = False
                                texto_lineas.insert(0, line)
                                break
                            else:
                                # if "COMPRAVENTA DERECHOS DE CUOTA" in texto_lineas[1] or "COMPRAVENTA DERECHOS DE CUOTA" in texto_lineas[2]:
                                #     nombres_de_a = nombres
                                #     for lineas in texto_lineas:
                                #         if "DE:" in lineas:
                                #             nombre_de = lineas[3:]
                                #             nombre_de, cedula_de = dividir_por_delimitadores(delimitado_cedula, nombre_de)
                                #             nombres_de.append(nombre_de)
                                        
                                encontrado_x = False
                                nombres = []
                                cedulas = []
                                porcentajes = []
                                texto_lineas = []
                        if "ANOTACION:" in line:
                            encontrado_de = False
                        # if folio == '18623':
                        #     print ("hola")
                        # print (folio)
                        if (" Nro 2 " in line) or (f" Nro {compraventa+1} " in line):
                            encontrado_nr2 = True
                            encontrado_nohaymas = True
                            
                # Combinar nombres y cédulas en una sola celda con saltos de línea
                #print (nombres)
                # nombres_celda = "\n".join(nombres)
                # cedulas_celda = "\n".join(cedulas)
                
                texto_celda = "\n".join(texto_lineas)
                
                if texto_celda != '':
                    # Buscar la primera fecha en formato DD-MM-AAAA
                    date_registro_match = re.search(r'\d{2}-\d{2}-\d{4}', texto_celda)
                    date_registro = date_registro_match.group(0) if date_registro_match else None

                    # Buscar la primera fecha en formato AAAA-MM-DD después del primer salto de línea
                    date_documento_match = re.search(r'del (\d{4}-\d{2}-\d{2}) ', texto_celda,re.IGNORECASE)
                    date_documento = date_documento_match.group(1) if date_documento_match else None
                    # if folio == '84642':
                    #     print ('error fecha->>',folio)
                    date_documento = datetime.strptime(date_documento, "%Y-%m-%d").strftime("%d-%m-%Y")

                    # Buscar la primera palabra después de "Doc: "
                    escritura_match = re.search(r'Doc: (\w+)', texto_celda)
                    escritura = escritura_match.group(1) if escritura_match else None

                    # Buscar el primer número después del primer salto de línea
                    n_escritura_match = re.search(r'(\w+) (.*?) DEL', texto_celda,re.IGNORECASE)
                    n_escritura = n_escritura_match.group(2) if n_escritura_match else None
                        
                    # Buscar la cadena de caracteres entre "00:00:00 " y " VALOR"
                    ente_match = re.search(r':(\d+) (.*?) VALOR', texto_celda,re.IGNORECASE)
                    if ente_match:
                        ente = ente_match.group(2).upper()
                        if "JUZGADO" not in ente:
                            # Divide la cadena en dos partes usando " DE " como delimitador
                            ente_partes = ente.split(" DE ", 1)

                            # Reordena las partes y las une en una sola cadena
                            ente = ente_partes[1] +" "+ ente_partes[0]
                        elif ("PRIMERO" or "SEGUNDO") in ente:
                            ente = ente.replace("PRIMERO", "001")
                            ente = ente.replace("SEGUNDO", "002")
                        else:
                            ente = ente.replace("JUZGADO", "JUZGADO 001")     
                    else:
                        ente = None
                    
                    primer_nombre = []
                    segundo_nombre = []
                    primer_apellido = []
                    segundo_apellido = []
                    genero = []

                    # Dividir nombres en primer nombre, segundo nombre, primer apellido y segundo apellido
                    #print ("nombres_celda-> ",nombres_celda)
                    if nombres != "":
                        i=0
                        while i < len(nombres):
                            pn, sn,pa, sa = dividir_nombres(nombres[i])
                            pn = pn.strip()
                            sn = sn.strip()
                            pa = pa.strip()
                            sa = sa.strip()
                            
                            # if derechoscuota:
                            #     cuenta = 0
                            #     for o in nombres_de:
                            #         if (pn in o or sn in o) and (pa in o or sa in o):
                            #             pn, sn,pa, sa = dividir_nombres(nombres_de_a[cuenta])
                            #             pn = pn.strip()
                            #             sn = sn.strip()
                            #             pa = pa.strip()
                            #             sa = sa.strip()
                            #         cuenta += 1
                                    
                            # Buscar el género correspondiente en el DataFrame
                            #filtro = (df['primernombre'].str.strip() == pn) & (df['segundonombre'].str.strip() == sn)
                            varios_name = False
                            while True:
                                if varios_name == False:
                                    filtro = (df['primernombre'].str.strip() == pn)
                                else:
                                    filtro = (df['primernombre'].str.strip() == sn)
                                resultados = df[filtro]

                                # Verificar si se encontraron coincidencias
                                if not resultados.empty:
                                    genero_encontrado = resultados['sexo'].unique()
                                    if len(genero_encontrado) == 1:
                                        genero.append(genero_encontrado[0])
                                        break
                                    else:
                                        varios_name = True
                                        #genero.append("Nombre ambiguo, revisar")
                                else:
                                    genero.append("No se encontró información de género")
                                    break
                                                                                                                                                                                                                               
                            primer_nombre.append(pn)
                            segundo_nombre.append(sn)
                            primer_apellido.append(pa)
                            segundo_apellido.append(sa) 
                            i += 1
                        
                        if folio == "75811":
                            print ("hola")
                        n_escritura_servidumbre = ""
                        bool_serv = False
                        cadena_spec = ""
                        for page in reversed(pdf.pages):
                            # Contar cuántas veces aparece "ANOTACION: Nro 1" y "ANOTACION" en todas las líneas
                            lines = page.extract_text().splitlines()
                            for line in reversed(lines):
                                for i in range(len(primer_nombre)):
                                    cadenas = [primer_nombre[i], segundo_nombre[i], primer_apellido[i], segundo_apellido[i]]
                                    # Recorres la lista y reemplazas cadenas vacías por 'abcd'
                                    for j in range(4):
                                        if cadenas[j] == '':
                                            cadenas[j] = 'abcd'
                                        if "\\" in cadenas[j] or '/' in cadenas[j]:
                                            cadenas[j] = cadenas[j].replace('\\', 'Ñ')
                                            cadenas[j] = cadenas[j].replace('/', 'Ñ')

                                    if (cadenas[0] in line or " "+cadenas[1] in line) and (cadenas[2] in line or " "+cadenas[3] in line):
                                        # Buscar cualquier número con más de dos dígitos en la línea
                                        matches2 = re.findall(r'\b\d{3,}\b', line)
                                        if matches2 and cedulas[i] == "":
                                            cedulas[i] = matches2[0]  # Asignar el primer número de más de dos dígitos como cédula 
                                            matches2 = []  
                        
                        
                            
                        for page in pdf.pages:
                            # Contar cuántas veces aparece "ANOTACION: Nro 1" y "ANOTACION" en todas las líneas
                            lines = page.extract_text().splitlines()
                            count_serv = 0
                            for line in lines:
                                if not bool_serv:
                                    if "Doc: ESCRITURA" in line:
                                        escrotura_match = re.search(r'ESCRITURA(.*?)(\d+):', line)
                                        n_escrotora = escrotura_match.group(1).strip() if escrotura_match else None
                                    if re.search(r"ESPECIFICACION: (\d+) SERVIDUMBRE", line, re.IGNORECASE):
                                        coincidencias = []
                                        bool_found = False
                                        if n_escrotora == "1237 del 2020-10-13":
                                            print ("")
                                        clean = re.sub(r'[.,()\s]+', ' ', line)
                                        tipo_servidumbre_match = re.search(r'ESPECIFICACION: (\d+) SERVIDUMBRE\s+(\w+(?:\s+\w+){0,4})(?:\s+\([\w\s]+\))?', clean)                                  
                                        if tipo_servidumbre_match and tipo_servidumbre_match.group(2).strip():
                                            bool_found = True
                                        else:
                                            tipo_servidumbre_match = re.search(r'ESPECIFICACION: (\d+) SERVIDUMBRE\s+(\w+(?:\s+\w+)?)(?:\s+\([\w\s]+\))?', clean)
                                            if tipo_servidumbre_match and tipo_servidumbre_match.group(2).strip():
                                                bool_found = True
                                            else:
                                                tipo_servidumbre + "ACUEDUCTO" +"\n"

                                        if bool_found:                                         
                                            # Dividir la cadena en palabras
                                            palabras = tipo_servidumbre_match.group(2).strip().split()

                                            # Iterar sobre las palabras y verificar si coinciden con las de la lista
                                            for palabra in palabras:
                                                for servi in servidumbres:
                                                    if servi in palabra:
                                                        if servi == "GAS":
                                                            coincidencias.append("GASODUCTO")    
                                                        else:
                                                            coincidencias.append(servi)
                                            # Crear una variable nueva concatenando las palabras coincidentes
                                            nueva_variable = " Y ".join(coincidencias)
                                            tipo_servidumbre = tipo_servidumbre + nueva_variable +"\n"  
                                        
                                        n_escritura_servidumbre = n_escritura_servidumbre + n_escrotora + "\n"  
                                        bool_serv = True
                                        cadena_spec = line
                                elif "PERSONAS QUE INTERVIENEN" not in line:
                                    if "https" not in line or "Consultas VUR" not in line:
                                        cadena_spec = cadena_spec + " "+ line
                                else:
                                    bool_serv = False
                                    cadena = re.sub(r'\([^)]*\)', '', cadena_spec)
                                    total_m2 = None
                                    valor = None
                                    cadena_limpia = re.sub(r'\([^)]*\)', '', cadena)
                                    palabras = cadena_limpia.split()
                                    cadena_limpia = ' '.join(palabras[-5:])

                                    # Buscar las unidades de medida y sus valores numéricos                                                                                                            
                                    matches = re.findall(r'\b(\d{4,}(?:[\.,]\d+)?|\d{1,3}(?:[.,]\d{3})*(?:[.,]?\d+)?)\s*(\w+)?\b', cadena_limpia)

                                    for match in matches:
                                        valor, unidad = match

                                        # Determinar si el número debe ser tratado como decimal o número de miles
                                        if ',' in valor and '.' in valor:
                                            valor = valor.replace('.', '') 
                                        elif valor.count('.') > 1:
                                            partes = valor.rsplit('.', 1)  # Dividir la cadena en dos partes desde el último punto
                                            if len(partes[-1]) < 3:  # Si los últimos dígitos después del último punto son menos de 3
                                                valor = partes[0].replace('.', '') + '.' + partes[-1]  # Mantener solo el punto que separa la parte decimal
                                        
                                        # if folio == '17649':
                                        #     print ('')
                                        
                                        if ',' in valor:
                                            valor = valor.replace(',', '.')  # Reemplazar coma por punto para tratar como número decimal
                                        elif '.' in valor and len(valor.split('.')[-1]) == 3:
                                            valor = valor.replace('.', '')  # Tratar como número de miles si tiene tres dígitos después del punto

                                        if unidad in conversiones:
                                            valor_m2 = float(valor) * conversiones[unidad]
                                            # print ('')
                                            if total_m2 is None:
                                                total_m2 = valor_m2
                                            else:
                                                total_m2 += valor_m2
                                                break  # Romper el bucle si ya se encontró el valor total en m2
                                            if unidad == "M2" or unidad in "MTS2":
                                                break
                                    if total_m2 != None: 
                                        area_servidumbre = area_servidumbre + str(total_m2) + "\n"
                                    else:
                                        area_servidumbre = area_servidumbre + "NO" + "\n"
                                count_serv += 1
                        
                        
                else:
                    ph = 'COLOCAR DATOS MANUALMENTE'

                # Guardar los datos en el archivo CSV si se encontró " X "
                with open(archivo_csv, "a", newline="", encoding="utf-8") as csv_file:
                    csv_writer = csv.writer(csv_file)

                    # Agregar encabezados si el archivo está vacío
                    if os.path.getsize(archivo_csv) == 0:
                        csv_writer.writerow(["Nombre de archivo","Folio", "Servidumbre","Escr. Serv","Area Serv", "PH","Texto", "Fecha registro","Fecha documento","Fuente adm.","N. Fuente","Ente Em.","Porcentajes","Cédulas", "Primer Nombre", "Segundo Nombre", "Primer Apellido", "Segundo Apellido","Género"])
                    
                    if primer_nombre == []:
                        print ("No hay nadaaaaaaa, archivo: ", archivo_pdf)
                    
                    # Agregar los datos del archivo PDF actual
                    i = 0
                    if len(nombres) == 0:
                        print("No se agregó foliooooo: ",folio)
                    else:
                        count_pdfs += 1
                    while i < len(nombres):
                        if i == 0:
                            csv_writer.writerow([archivo_pdf,folio, tipo_servidumbre,n_escritura_servidumbre, area_servidumbre, ph, texto_celda,date_registro,date_documento,escritura,n_escritura,ente,porcentajes[i], cedulas[i], primer_nombre[i], segundo_nombre[i], primer_apellido[i], segundo_apellido[i],genero[i]])
                        else:
                            csv_writer.writerow(["", folio,"","","","", "","","","", "","",porcentajes[i],cedulas[i], primer_nombre[i], segundo_nombre[i], primer_apellido[i], segundo_apellido[i],genero[i]])
                        i += 1

                # Limpiar las listas para el próximo archivo PDF
                nombres.clear()
                cedulas.clear()
                porcentajes.clear()
                texto_lineas.clear()

print(f"Se ha analizado y guardado la información en {archivo_csv} de {count_pdfs} PDFs")
