import json
import subprocess
import re

# Función para leer el archivo matched_devices.json
def read_matched_devices(file_path='json/matched_devices.json'):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            if not data:
                print(f"Advertencia: {file_path} está vacío.")
            return data
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}.")
        return []

# Función para ejecutar un escaneo simple con nmap
def nmap_scan(ip):
    command = ['nmap', '-sV', '-O', '-A', '-p-', '-Pn', '-d', '--script', 'vuln', '--min-rate', '5000', '-n', '--open', ip]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar nmap: {e}")
        return ""

# Función para analizar la salida de nmap y extraer puertos, servicios, sistema operativo y vulnerabilidades
def parse_nmap_output(nmap_output):
    parsed_data = {
        'ports_services': [],
        'os_info': None
    }
    
    current_port = None  # Variable para llevar el seguimiento del puerto actual
    current_service = None

    # Imprimir la salida de Nmap para depurar
    print("Salida cruda de Nmap:\n", nmap_output)

    if not nmap_output.strip():
        print("Advertencia: La salida de Nmap está vacía.")
        return parsed_data

    for line in nmap_output.splitlines():
        if '/tcp' in line or '/udp' in line:  # Detecta líneas con puertos
            parts = line.split()
            port_service = {
                'port': parts[0],      # El puerto y protocolo (ej. 80/tcp)
                'state': parts[1],     # Estado del puerto (open, closed, etc.)
                'service': ' '.join(parts[2:]),  # Nombre del servicio
                'vulnerabilities': []  # Inicializar lista de vulnerabilidades para este puerto
            }
            parsed_data['ports_services'].append(port_service)
            current_port = port_service  # Actualizar el puerto y servicio actual
        elif 'OS details' in line or 'Running' in line:  # Detecta detalles del sistema operativo
            parsed_data['os_info'] = line.split(':', 1)[1].strip() if ':' in line else line.strip()
        elif 'CVE-' in line:  # Detecta vulnerabilidades con CVE
            cve_match = re.search(r'(CVE-\d{4}-\d+)', line)
            if cve_match and current_port:
                cve_id = cve_match.group(1)
                vuln_desc = line.split(':', 1)[1].strip() if ':' in line else line.strip()
                current_port['vulnerabilities'].append({
                    'cve': cve_id,
                    'description': vuln_desc
                })
        elif 'VULNERABLE' in line and current_port:  # Detecta descripciones generales de vulnerabilidades
            vuln_desc = line.strip()
            current_port['vulnerabilities'].append({
                'cve': None,
                'description': vuln_desc
            })

    return parsed_data

# Función principal
def main():
    matched_devices = read_matched_devices()
    if not matched_devices:
        print("No se encontraron dispositivos para escanear.")
        return

    scan_results = []

    for device in matched_devices:
        ip = device.get('ip_address')  # Usar 'ip_address' del JSON
        if ip:
            print(f"Escaneando {ip} con nmap...")
            nmap_output = nmap_scan(ip)
            if nmap_output:
                parsed_data = parse_nmap_output(nmap_output)
                scan_results.append({
                    'ip': ip,
                    'mac': device.get('mac_address'),  # Usar 'mac_address' del JSON
                    'ports_services': parsed_data['ports_services'],
                    'os_info': parsed_data['os_info']
                })
            else:
                print(f"Advertencia: No se obtuvieron resultados para {ip}.")

    # Guardar resultados en un archivo JSON
    if scan_results:
        with open('json/nmap_scan_results.json', 'w') as json_file:
            json.dump(scan_results, json_file, indent=4)
        print("Escaneo completado. Resultados guardados en 'nmap_scan_results.json'.")
    else:
        print("No se generaron resultados de escaneo.")

if __name__ == '__main__':
    main()
