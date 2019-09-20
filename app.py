import os
from flask import Flask, request
import telebot
from telebot import types
import psycopg2
from random import randint

DATABASE_URL = os.environ['DATABASE_URL']
conexion = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conexion.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id_usuario integer unique, user_name varchar(50), alias varchar(50), bonos_solicitados integer DEFAULT 0, importe integer DEFAULT 0, is_admin bool DEFAULT False, creado date default CURRENT_DATE, ultimo_uso date default CURRENT_DATE, casa varchar(50));")

# Inserte su url
URL_PATH = 'https://tu.url.com/'

# Inserte su token
TOKEN = 'tu12345token'

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
hideBoard = types.ReplyKeyboardRemove()

def calcularBono(u_name, importe, casa='Codere'):

    link = {
                'Codere':'bit.ly/coderetg',
                'Bet365':'bit.ly/bet365tg',
                'William Hill':'bit.ly/willhilltg',
                'Betfair':'bit.ly/betfairtg',
                'Sportium':'bit.ly/sportiumtg',
                'Bwin':'bit.ly/bwintg',
                '888sport': 'bit.ly/888sportg',
            }

 
    msg = []
    msg.append(str(u_name))
    msg.append('Según la calculadora, el mejor bono es el de '+ casa +', donde recibirás un bono total de '+str(importe)+'€')
    msg.append('<b>Ahora debes</b> <a href="http://' + link[casa] +'">registrarte en la casa de apuestas a través de este link</a>!')
    msg.append('Cuando lo hayas hecho, deberás escribirnos a info@infobonos.es indicando tu nombre de usuario en la casa de apuestas seleccionada, recuerda que puedes elegir entre estas casas: <a href="http://bit.ly/bet365tg">Bet365</a>, <a href="http://bit.ly/willhilltg">William Hill</a>, <a href="http://bit.ly/betfairtg">Betfair</a>, <a href="http://bit.ly/sportiumtg">Sportium</a>, <a href="http://bit.ly/bwintg">Bwin</a>, <a href="http://bit.ly/coderet">Codere</a> y <a href="http://bit.ly/888sportg">888sport</a>')
    msg.append('Una vez hayamos validado tus datos, procederemos a entregarte el bono especial de InfoBonos de 25€.')
    msg.append('Recuerda que este bono especial está sujeto a las siguientes <a href="http://bit.ly/condicionestg">condiciones</a>.')

    text = str()
    for i in msg:
        text += i +'\n\n'

    return text

# Para promover entrar al menu de administrador  envie el comando /admin
@bot.message_handler(commands=['admin'])
def admin(message):
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario::integer IN ({})".format(message.from_user.id)) 
    u = cursor.fetchone()
    print(u)
    if u[5] == True:   
        bot.send_message(message.chat.id,'Hola Admin! 😇',reply_markup=menu_admin())
    else:
        bot.send_message(message.chat.id, 'Necesita privilegios de administrador para utilizar esta opción.')

# Para promover privilegios de administrador a un usuario envie el comando /create_new_admin*
@bot.message_handler(commands=['create_new_admin*'])
def new_admin(message):
    try:
        cursor.execute("UPDATE usuarios SET is_admin=%s::bool  WHERE id_usuario=%s::integer",(True, message.from_user.id))
        conexion.commit()
        bot.send_message(message.chat.id,'Hola nuevo Admin! 😇',reply_markup=menu_admin())
    except Exception as e:
        print(e)

@bot.message_handler(commands=['start'])
def start(message):
    
   
    bot.reply_to(message, 'Bienvenid@ 🤗, ¿Cuál va a ser tu primer depósito?', reply_markup=menu())

    if message.from_user.username:
        alias = message.from_user.username
    else:
        alias = 'Sin alias'
    
    try: 
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario::integer IN ({})".format(message.from_user.id))
        row = cursor.fetchone()
        print(row)
        if row:
            print('Ya existe.')
        else:
            cursor.execute("INSERT INTO usuarios (id_usuario, user_name, alias) VALUES ({},'{}','{}');".format(message.from_user.id, message.from_user.first_name, alias))

    except Exception as e:
        print(e)
@bot.callback_query_handler(lambda q: q.message.chat.type == "private")
def private_query(query):
    
    bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id)

    message = query

    if query.data == 'Recibir':
        
        try:
            cursor.execute("SELECT * FROM usuarios WHERE id_usuario::integer IN ({})".format(message.from_user.id)) 
            u = cursor.fetchone()
            importe = u[4]
            c = u[8]
            print(importe)

            if importe > 0:
                bot.send_message(message.from_user.id,calcularBono(message.from_user.first_name, importe, casa=c), reply_markup=hideBoard,parse_mode='HTML')
                bot.send_message(message.from_user.id, 'Quieres calcular un nuevo bono? 👇', reply_markup=button_replay())
                cursor.execute("UPDATE usuarios SET bonos_solicitados=%s::integer  WHERE id_usuario=%s::integer",(u[3]+1, message.from_user.id))
            else:
                bot.send_message(message.from_user.id,'Debe seleccionar un monto a depositar para calcular un Bono.', reply_markup=menu())
        except Exception as e:
            print(e)
    if query.data == 'Reintentar':
        bot.send_message(message.from_user.id,'Seleccione un nuevo monto a calcular! 😉', reply_markup=menu())
def menu_admin():
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('Balance 📊')
    itembtn2 = types.KeyboardButton('Usuarios 🗂')
    itembtn3 = types.KeyboardButton('Notificar 📤')
    itembtn4 = types.KeyboardButton('Salir 🔙')

    markup.add(itembtn1, itembtn2, itembtn3, itembtn4) 
    
    return markup  
def menu():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('10 €')
    itembtn2 = types.KeyboardButton('30 €')
    itembtn3 = types.KeyboardButton('50 €')
    itembtn4 = types.KeyboardButton('100 €')
    itembtn5 = types.KeyboardButton('200 €')
    itembtn6 = types.KeyboardButton('300 €')
    itembtn7 = types.KeyboardButton('400 €')
    itembtn8 = types.KeyboardButton('500 €')
    markup.add(itembtn1, itembtn2, itembtn3,itembtn4, itembtn5, itembtn6, itembtn7, itembtn8) 
    
    return markup
def button_bono():
    emo = ('💸','💵','🍾','🍺','💰','💷','💶','💴','👑','🍻')
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton("Recibir Bono "+emo[randint(0,9)], callback_data="Recibir"))
    return k
def button_replay():
    emo = ('💸','💵','🍾','🍺','💰','💷','💶','💴','👑','🍻')
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton("Calcular nuevo bono "+emo[randint(0,9)], callback_data="Reintentar"))
    return k
@bot.message_handler(func=lambda message: True, content_types=['text'])
def main(message):

    print('usuario: '+message.from_user.first_name)
    print('id: '+ str(message.from_user.id))
    print('comando: '+ str(message.text))

    try:
        cursor.execute('UPDATE usuarios SET ultimo_uso = CURRENT_DATE where id_usuario={}'.format(message.from_user.id))
    except Exception as e:
        print(e)


    if message.text == '10 €' or message.text == '30 €' or message.text == '50 €' or message.text == '100 €' or message.text == '200 €' or message.text == '300 €' or message.text == '400 €' or message.text == '500 €':
        
        bono = str()
        casa = ['Codere','Bet365','William Hill','Betfair','Sportium','Bwin','888sport']
        casa = casa[randint(0,6)]
        
        importe = message.text.replace(' €','')


        if int(importe) < 350 and casa == 'Codere':
            bono = str(importe)
        elif int(importe) > 350 and casa == 'Codere':
            bono = str(350)
        elif int(importe) < 250 and casa == 'Bwin':
            bono = str(importe)
        elif int(importe) > 250 and casa == 'Bwin':
            bono = str(250)
        elif int(importe) < 100:
            bono = str(importe)
        elif int(importe) >= 100:
            bono = str(100)

        if int(importe) < 100:
            infobono = str(0)
        else:
            infobono = str(25)

        total = str(int(importe)+ int(bono) + int(infobono))
        bot.reply_to(message, 'Tu importe: ' + importe +' €'+ '\nTu Bono: '+ bono +' €'+ '\nInfoBonos: ' + infobono +' €'+ '\nRecibes: ' + total +' €', reply_markup=menu())
        
        emo = ('🤯','😳','🤩','🥳','🤗','😍','🥰','😻','😼','🙀')

        bot.send_message(message.from_user.id, 'No te lo pierdas '+emo[randint(0,9)], reply_markup=button_bono())

        try:
            if message.from_user.username:
                alias = message.from_user.username
            else:
                alias = 'Sin alias'     

            cursor.execute("SELECT * FROM usuarios WHERE id_usuario::integer IN ({})".format(message.from_user.id))
            row = cursor.fetchall()

            if row:
                cursor.execute("UPDATE usuarios SET importe=%s::integer, casa=%s::text  WHERE id_usuario=%s::integer",(total, casa,message.from_user.id))
            else:
                cursor.execute("INSERT INTO usuarios (id_usuario, user_name, alias, importe, casa) VALUES ({},'{}','{}',{},'{}');".format(message.from_user.id, message.from_user.first_name, alias, total, casa))

        except Exception as e:
            print(e)
    
    elif message.text == 'Balance 📊':
        
        cursor.execute('SELECT COUNT(*) FROM usuarios') 
        u = cursor.fetchone()

        cursor.execute('SELECT SUM(bonos_solicitados) FROM usuarios') 
        b = cursor.fetchone()

        bot.send_message(message.chat.id, 'Usuarios registrados: <b>{}</b>'.format(u[0])+'\nBonos solicitados: <b>{}</b>'.format(b[0]), parse_mode='HTML')


    elif message.text == 'Usuarios 🗂':
        msg = str()
        cursor.execute('SELECT * FROM usuarios') 
        users = cursor.fetchall()

        for u in users:

            msg += '\nNombre: <b>{}</b>'.format(u[1])
            msg += '\nAlias: <b>@{}</b>'.format(u[2])
            msg += '\nBonos solicitados: <b>{}</b>'.format(u[3])
            msg += '\nUltimo bono calculado: <b>{}</b>'.format(u[4])+' €'
            msg += '\nSe unió el: <b>{}</b>'.format(u[6])
            msg += '\nUltima visita: <b>{}</b>'.format(u[7])+'\n\n'

        bot.send_message(message.chat.id, msg, parse_mode='HTML')
    elif message.text == 'Notificar 📤':
        markup = types.ForceReply(selective=False)

        bot.send_message(message.chat.id, "Responda el siguiente mensaje para difundir, puede utilizar etiquetas como <b>*negrita*</b> o <i>_italica_</i> para resaltar el texto. \n\nPara cancelar presione <b>x</b>", parse_mode='HTML')
        
        bot.send_message(message.chat.id, "difundir:", reply_markup=markup)
        
    elif message.reply_to_message:

        cursor.execute("SELECT * FROM usuarios WHERE id_usuario::integer IN ({})".format(message.from_user.id)) 
        u = cursor.fetchone()
        print(u)
        if u[5] == True:
            if message.reply_to_message.text == 'difundir:':
                
                cursor.execute('SELECT * FROM usuarios') 
                users = cursor.fetchall()

                for u in users:
                    try:
                        bot.send_message(u[0], message.text, parse_mode='Markdown', reply_markup=menu())
                    except:
                        pass
                bot.send_message(message.chat.id, 'Notificafión enviada!',reply_markup=menu_admin())
            else:
                bot.send_message(message.chat.id, 'Error al notificar, asegurese de que está respondiendo al mensaje correcto.', reply_markup=menu_admin(), parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'Necesita privilegios de administrador para utilizar esta opción.')
    elif message.text == 'Salir 🔙':
        bot.send_message(message.chat.id,'Hasta luego Admin 😉', reply_markup=menu())
    else:
        bot.reply_to(message, 'Seleccione el menú y escoja un importe válido.', reply_markup=menu())
    conexion.commit()
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200
#Al cambiar la url o el token debe entrar al link para que se actualice
@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=URL_PATH + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
conexion.close()
