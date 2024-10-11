import sys #Para interactuar con el interprete de Python
import getopt #Maneja argumentos de la linea de comandos
import requests #Usada para mostrar mensaje de error en la peticion a la API
import subprocess #Ejecuta comandos del sistema
import re #Usada en la linea 42 para solo tener MAC validas

#Funcion que muestra el mensaje de ayuda
def mostrarAyuda():
    print("Uso: python OUILookup.py --mac <mac> | --arp | [--help]")
    print(" --mac: MAC a consultar. Ej: aa:bb:cc:00:00:00.")
    print(" --arp: Muestra los fabricantes de los hosts disponibles en la tabla arp.")
    print(" --help: Muestra este mensaje y termina.")

#Funcion que consulta el fabricante de una MAC
def consultarFabricante(mac):
    link = f"https://api.maclookup.app/v2/macs/{mac}" #Link de la API con la direccion mac
    try:
        respuesta = requests.get(link) #Envia una peticion a la API
        fabricante = respuesta.json() #Convierte la repuesta a un diccionario 
        
        #Verifica si se encontro el fabricante y muestra la informacion correspondiente (mac/fabricante/tiempo)
        if 'company' in fabricante and fabricante['company']: 
            print(f"MAC address: {mac}")
            print(f"Fabricante: {fabricante['company']}")
        else:
            print(f"MAC address: {mac}")
            print("Fabricante: Not Found") #En caso que no se haya encontado el fabricante
        print(f"Tiempo de respuesta: {respuesta.elapsed.total_seconds() * 1000:.0f} ms")
    except requests.exceptions.RequestException as e:
        print(f"Error en la consulta: {e}")  #Retorna un error


#Funcion para obtener la tabla ARP y consultar los fabricantes
def consultarArp():
    commando = "arp -a" #Se define el comando
    
    try:
        arp = subprocess.check_output(commando, shell=True).decode('cp1252') #Ejecuta el comando arp -a y decodifica la salida
        lineas = arp.splitlines() #Separa la salida en lineas separadas

        mac = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")  #Solo macs validas (12 numeros hexadecimales)
        
        #Revisa cada linea de la salida del comando arp -a
        for linea in lineas:
            igual = mac.search(linea) #Busca si hay una direccion mac valida en la linea actual
            if igual:
               mac_address = igual.group() #Obtiene la direccion mac que se encontro
               consultarFabricante(mac_address)  #Llamamos a la funcion para obtener los fabricantes
    
    except subprocess.CalledProcessError as e:
        print(f"Error al obtener la tabla ARP: {e}")

# Funcion principal, gestiona los argumentos y llama a las funciones 
def main(argv):
    #Verifica que se hayan pasado argumentos
    if len(argv) == 0: 
        mostrarAyuda()
        sys.exit()

    try:
        opts, a = getopt.getopt(argv, "", ["mac=", "arp", "help"]) #Procesa lo argumentos de la linea de comandos
    except getopt.GetoptError: #Arroja errores en el procesamiento de argumentos
        mostrarAyuda()
        sys.exit(2)

    #Las opciones de los argumentos 
    for opt, m in opts:
        if opt == '--help':
            mostrarAyuda()
            sys.exit()
        elif opt == '--mac':
            consultarFabricante(m)
        elif opt == '--arp':
            consultarArp()

if __name__ == "__main__":
    main(sys.argv[1:])



