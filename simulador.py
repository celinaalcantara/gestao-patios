import paho.mqtt.client as mqtt
import time
import random
import sys

BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC_BASE = "patios/filial_A/leitores/"

DISPOSITIVOS = {
    "leitor_1": "corredor_entrada",
    "leitor_2": "corredor_saida",
    "leitor_3": "area_estacionamento"
}

MOTO_IDS = ["moto_123", "moto_456", "moto_789", "moto_010"] # Tags RFID simuladas

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[{client._client_id.decode()}] Conectado ao broker MQTT com sucesso.")
    else:
        print(f"Falha na conexão, código de retorno: {reason_code}")

def run_simulator(device_id, location):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"Simulador_{device_id}".encode())
    
    client.on_connect = on_connect
    
    client.reconnect_delay_set(min_delay=1, max_delay=120)
    
    try:
        client.connect(BROKER_ADDRESS, PORT, 60)
    except Exception as e:
        print(f"Erro ao conectar o simulador {device_id}: {e}")
        return

    client.loop_start()
    
    while True:
        moto_id = random.choice(MOTO_IDS)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        payload = f"{moto_id},{device_id},{location},{timestamp}"
        topic = TOPIC_BASE + device_id
        
        result = client.publish(topic, payload)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[{device_id}] Publicando no tópico '{topic}': {payload}")
        else:
            print(f"[{device_id}] FALHA ao publicar mensagem. Código: {result.rc}")
        time.sleep(random.randint(5, 15))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python simulador.py [leitor_id]")
        print("Ex: python simulador.py leitor_1")
        sys.exit(1)
        
    device_id = sys.argv[1] # Captura o argumento da linha de comando
    
    if device_id in DISPOSITIVOS:
        location = DISPOSITIVOS[device_id]
        print(f"Iniciando simulador para o dispositivo: {device_id} ({location})")
        
        run_simulator(device_id, location)
    else:
        print(f"ERRO: ID de leitor '{device_id}' não é válido. Use: leitor_1, leitor_2, ou leitor_3.")
        sys.exit(1)