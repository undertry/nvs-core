import csv
import json
import os

# Rutas de los archivos CSV y JSON para las redes WiFi
wifi_csv_file = 'csv/wifi_networks.csv'
wifi_json_file = 'json/wifi_networks.json'

# Rutas de los archivos CSV y JSON para los dispositivos conectados
device_csv_file = 'csv/devices.csv'
device_json_file = 'json/connected_devices.json'

def csv_to_json_wifi(csv_filepath, json_filepath):
    wifi_networks = []

    try:
        # Comprobar si el archivo CSV existe
        if not os.path.exists(csv_filepath):
            print(f"No se encontró el archivo CSV: {csv_filepath}")
            return

        # Leer el archivo CSV
        with open(csv_filepath, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Filtrar y estructurar los datos relevantes
                wifi_network = {
                    "BSSID": row.get("BSSID", "").strip(),
                    "ESSID": row.get("ESSID", "").strip(),
                    "Signal": row.get("Signal", "").strip(),
                    "Channel": row.get("Channel", "").strip(),
                    "Encryption": row.get("Encryption", "").strip()
                }
                wifi_networks.append(wifi_network)

        # Escribir los datos en formato JSON
        with open(json_filepath, mode='w') as json_file:
            json.dump(wifi_networks, json_file, indent=4)

        print(f"Datos de redes WiFi convertidos a JSON y guardados en: {json_filepath}")

    except Exception as e:
        print(f"Error al convertir el CSV a JSON: {e}")

def csv_to_json_devices(csv_filepath, json_filepath):
    devices = []

    try:
        # Comprobar si el archivo CSV existe
        if not os.path.exists(csv_filepath):
            print(f"No se encontró el archivo CSV: {csv_filepath}")
            return

        # Leer el archivo CSV
        with open(csv_filepath, mode='r') as file:
            csv_reader = csv.reader(file)
            capture = False
            for row in csv_reader:
                # Detectar la sección de estaciones conectadas
                if len(row) > 0 and row[0].strip() == 'Station MAC':
                    capture = True
                    continue

                if capture and len(row) > 0 and row[0].strip():  # Si estamos en la sección correcta
                    mac_address = row[0].strip()  # MAC de la estación
                    if mac_address:  # Asegurarse de que haya una MAC
                        device_info = {
                            'station': mac_address,
                            'bssid': row[5].strip()  # o cambiar según cómo aparezca en el CSV
                        }
                        devices.append(device_info)

        # Guardar los datos en formato JSON
        with open(json_filepath, mode='w') as json_file:
            json.dump(devices, json_file, indent=4)

        print(f"Datos de dispositivos conectados convertidos a JSON y guardados en: {json_filepath}")

    except Exception as e:
        print(f"Error al convertir el CSV a JSON: {e}")

if __name__ == "__main__":
    # Convertir el CSV de redes WiFi a JSON
    csv_to_json_wifi(wifi_csv_file, wifi_json_file)

    # Convertir el CSV de dispositivos conectados a JSON
    csv_to_json_devices(device_csv_file, device_json_file)
