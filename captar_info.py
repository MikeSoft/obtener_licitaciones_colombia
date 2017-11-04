# -*- coding: utf-8 -*-
# Mike Brian Olivera
import sqlite3
import requests
import sys
from datetime import date
import re
import unidecode
reload(sys)
sys.setdefaultencoding('utf-8')
from xml.dom.minidom import parseString
from ciudad import get_municipio

conn = sqlite3.connect('database.db')
conn.text_factory = str
c = conn.cursor()
c.execute(
    "CREATE TABLE IF NOT EXISTS licitaciones (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,"
    "departamento TEXT NOT NULL ,municipio TEXT NOT NULL,"
    "titulo TEXT NOT NULL ,descripcion TEXT NOT NULL ,link TEXT NOT NULL ,author TEXT NOT NULL ,"
    " entidad TEXT NULL,precio_estimado INTEGER NULL,fecha DATE NOT NULL,categoria TEXT NOT NULL,subcategoria TEXT NOT NULL,descripcion_filtrado TEXT,UNIQUE(link) );"
)

c.execute("CREATE TABLE IF NOT EXISTS errores (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,tipo TEXT NOT NULL ,descripcion TEXT NOT NULL ,info TEXT NOT NULL );")

'''
CREATE TABLE licitaciones (
	id INTEGER PRIMARY KEY AUTOINCREMENT   NOT NULL ,
	titulo TEXT NOT NULL ,
	descripcion TEXT NOT NULL ,
	fecha DATE NOT NULL ,
	link TEXT NOT NULL ,
	author TEXT NOT NULL ,
	departamento TEXT NOT NULL ,
	municipio TEXT NOT NULL ,
	entidad TEXT NULL ,
	precio_estimado INTEGER NULL ,
	categoria TEXT NOT NULL,
	subcategoria TEXT NOT NULL,
	descripcion_filtrado TEXT,
	UNIQUE(link)
);

CREATE TABLE errores (
	id INTEGER PRIMARY KEY AUTOINCREMENT   NOT NULL ,
	tipo TEXT NOT NULL ,
	descripcion TEXT NOT NULL ,
	info TEXT NOT NULL 
);
'''




# A Material Vivo Animal y Vegetal
# B. Materias Primas
# C. Maquinaria, Herramientas, Equipo Industrial y Vehículos
# D. Componentes y Suministros
# E. Productos de Uso Final
# F. Servicios
# G. Terrenos, Edificios, Estructuras y Vías

RSS = [
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-10000000.xml", "cat": "A", "subcat":"Material vivo vegetal y animal, accesorios y suministros"},
	
	{"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-11000000.xml", "cat": "B", "subcat":"Material mineral, textil y vegetal y animal no comestible"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-12000000.xml", "cat": "B", "subcat":"Material químico incluyendo bioquímicos y materiales de gas"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-13000000.xml", "cat": "B", "subcat":"Materiales de resina, colofonia, caucho, espuma, película y elastómericos"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-14000000.xml", "cat": "B", "subcat":"Materiales y productos de papel"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-15000000.xml", "cat": "B", "subcat":"Materiales combustibles, aditivos para combustibles, lubricantes y anticorrosivos"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-20000000.xml", "cat": "C", "subcat":"Maquinaria y accesorios de minería y perforación de pozos"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-21000000.xml", "cat": "C", "subcat":"Maquinaria y accesorios para agricultura, pesca, silvicultura y fauna"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-22000000.xml", "cat": "C", "subcat":"Maquinaria y accesorios para construcción y edificación"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-23000000.xml", "cat": "C", "subcat":"Maquinaria y accesorios para manufactura y procesamiento industrial"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-24000000.xml", "cat": "C", "subcat":"Maquinaria, accesorios y suministros para manejo, acondicionamiento y almacenamiento de materiales"},
	{"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-25000000.xml", "cat": "C", "subcat":"Vehículos comerciales, militares y particulares, accesorios y componentes"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-26000000.xml", "cat": "C", "subcat":"Maquinaria y accesorios para generación y distribución de energía"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-27000000.xml", "cat": "C", "subcat":"Herramientas y maquinaria general"},
	
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-30000000.xml", "cat": "D", "subcat":"Componentes y suministros para estructuras, edificación, construcción y obras civiles"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-31000000.xml", "cat": "D", "subcat":"Componentes y suministros de manufactura"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-32000000.xml", "cat": "D", "subcat":"Componentes y suministros electrónicos"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-39000000.xml", "cat": "D", "subcat":"Componentes, accesorios y suministros de sistemas eléctricos e iluminación"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-40000000.xml", "cat": "D", "subcat":"Componentes y equipos para distribución y sistemas de acondicionamiento"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-41000000.xml", "cat": "D", "subcat":"Equipos y suministros de laboratorio, de medición, de observación y de pruebas"},
	
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-42000000.xml", "cat": "E", "subcat":"Equipo Médico, accesorios y suministros"},
	{"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-43000000.xml", "cat": "E", "subcat":"Difusión de tecnologías de información y telecomunicaciones"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-44000000.xml", "cat": "E", "subcat":"Equipos de oficina, accesorios y suministros"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-45000000.xml", "cat": "E", "subcat":"Equipos y suministros para impresión, fotografía y audiovisuales"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-46000000.xml", "cat": "E", "subcat":"Equipos y suministros de defensa, orden público, protección, vigilancia y seguridad"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-47000000.xml", "cat": "E", "subcat":"Equipos y suministros para limpieza"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-48000000.xml", "cat": "E", "subcat":"Maquinaria, equipo y suministros para la industria de servicios"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-49000000.xml", "cat": "E", "subcat":"Equipos, suministros y accesorios para deportes y recreación"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-50000000.xml", "cat": "E", "subcat":"Alimentos, bebidas y tabaco"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-51000000.xml", "cat": "E", "subcat":"Medicamentos y productos farmacéuticos"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-52000000.xml", "cat": "E", "subcat":"Artículos domésticos, suministros y productos electrónicos de consumo"},
	{"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-53000000.xml", "cat": "E", "subcat":"Ropa, maletas y productos de aseo personal"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-54000000.xml", "cat": "E", "subcat":"Productos para relojería, joyería y piedras preciosas"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-55000000.xml", "cat": "E", "subcat":"Publicaciones impresas, publicaciones electrónicas y accesorios"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-56000000.xml", "cat": "E", "subcat":"Muebles, mobiliario y decoración"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-60000000.xml", "cat": "E", "subcat":"Instrumentos musicales, juegos, juguetes, artes, artesanías y equipo educativo, materiales, accesorios y suministros"},
	
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-70000000.xml", "cat": "F", "subcat":"Servicios de contratación agrícola, pesquera, forestal y de fauna"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-71000000.xml", "cat": "F", "subcat":"Servicios de minería, petróleo y gas"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-72000000.xml", "cat": "F", "subcat":"Servicios de edificación, construcción de instalaciones y mantenimiento"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-73000000.xml", "cat": "F", "subcat":"Servicios de producción industrial y manufactura"},
	{"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-76000000.xml", "cat": "F", "subcat":"Servicios de limpieza, descontaminación y tratamiento de residuos"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-77000000.xml", "cat": "F", "subcat":"Servicios medioambientales"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-78000000.xml", "cat": "F", "subcat":"Servicios de transporte, almacenaje y correo"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-80000000.xml", "cat": "F", "subcat":"Servicios de gestón, servicios profesionales de empresa y servicios administrativos"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-81000000.xml", "cat": "F", "subcat":"Servicios basados en ingeniería, investigación y tecnología"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-82000000.xml", "cat": "F", "subcat":"Servicios editoriales, de diseño, de artes gráficas y bellas artes"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-83000000.xml", "cat": "F", "subcat":"Servicios públicos y servicios relacionados con el sector público"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-84000000.xml", "cat": "F", "subcat":"Servicios financieros y de seguros"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-85000000.xml", "cat": "F", "subcat":"Servicios de salud"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-86000000.xml", "cat": "F", "subcat":"Servicios educativos y de formación"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-90000000.xml", "cat": "F", "subcat":"Servicios de viajes, alimentación, alojamiento y entretenimiento"},
	{"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-91000000.xml", "cat": "F", "subcat":"Servicios personales y domésticos"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-92000000.xml", "cat": "F", "subcat":"Servicios de defensa nacional, orden público, seguridad y vigilancia"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-93000000.xml", "cat": "F", "subcat":"Servicios políticos y de asuntos cívicos"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-94000000.xml", "cat": "F", "subcat":"Organizaciones y clubes"},
	
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-95000000.xml", "cat": "G", "subcat":"Terrenos, edificios, estructuras y vías"},
]



def replaceIgnoreCase(real_text ,old_text, new_text):
    redata = re.compile(re.escape(old_text), re.IGNORECASE)
    return redata.sub(new_text, real_text)

def get_entidad(entidad,departamento, municipio):
    partes = [unidecode.unidecode(x.strip()) for x in entidad.split("-")]
    posibles = []
    #print partes
    for parte in partes:
        parte = unidecode.unidecode(parte)
        part = replaceIgnoreCase(parte,departamento,"")
        part = replaceIgnoreCase(part, municipio, "")
        if part not in "":
            posibles.append(parte.encode("utf8"))

    if len(posibles)== 0:
        return municipio.encode("utf8")
    elif len(posibles) == 1:
        return unicode(posibles[0]).encode("utf8")
    else:
        return " - ".join(posibles).encode("utf8")


today = date.today()
contador = 0
def item2db(item, categoria, subcategoria):
	try:
		titulo = unicode(item.getElementsByTagName("title")[0].childNodes[0].data)
		titulo = "Proceso "+titulo[11:]
		descripcion = item.getElementsByTagName("description")[0].childNodes[0].data
		
		link = item.getElementsByTagName("link")[0].childNodes[0].data

		author = item.getElementsByTagName("author")[0].childNodes[0].data
		author = author.replace(" ", "")
		
		departamento = item.getElementsByTagName("category")[0].childNodes[0].data
		departamento = unidecode.unidecode(departamento)
		
		pos_end_entidad = item.getElementsByTagName("description")[0].childNodes[0].data.index("</strong>")
		entidad = descripcion[8:pos_end_entidad]
		
		municipio = get_municipio(entidad)
		if type(municipio) is not str:
			return
		entidad = get_entidad(entidad, departamento, municipio)

		
		pos_end_entidad += 9
		post_start_precio_estimado = descripcion.index("<strong>", pos_end_entidad) + 8 + 17

		precio_estimado = descripcion[post_start_precio_estimado:-9]
		precio_estimado = int(precio_estimado.replace(",",""))

		titulo = unidecode.unidecode(titulo)
		
		municipio = unidecode.unidecode(municipio)
		
		
		descripcion = unidecode.unidecode(descripcion)
		
		BR = descripcion.index("<br/>")+5
		descripcion_filtrado =  descripcion[BR:]
		descripcion_filtrado = descripcion_filtrado[:descripcion_filtrado.index("<br />")]
		
		elementos_sql = (titulo, descripcion, link, author, departamento, municipio, entidad, precio_estimado,today,categoria,subcategoria,descripcion_filtrado)
		
		
		sql = 'INSERT INTO licitaciones(titulo,descripcion,link,author,departamento,municipio,entidad,precio_estimado,fecha,categoria,subcategoria,descripcion_filtrado) values(?,?,?,?,?,?,?,?,?,?,?,?)'
		c.execute(sql,elementos_sql)
		conn.commit()
		global contador
		contador = contador + 1
	except sqlite3.IntegrityError:
		pass
	except Exception as ex:
		tipo = str(type(ex).__name__)
		descripcion = str(ex.args)
		data = link
		sql = "INSERT INTO errores(tipo, descripcion,info) values(?,?,?)"
		c.execute(sql,(tipo,descripcion,data))
		print tipo+":> " + descripcion


def makepeticion(elemento):
    try:
        R = requests.get(elemento["url"])
        XML = parseString(R.content).documentElement

        for item in XML.getElementsByTagName("item"):
            item2db(item, elemento["cat"],elemento["subcat"])

    except requests.exceptions.RequestException as e:
        print "Error con la conexion a internet"
        sys.exit(1)


def main():

    for rss in RSS:
        makepeticion(rss)
    print  contador," licitaciones nuevas agregadas"

if __name__ == "__main__":
    main()
