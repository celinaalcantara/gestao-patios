# Mapeamento Inteligente do Pátio Mottu

Este projeto é um protótipo para um sistema de gerenciamento de pátio que utiliza IoT para rastrear a localização de motos em tempo real.

## Descrição

A solução simula sensores RFID (leitores) posicionados em áreas estratégicas de um pátio. Quando uma moto passa por um leitor, uma mensagem é enviada via MQTT para um backend central.

O backend processa essa informação, valida com uma API externa (simulando um sistema de visão computacional) e persiste o status do evento. Um dashboard web exibe todas as leituras em tempo real, destacando inconsistências para que um operador possa tomar uma ação.

## Tecnologias Utilizadas

*   **Backend**: Python, Flask, Paho-MQTT, Pandas
*   **Frontend**: HTML, CSS, JavaScript
*   **Comunicação**: Broker MQTT (como Mosquitto)
*   **API Externa**: O sistema se integra a uma API (neste caso, uma API em Java para simular a visão computacional).

## Como Rodar o Projeto

### Pré-requisitos

1.  Python 3.x instalado.
2.  Um broker MQTT rodando localmente (ex: Mosquitto).
3.  A API de visão computacional (Java) deve estar rodando em `http://localhost:8080`.

### Passos para Execução

1.  **Clone o repositório** para a sua máquina.

2.  **Instale as dependências** do Python:
    ```shell
    pip install -r requirements.txt
    ```

3.  **Inicie o backend**: Em um terminal, execute o servidor principal. Ele vai gerenciar os dados e o dashboard.
    ```shell
    python main.py
    ```

4.  **Inicie os simuladores de sensores**: Abra um novo terminal para cada simulador que desejar.
    ```shell
    python simulador.py leitor_1
    python simulador.py leitor_2
    python simulador.py leitor_3
    ```

5.  **Acesse o Dashboard**: Abra seu navegador e acesse `http://127.0.0.1:5000/`. Os dados das motos começarão a aparecer em tempo real.

## Resultados Parciais

Atualmente, o sistema é capaz de:
*   Simular múltiplos sensores IoT enviando dados em paralelo.
*   Receber e processar dados via MQTT.
*   Integrar com uma API externa para validar os dados dos sensores.
*   Persistir um log de todos os eventos em um arquivo CSV.
*   Exibir os dados em um dashboard web com atualizações em tempo real.
*   Destacar visualmente os eventos que apresentam inconsistências (ex: sensor detectou, mas a visão não confirmou).