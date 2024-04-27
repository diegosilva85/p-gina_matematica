import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


class Email:
    def __init__(self, valor):
        remetente = 'diegoestudosmtp@gmail.com'
        password = os.environ.get("senha_email").strip("")
        destinatario = 'diegomelosilva85@gmail.com'
        subject = f'Planilha da turma_{valor}'
        body = ''
        # Criar a mensagem MIME
        message = MIMEMultipart()
        message['From'] = remetente
        message['To'] = destinatario
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        # Anexo - Caminho do arquivo CSV
        csv_file_path = f'./static/Turma_{valor}.csv'
        # Criar a parte do anexo (CSV)
        with open(csv_file_path, 'rb') as csv_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(csv_file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={csv_file_path.split("/")[-1]}')
        # Adicionar a parte do anexo à mensagem
        message.attach(part)
        # Conectar ao servidor SMTP e enviar o email
        with smtplib.SMTP('smtp.gmail.com') as connection:
            connection.starttls()
            connection.login(user=remetente, password=password)
            connection.sendmail(remetente, destinatario, message.as_string())
