import os
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import requests

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
underdog = os.getenv("ASSISTANT_ID")


def wait_on_run(run, thread):
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    while run.status in ["queued", "in_progress"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    return run


def get_openai_response(prompt):
    """Obtém resposta do Assistente OpenAI (UNDERDOG)"""
    try:
        thread = client.beta.threads.create()

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )

        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=underdog)
        run = wait_on_run(run, thread)

        messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
        messages_list = list(messages)
        response = messages_list[-1].content[0].text.value

        return response
    except Exception as e:
        return f"Erro no OpenAI: {str(e)}"


def get_existing_bot_response(prompt):
    """Obtém resposta do bot LANLINK"""
    try:
        url = "https://fnc-seplagmg-faleconosco.azurewebsites.net/api/Chat?"
        body = {
            "key": os.getenv("FNC_KEY"),
            "pergunta": prompt
        }
        response = requests.post(url, json=body)

        return response.text if response.status_code == 200 else "Erro na API LANLINK."
    except Exception as e:
        return f"Erro no bot LANLINK: {str(e)}"


def get_faleconosco_response(prompt):
    """Obtém resposta do bot FALE CONOSCO (Direct Line)"""
    try:
        url_token = "https://faleconosco-azure-bot.azurewebsites.net/directline/token"
        token_response = requests.get(url_token)

        if token_response.status_code != 200:
            return "Erro ao obter token do bot."

        token = token_response.json().get("token")
        if not token:
            return "Token do bot não encontrado."

        url_conversation = "https://directline.botframework.com/v3/directline/conversations"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        conversation_response = requests.post(url_conversation, headers=headers)
        if conversation_response.status_code not in [200, 201]:  # Aceita 201 como sucesso
            return f"Erro ao criar conversa com o bot. Status: {conversation_response.status_code}, Response: {conversation_response.text}"

        conversation_id = conversation_response.json().get("conversationId")
        if not conversation_id:
            return "Erro: conversationId não encontrado na resposta do bot."

        print(f"✅ Conversa criada com sucesso! ID: {conversation_id}")  # Depuração




        conversation_id = conversation_response.json().get("conversationId")

        url_message = f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities"
        message_body = {
            "type": "message",
            "from": {"id": "user"},
            "text": prompt
        }

        print("Enviando mensagem para o bot...", message_body)  # LOG PARA DEBUG

        message_response = requests.post(url_message, json=message_body, headers=headers)

        if message_response.status_code != 200:
            return f"Erro ao enviar mensagem ao bot. Status: {message_response.status_code}, Response: {message_response.text}"
        


        url_activities = f"https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities"
        activities_response = requests.get(url_activities, headers=headers)

        messages = activities_response.json().get("activities", [])

        for msg in reversed(messages):
            print(f"🔍 Depurando resposta: {msg}")  # LOG PARA DEPURAÇÃO

            if msg.get("from", {}).get("id") != "user":  
                # Tenta pegar o texto padrão (caso exista)
                text_content = msg.get("text", "")

                # Se não houver texto, tenta extrair do Adaptive Card
                if not text_content and "attachments" in msg:
                    for attachment in msg["attachments"]:
                        if attachment.get("contentType") == "application/vnd.microsoft.card.adaptive":
                            adaptive_card = attachment.get("content", {})
                            body = adaptive_card.get("body", [])
                            for item in body:
                                if item.get("type") == "TextBlock" and "text" in item:
                                    text_content = item["text"]
                                    break

                return text_content if text_content else "⚠️ O bot respondeu, mas o conteúdo não pôde ser extraído."

        return "⚠️ O bot não enviou uma resposta válida."



        return "Sem resposta do bot."
    except Exception as e:
        return f"Erro no bot FALE CONOSCO: {str(e)}"


@app.route('/api/bot0', methods=['POST'])
def bot0():
    """Chama LLKv2 (placeholder para implementação futura)"""
    data = request.json
    prompt = data['prompt']
    response = "LLKv2 não implementado."
    return jsonify({'response': response})


@app.route('/api/bot1', methods=['POST'])
def bot1():
    """Chama o bot OpenAI (UNDERDOG)"""
    data = request.json
    prompt = data['prompt']
    response = get_openai_response(prompt)
    return jsonify({'response': response})


@app.route('/api/bot2', methods=['POST'])
def bot2():
    """Chama o bot LANLINK"""
    data = request.json
    prompt = data['prompt']
    response = get_existing_bot_response(prompt)
    return jsonify({'response': response})


@app.route('/api/bot3', methods=['POST'])
def bot3():
    """Chama o bot FALE CONOSCO"""
    data = request.json
    prompt = data['prompt']
    response = get_faleconosco_response(prompt)
    return jsonify({'response': response})


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
