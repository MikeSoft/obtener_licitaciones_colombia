# k3sos
import sqlite3
import requests
import sys
from datetime import date
import re
import unidecode
reload(sys)
sys.setdefaultencoding('utf-8')
from xml.dom.minidom import parseString

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute(
    "CREATE TABLE IF NOT EXISTS licitaciones (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,"
    "titulo TEXT NOT NULL ,descripcion TEXT NOT NULL ,link TEXT NOT NULL ,author TEXT NOT NULL ,"
    "departamento TEXT NOT NULL ,municipio TEXT NOT NULL,"
    " entidad TEXT NULL,precio_estimado INTEGER NULL,fecha DATE NOT NULL,UNIQUE(link) );"
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
	UNIQUE(link)
);

CREATE TABLE errores (
	id INTEGER PRIMARY KEY AUTOINCREMENT   NOT NULL ,
	tipo TEXT NOT NULL ,
	descripcion TEXT NOT NULL ,
	info TEXT NOT NULL 
);
'''

today = date.today()
contador = 0



RSS = [
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Amazonas.xml", "dept": "Amazonas"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Antioquia.xml", "dept": "Antioquia"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Arauca.xml", "dept": "Arauca"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Atlantico.xml", "dept": "Atlantico"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-BogotaDC.xml", "dept": "BogotaDC"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Bolivar.xml", "dept": "Bolivar"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Boyaca.xml", "dept": "Boyaca"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Caldas.xml", "dept": "Caldas"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Caqueta.xml", "dept": "Caqueta"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Casanare.xml", "dept": "Casanare"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Cauca.xml", "dept": "Cauca"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Cesar.xml", "dept": "Cesar"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Choco.xml", "dept": "Choco"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Cordoba.xml", "dept": "Cordoba"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Cundinamarca.xml",
     "dept": "Cundinamarca"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Guainia.xml", "dept": "Guainia"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Guaviare.xml", "dept": "Guaviare"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Huila.xml", "dept": "Huila"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-LaGuajira.xml", "dept": "La Guajira"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Magdalena.xml", "dept": "Magdalena"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Meta.xml", "dept": "Meta"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Narino.xml", "dept": "Narino"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-NorteDeSantander.xml",
     "dept": "Norde de Santander"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Putumayo.xml", "dept": "Putumayo"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Quindio.xml", "dept": "Quindio"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Risaralda.xml", "dept": "Risaralda"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Santander.xml", "dept": "Santander"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Sucre.xml", "dept": "Sucre"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-SanAndresProvidenciaySantaCatalina.xml",
     "dept": "Islas"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Tolima.xml", "dept": "Tolima"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-ValledelCauca.xml",
     "dept": "Valle del Cauca"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Vaupes.xml", "dept": "Vaupes"},
    {"url": "https://www.contratos.gov.co/Archivos/RSSFolder/RSSFiles/rssFeed-Vichada.xml", "dept": "Vichada"}
]

def replaceIgnoreCase(real_text ,old_text, new_text):
    redata = re.compile(re.escape(old_text), re.IGNORECASE)
    return redata.sub(new_text, real_text)

def get_entidad(entidad,departamento, municipio):
    partes = [unicode(x.strip()) for x in entidad.split("-")]
    municipio = unidecode.unidecode(municipio)
    departamento = unidecode.unidecode(departamento)
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



def item2db(item, departamento):
    try:
        titulo = unicode(item.getElementsByTagName("title")[0].childNodes[0].data)
        titulo = "Proceso "+titulo[11:]
        descripcion = item.getElementsByTagName("description")[0].childNodes[0].data

        link = item.getElementsByTagName("link")[0].childNodes[0].data

        author = item.getElementsByTagName("author")[0].childNodes[0].data
        author = author.replace(" ", "")

        municipio = item.getElementsByTagName("category")[0].childNodes[0].data

        pos_end_entidad = item.getElementsByTagName("description")[0].childNodes[0].data.index("</strong>")
        entidad = descripcion[8:pos_end_entidad]
        entidad = get_entidad(entidad, departamento, municipio)

        '''
        f = open("entidades.txt","a")
        #f.write(unicode(entidad)+","+unicode(departamento)+","+unicode(municipio)+"\n")
        f.write(entidad)
        f.close()
        '''


        pos_end_entidad += 9
        post_start_precio_estimado = descripcion.index("<strong>", pos_end_entidad) + 8 + 17

        precio_estimado = descripcion[post_start_precio_estimado:-9]
        precio_estimado = int(precio_estimado.replace(",",""))

        titulo = unidecode.unidecode(titulo)
        descripcion = unidecode.unidecode(descripcion)
        municipio = unidecode.unidecode(municipio)




        sql = 'INSERT INTO licitaciones(titulo,descripcion,link,author,departamento,municipio,entidad,precio_estimado,fecha) values(?,?,?,?,?,?,?,?,?)'
        c.execute(sql,(titulo, descripcion, link, author, departamento, municipio, entidad, precio_estimado,today))
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
        print tipo+": " + descripcion


def makepeticion(elemento):
    try:
        R = requests.get(elemento["url"])
        XML = parseString(R.content).documentElement

        for item in XML.getElementsByTagName("item"):
            item2db(item, elemento["dept"])

    except requests.exceptions.RequestException as e:
        print "Error con la conexion a internet"
        sys.exit(1)


def main():

    for rss in RSS:
        makepeticion(rss)
    print  contador," licitaciones nuevas agregadas"

if __name__ == "__main__":
    main()
