# app/cliente/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.agendamento import Agendamento
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/painel')
@login_required
def painel():
    if current_user.admin:
        return redirect(url_for('admin.dashboard'))
    
    agendamentos = Agendamento.query.filter_by(usuario_id=current_user.id)\
                                   .order_by(Agendamento.data.desc(), Agendamento.horario.desc())\
                                   .all()
    
    return render_template('cliente/painel.html', agendamentos=agendamentos)

@cliente_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        current_user.nome = request.form.get('nome')
        current_user.cpf = request.form.get('cpf')
        current_user.telefone = request.form.get('telefone')
        
        nova_senha = request.form.get('nova_senha')
        if nova_senha:
            current_user.senha = generate_password_hash(nova_senha)
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('cliente.perfil'))
    
    return render_template('cliente/perfil.html')

@cliente_bp.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar():
    if request.method == 'POST':
        servico = request.form.get('servico')
        data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
        horario = datetime.strptime(request.form.get('horario'), '%H:%M').time()
        observacao = request.form.get('observacao')
        
        horarios_validos = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00']
        if horario.strftime('%H:%M') not in horarios_validos:
            flash('Horário inválido.', 'danger')
            return redirect(url_for('cliente.agendar'))
        
        if data < datetime.now().date():
            flash('Não é possível agendar em datas passadas.', 'danger')
            return redirect(url_for('cliente.agendar'))
        
        existe = Agendamento.query.filter_by(data=data, horario=horario).first()
        if existe:
            flash('Este horário já está ocupado. Por favor, escolha outro.', 'danger')
            return redirect(url_for('cliente.agendar'))
        
        agendamento = Agendamento(
            usuario_id=current_user.id,
            servico=servico,
            data=data,
            horario=horario,
            observacao=observacao,
            status='PENDENTE'
        )
        
        db.session.add(agendamento)
        db.session.commit()
        
        flash('Agendamento realizado com sucesso! Aguardando confirmação.', 'success')
        return redirect(url_for('cliente.painel'))
    
    return render_template('cliente/agendar.html', now=datetime.now())

@cliente_bp.route('/agendamento/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    
    if agendamento.usuario_id != current_user.id:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('cliente.painel'))
    
    if agendamento.status == 'CANCELADO':
        flash('Este agendamento já está cancelado.', 'warning')
        return redirect(url_for('cliente.painel'))
    
    agendamento.status = 'CANCELADO'
    db.session.commit()
    
    flash('Agendamento cancelado com sucesso.', 'success')
    return redirect(url_for('cliente.painel'))

@cliente_bp.route('/horarios-disponiveis')
@login_required
def horarios_disponiveis():
    data_str = request.args.get('data')
    if not data_str:
        return jsonify({'horarios': []})
    
    data = datetime.strptime(data_str, '%Y-%m-%d').date()
    
    horarios_fixos = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00']
    
    agendamentos = Agendamento.query.filter_by(data=data).all()
    horarios_ocupados = [a.horario.strftime('%H:%M') for a in agendamentos]
    
    horarios_disponiveis = [h for h in horarios_fixos if h not in horarios_ocupados]
    
    return jsonify({'horarios': horarios_disponiveis})