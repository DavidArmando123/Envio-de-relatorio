from flask import Flask, request, render_template, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

cred = credentials.Certificate(os.getenv("firebase-key.json")) 
firebase_admin.initialize_app(cred)
db = firestore.client()

EMAIL_HOST = "smtp.gmail.com"  
EMAIL_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  

def enviar_email_notificacao(dados):
    try:
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS 
        msg['Subject'] = "Novo dado enviado ao sistema"
        corpo = f"Uma nova informação foi enviada ao sistema:\n\nNome: {dados['nome']}\nE-mail: {dados['email']}\nMensagem: {dados['mensagem']}"
        msg.attach(MIMEText(corpo, 'plain'))

        # Envio do e-mail
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("E-mail de notificação enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            email = request.form.get('email')
            mensagem = request.form.get('mensagem')

            if not nome or not email or not mensagem:
                flash("Todos os campos são obrigatórios!", "erro")
                return redirect(url_for('index'))

            db.collection('form_data').add({
                'nome': nome,
                'email': email,
                'mensagem': mensagem
            })
            enviar_email_notificacao({'nome': nome, 'email': email, 'mensagem': mensagem})

            flash("Dados enviados com sucesso!", "sucesso")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Erro ao enviar dados: {str(e)}", "erro")
            return redirect(url_for('index'))
    return render_template('formulario.html')

if __name__ == '__main__':
    app.secret_key = 'chave_secreta'
    app.run(debug=True)
