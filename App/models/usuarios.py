from App import db,ma
from datetime import datetime
from App.models.pessoas import SchemaPessoas
from marshmallow import Schema
from flask_login import UserMixin
from werkzeug.security import check_password_hash,generate_password_hash
from marshmallow import fields

class Usuarios(db.Model,UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    senha = db.Column(db.String(200), nullable=False)
    token = db.Column(db.String(255))
    datacriacao = db.Column(db.DateTime, default=datetime.now())
    idpessoa = db.Column(db.Integer, db.ForeignKey('pessoas.id'))
    pessoa = db.relationship("Pessoas")

    def setSenha(self,senha):
        self.senha = generate_password_hash(senha)

    def getValidacaoSenha(self,senha):
        return check_password_hash(self.senha,senha)
    
class SchemaUsuarios(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuarios
    pessoa = fields.Nested(SchemaPessoas)