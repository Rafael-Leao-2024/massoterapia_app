from app import db
from datetime import datetime

class Depoimento(db.Model):
    __tablename__ = 'depoimentos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    avaliacao = db.Column(db.Integer, nullable=False)  # 1 a 5 estrelas
    status = db.Column(db.String(20), default='PENDENTE')  # PENDENTE, APROVADO, REJEITADO
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    aprovado_em = db.Column(db.DateTime)
    
    # Mudando o nome do backref para evitar conflito
    usuario = db.relationship('User', backref='depoimentos_feitos', foreign_keys=[usuario_id])
    
    def __repr__(self):
        return f'<Depoimento {self.nome} - {self.avaliacao} estrelas>'