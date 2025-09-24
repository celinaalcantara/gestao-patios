import paho.mqtt.client as mqtt
import time
import random
 
# Informações do Broker MQTT
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC_BASE = "patios/filial_A/leitores/"
 
# Informações do Dispositivo
dispositivos = {
    "leitor_1": "corredor_entrada",
    "leitor_2": "corredor_saida",
    "leitor_3": "area_estacionamento"
}
 
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao broker MQTT com sucesso.")
    else:
        print(f"Falha na conexão, código de retorno: {rc}")
 
def run_simulator(device_id, location):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(BROKER_ADDRESS, PORT, 60)
    
    moto_ids = ["moto_123", "moto_456", "moto_789"] # Tags RFID simuladas
    
    while True:
        # simulando a leitura de uma moto (a cada 5-15 segundos)
        moto_id = random.choice(moto_ids)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        payload = f"{moto_id},{device_id},{location},{timestamp}"
        topic = TOPIC_BASE + device_id
        
        print(f"Dispositivo {device_id} publicando no tópico '{topic}': {payload}")
        client.publish(topic, payload)
        
        time.sleep(random.randint(5, 15))
 
if __name__ == "__main__":
    print("Iniciando simulador para o leitor_1...")
    run_simulator("leitor_1", dispositivos["leitor_1"])
 
