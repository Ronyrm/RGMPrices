from ast import expr_context
from App import app,db
from flask import request,jsonify,render_template,session,redirect,url_for
from flask_login import login_user,current_user
from App.views.Pessoas import usuarios
from App.models.usuarios import SchemaUsuarios, Usuarios
from functools import wraps
import jwt
import datetime

def getTokenUser(usuario):
    try:
        totalHoraExpira = int(app.config['HORA_EXPIRA_TOKEN'])
    except:
        totalHoraExpira = 12

    dtexp = datetime.datetime.now() + datetime.timedelta(hours=totalHoraExpira)
    try:
        return jwt.encode({'username': usuario.username, 'id': usuario.id, 'exp': dtexp},
                             app.config['SECRET_KEY'],
                             algorithm='HS256')
    except:
        return None
            

def autentifica_form():
    from werkzeug.security import check_password_hash
    import jwt

    if request.method == 'POST':
        username, senha = request.form['username'],request.form['password']

        usuario = usuarios.capturaUsuarioPorUserNameEmail(username,username)
        if not usuario:
            return render_template('layouts/login.html',
                                   login=False,
                                   mensagem='O Usuário {} não foi encontrado na base de dados.'.format(username))

        valida =  check_password_hash(usuario.senha,senha)
        if not valida:
            return render_template('layouts/login.html',
                                   login=False,
                                   mensagem='Senha não confere.')

        token = getTokenUser(usuario)
        #try:
        #    token_decode = token.encode().decode('utf-8')
        #except ValueError as err:
        #    return render_template('layouts/login.html',
        #                           login=False,
        #                           mensagem='Erro ao decodificar:' + str(err))
        try:
            usuario.token = token
            db.session.commit()
            login_user(usuario)
        except Exception as E:
            return render_template('layouts/login.html',
                                   login=False,
                                   mensagem='Houve um erro na geração do Token. Error: {}'.format(str(E)))
        #    print(str(E))
        
        #try:
        #    schema = schema = SchemaUsuarios(many=True,exclude=('senha','token'))
        #    userschema = schema.dump(usuario)
        #    print(userschema)
        #except Exception as E:
        #    print(str(E))    

        return redirect(url_for('index.root',token=token))
        #return render_template('layouts/index.html',
        #                       login=True,
        #                       mensagem='Usuário logado com sucesso',
        #                       token=token_decode)

    #return jsonify({'mensagem': 'Não pode verificar!', 'login': False}), 401
    return render_template('layouts/login.html',
                                   login=False,
                                   mensagem='Houve uma falha na validação e geração do Token. Faça novamente o Login!')

def token_requerido(func):
    @wraps(func)
    def decorated(*args, **kwargs):

        token = request.args.get('token')
        if not token:
            token = current_user.token if current_user.is_authenticated else None
                
        if not token:
            #return jsonify({'login': False, 'mensagem': ' Token não informado','data': {}}), 401
            return render_template('layouts/login.html',login='',mensagem='')
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms="HS256")
            #current_user = usuarios.capturaUsuarioPorUserName(data['username'])

            #return jsonify({'valide': True, 'mensage': ' Token Valido', 'data': data}), 201

        except Exception as e:
            #return jsonify({'login': False, 'mensagem': ' Token inválido ou expirado', 
            #                'data': {},
            #                'erro': str(e)}), 401
            return render_template('layouts/login.html',
                                   login=False,
                                   mensagem='Token inválido ou expirado. Faça novamente o Login!')


        return func(token,*args, **kwargs)
    return decorated