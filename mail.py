import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from env import EmailConfig
from typing import List


def send_email(to_emails: List[str], subject, data_list, order_info):
    print(EmailConfig.SMTP_EMAIL)
    print(EmailConfig.SMTP_SERVER)
    print(EmailConfig.SMTP_PORT)
    print(EmailConfig.SMTP_PASSWORD)
    msg = MIMEMultipart()
    msg["From"] = EmailConfig.SMTP_EMAIL
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = subject

    body = (
        f"<h2>Order ID: {order_info.id}</h2> <h2>Order Total: {order_info.total}</h2>"
    )
    index = 1
    for obj in data_list:
        item = obj.item
        body += f"<h2>Item #{index}:</h2>"
        body += f"<p><b>Quantity:</b> {obj.quantity}</p>"
        body += f"<p><b>Item:</b> {item.upc}</p>"
        body += f"<p><b>Description:</b> {item.description}</p>"
        body += f"<p><b>Price:</b> {item.price}</p>"
        body += f"<p><b>In Stock:</b> {item.in_stock}</p>"
        body += f"<p><b>On Order:</b> {item.on_order}</p>"
        body += f"<p><b>Manufacturer Part:</b> {item.mfr_part}</p>"
        body += f"<p><b>Manufacturer:</b> {item.manufacturer}</p>"
        body += f"<p><b>Category:</b> {item.category}</p>"
        body += f"<p><b>Condition:</b> {item.condition}</p>"
        body += "<hr />"
        index += 1

    # HTML body
    html_body = f"""
    <html>
    <body>
        <h1>Hello!</h1>
        {body}
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, "html"))
    msg.attach(MIMEText(body, "plain"))
    server = smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT)
    server.login(EmailConfig.SMTP_EMAIL, EmailConfig.SMTP_PASSWORD)
    # server.starttls()
    server.login(EmailConfig.SMTP_EMAIL, EmailConfig.SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(EmailConfig.SMTP_EMAIL, to_emails, text)
    server.quit()
