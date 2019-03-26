import smtplib
from email.mime.text import MIMEText
from email.header import Header


def sendMail(bot, receivers, content):
    content = "content"
    email = bot["email"]
    password = bot["password"]
    subject = "New Homework ><"
    message = MIMEText(content, "plain", 'utf-8')
    message['From'] = bot["email"]
    message['To'] = bot["email"]
    message["Subject"] = subject
    try:
        smtpObj = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtpObj.login(email, password)
        smtpObj.sendmail(email, receivers, message.as_string())
        print("Send successfully!")
    except smtplib.SMTPException as e:
        print("Error: {}".format(e))


if __name__ == "__main__":
    pass
