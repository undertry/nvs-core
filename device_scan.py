import subprocess
import os
import csv
import time
import json  # Asegurarnos de importar json

# Importar las funciones para manejar el modo monitor/managed
from monitor_mode import enable_monitor_mode, disable_monitor_mode

# Función para cargar la duración del escaneo directamente del JSON
def get_scan_duration():
    mode_file = 'json/scan_mode.json'
    if os.path.exists(mode_file):
        with open(mode_file, 'r') as f:
            data = json.load(f)
            return data.get('duration', 30)  # 30 segundos como valor predeterminado
    return 30  # Valor predeterminado si el archivo no existe

# Función para obtener el archivo JSON con el modo seleccionado
def load_scan_mode(json_file='json/scan_mode.json'):
    with open(json_file, 'r') as file:
        mode_data = json.load(file)
    return mode_data.get("mode", "Rápido") # valor por defecto si el modo no esta especificado


# Función para obtener el archivo JSON con la red seleccionada
def load_selected_network(json_file='json/respuesta.json'):
    with open(json_file, 'r') as file:
        selected_network = json.load(file)
    return selected_network

# Función para ejecutar airodump-ng con el BSSID y canal especificados
def run_airodump(bssid, channel, output_file, scan_duration):
    # Eliminar cualquier archivo existente que comience con output_file
    for file in os.listdir('csv'):
        if file.startswith(output_file):
            os.remove(os.path.join('csv', file))

    # Ejecutar el comando airodump-ng con los parámetros especificados
    airodump_command = [
        'sudo', 'airodump-ng', '--bssid', bssid, '--channel', str(channel),
        '--write', os.path.join('csv', output_file), '--output-format', 'csv', 'wlan0mon'
    ]

    print(f"Ejecutando: {' '.join(airodump_command)}")
    # Iniciar el proceso
    process = subprocess.Popen(airodump_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(scan_duration)  # Esperar el tiempo basado en el modo de escaneo
    process.terminate()  # Detener el proceso

    # Capturar la salida y errores
    stdout, stderr = process.communicate()

    # Imprimir cualquier salida estándar y errores
    print(f"Salida estándar:\n{stdout.decode()}")
    print(f"Errores:\n{stderr.decode()}")
    if stderr:
        print(f"Error detectado: {stderr.decode()}")
    else:
        print(f"Escaneo terminado. Archivo CSV generado.")

# Función para encontrar el archivo CSV generado más reciente
def find_latest_csv(output_file_prefix):
    csv_files = [f for f in os.listdir('csv') if f.startswith(output_file_prefix) and f.endswith('.csv')]
    
    if not csv_files:
        print(f"No se encontraron archivos CSV con el prefijo {output_file_prefix}")
        return None
    
    # Ordenar los archivos por el número de sufijo (extraer el número del nombre)
    csv_files.sort(key=lambda x: int(x.split('-')[-1].split('.')[0]), reverse=True)
    
    # Devolver el archivo con el número de sufijo más alto
    return csv_files[0]

# Función para limpiar y renombrar el archivo CSV generado
def clean_and_rename_csv(output_file, clean_csv_file):
    # Buscar el archivo CSV más reciente
    latest_csv = find_latest_csv(output_file)
    
    if latest_csv:
        latest_csv_path = os.path.join('csv', latest_csv)
        # Verificar si el archivo realmente existe antes de renombrarlo
        if os.path.exists(latest_csv_path):
            os.rename(latest_csv_path, clean_csv_file)
            print(f"Archivo CSV renombrado a {clean_csv_file}")
        else:
            print(f"Error: El archivo CSV {latest_csv_path} no fue encontrado tras su creación.")
    else:
        print(f"No se encontró el archivo CSV generado.")

# Función principal
def main():
    # Directorio para almacenar los CSV
    csv_directory = 'csv'
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)

    # Cargar la red seleccionada desde el archivo respuesta.json
    selected_network = load_selected_network()
    print(f"Red seleccionada: {selected_network['essid']} (BSSID: {selected_network['bssid']})")

    # Cargar el modo de escaneo desde el archivo mode.json
    mode = load_scan_mode()
    duration = get_scan_duration()    
    
    print(f"Modo de escaneo seleccionado: {mode} (Duración: {duration} segundos)")

    bssid = selected_network['bssid']
    channel = selected_network['channel']

    # Nombre base para el archivo CSV (sin sufijo numérico)
    csv_file_prefix = 'device'

    # Ejecutar airodump-ng con la duración del modo de escaneo seleccionado
    run_airodump(bssid, channel, csv_file_prefix, duration)

    # Limpiar y renombrar el archivo CSV a 'devices.csv'
    clean_csv_file = os.path.join(csv_directory, 'devices.csv')
    clean_and_rename_csv(csv_file_prefix, clean_csv_file)

    # Restaurar la interfaz a modo gestionado
    try:
        disable_monitor_mode('wlan0')
    except Exception as e:
        print(f"Error al deshabilitar modo monitor: {e}")

if __name__ == "__main__":
    main()
