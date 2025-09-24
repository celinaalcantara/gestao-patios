import paho.mqtt.client as mqtt
import pandas as pd
import os
 
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC_SUBSCRIBE = "patios/filial_A/leitores/#"
 
DATA_FILE = "dados_patios.csv"
 
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Backend conectado ao broker MQTT com sucesso.")
        client.subscribe(TOPIC_SUBSCRIBE)
    else:
        print(f"Falha na conexão do backend, código de retorno: {rc}")
 
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(f"Mensagem recebida do tópico '{msg.topic}': {payload}")
    
    persist_data(payload)
 
def persist_data(data_string):
    try:
        moto_id, device_id, location, timestamp = data_string.split(',')
        
        new_data = pd.DataFrame([{
            'moto_id': moto_id,
            'device_id': device_id,
            'location': location,
            'timestamp': timestamp
        }])
        
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = pd.concat([df, new_data], ignore_index=True)
        else:
            df = new_data
        
        df.to_csv(DATA_FILE, index=False)
        print("Dados persistidos com sucesso.")
        
    except Exception as e:
        print(f"Erro ao processar e persistir os dados: {e}")
 
if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(BROKER_ADDRESS, PORT, 60)
    
    client.loop_forever()