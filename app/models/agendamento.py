from app import db
from datetime import datetime

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    servico = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='PENDENTE')
    observacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def servico_display(self):
        servicos = {
            'MASSAGEM_RELAXANTE': 'Massagem Relaxante',
            'VENTOSATERAPIA': 'Ventosaterapia',
            'VENTOSA_DESLIZANTE': 'Ventosa Deslizante',
            'PEDRAS_QUENTES': 'Massagem com Pedras Quentes',
            'LIBERACAO_MUSCULAR': 'Liberação Muscular'
        }
        return servicos.get(self.servico, self.servico)