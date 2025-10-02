import paho.mqtt.client as mqtt
import pandas as pd
import os
import json
import threading
from flask import Flask, send_file, render_template
from flask import jsonify
import requests
import random

# configs gerais
broker_address = "localhost"
port = 1883
topic_subscribe = "patios/filial_A/leitores/#"
data_file = "dados_patios.csv"

class patio_vision_api:
    def __init__(self, api_url):
        self.api_url = api_url
    
    def analyze_location(self, location_id):
        try:
            response = requests.get(f"{self.api_url}/locations/{location_id}")
            response.raise_for_status()  # Lança uma exceção para erros HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"falha ao chamar a api de visão: {e}")
            return None

    def register_moto(self, moto_data):
        try:
            # O endpoint para registrar a moto, conforme a proposta.
            response = requests.post(f"{self.api_url}/moto", json=moto_data)
            response.raise_for_status() # Lança exceção para erros HTTP (4xx ou 5xx)
            print(f"moto {moto_data.get('id')} registrada na api.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"erro ao registrar moto na api: {e}")
            # Se a resposta tiver corpo (ex: erro de validação), podemos imprimi-lo
            print(f"detalhe do erro: {e.response.text if e.response else 'n/a'}")
            return False

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("backend conectado no broker mqtt.")
        client.subscribe(topic_subscribe)
    else:
        print(f"ih, deu ruim pra conectar o backend. código: {reason_code}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    persist_data(payload)

def persist_data(data_string):
    try:
        data = data_string.split(',')
        moto_id = data[0]
        device_id = data[1]
        location = data[2]
        timestamp = data[3]
        final_status = 'NAO_VERIFICADO' # Valor padrão se a API falhar
        
        # Integração com a API de Visão Computacional
        vision_data = patio_api_client.analyze_location(location)
        if vision_data:
            print(f"api de visão respondeu para {location}: {vision_data}")
            vision_status = vision_data.get('status', 'erro')
            # logica para comparar o sensor com a visao
            
            if vision_status == 'ocupada':
                # Se a visão confirma, tentamos registrar a moto na API Java
                moto_payload = {
                    "id": moto_id,
                    "location": location,
                    "timestamp": timestamp
                }
                if patio_api_client.register_moto(moto_payload):
                    final_status = 'OK' # Sensor, visão e registro na API concordam.
                else:
                    final_status = 'ERRO_REGISTRO' # Falha ao fazer o POST para a API.
            elif vision_status == 'livre':
                final_status = 'INCONSISTENTE' # Sensor detectou, mas visão não vê. ALERTA!
            else:
                final_status = 'ERRO_VISAO' # A API retornou algo inesperado.
        
        # cria um dataframe com os novos dados
        new_data = pd.DataFrame([{
            'moto_id': moto_id,
            'device_id': device_id,
            'location': location,
            'timestamp': timestamp,
            'status': final_status
        }])
        
        # carrega os dados que ja existem e adiciona a nova linha
        if os.path.exists(data_file):
            df = pd.read_csv(data_file)
            df = pd.concat([df, new_data], ignore_index=True)
        else:
            df = new_data
        
        df.to_csv(data_file, index=False)
        print(f"dados salvos. última leitura: {moto_id}")
        
    except Exception as e:
        print(f"erro ao processar e salvar os dados: {e}")


# servidor http (flask)
app = Flask(__name__, template_folder='dashboard')

@app.route('/data/status.csv')
def serve_csv():
    if not os.path.exists(data_file):
        return "moto_id,device_id,location,timestamp,status\n"
    return send_file(data_file, mimetype='text/csv', as_attachment=False)

@app.route('/')
def serve_dashboard():
    return render_template('index.html')

# simulador de api (para testes)
@app.route('/mock/locations/<location_id>')
def mock_vision_api(location_id):
    # retorna 'ocupada' ou 'livre' aleatoriamente para forçar testes
    mock_status = random.choice(['ocupada', 'livre'])
    print(f"[mock api] local '{location_id}' consultado. retornando: '{mock_status}'")
    return jsonify({'status': mock_status})

@app.route('/mock/moto', methods=['POST'])
def mock_register_moto():
    # esta rota simula o endpoint de registro da api java.
    # ela apenas confirma o recebimento e retorna sucesso (http 200).
    # isso permite que o status 'ok' seja alcançado.
    print("[mock api] recebido post para registrar moto. retornando sucesso.")
    return jsonify({'message': 'moto registrada com sucesso (mock)'}), 200


def run_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(broker_address, port, 60)
        client.loop_forever()
    except Exception as e:
        print(f"falha ao conectar o cliente mqtt: {e}")

# inicialização
# para testar com a api real, use a primeira linha.
# para testar com o simulador, comente a primeira e descomente a segunda.
# patio_api_client = patio_vision_api("http://localhost:8080/api")
patio_api_client = patio_vision_api("http://127.0.0.1:5000/mock")

if __name__ == "__main__":
    # inicia o cliente mqtt em outra thread pra não travar o servidor web
    mqtt_thread = threading.Thread(target=run_mqtt_client)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    
    print("\nservidor flask no ar. acesse: http://127.0.0.1:5000/")
    app.run(debug=False)

    