from app import db
from app.models.user import User
from app.models.depoimento import Depoimento
from app.models.agendamento import Agendamento

# Definir relacionamentos aqui para evitar conflitos
User.agendamentos = db.relationship('Agendamento', backref='usuario', lazy=True, foreign_keys=[Agendamento.usuario_id])
User.depoimentos = db.relationship('Depoimento', backref='cliente', lazy=True, foreign_keys=[Depoimento.usuario_id])
Depoimento.usuario = db.relationship('User', backref='_depoimentos_backref', foreign_keys=[Depoimento.usuario_id])