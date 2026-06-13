# app/admin/routes.py (completo e corrigido)
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.depoimento import Depoimento
from app.models.user import User
from app.models.agendamento import Agendamento
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('main.landing'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    try:
        # Totais
        total_clientes = User.query.filter_by(admin=False).count()
        total_agendamentos = Agendamento.query.count()
        
        # Data atual
        hoje = datetime.now().date()
        
        # Agendamentos de hoje
        agendamentos_hoje = Agendamento.query.filter(Agendamento.data == hoje).count()
        
        # Agendamentos da semana
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        agendamentos_semana = Agendamento.query.filter(
            Agendamento.data >= inicio_semana,
            Agendamento.data <= inicio_semana + timedelta(days=6)
        ).count()
        
        # Agendamentos por status
        pendentes = Agendamento.query.filter_by(status='PENDENTE').count()
        confirmados = Agendamento.query.filter_by(status='CONFIRMADO').count()
        cancelados = Agendamento.query.filter_by(status='CANCELADO').count()
        depoimentos_pendentes = Depoimento.query.filter_by(status="PENDENTE").all()
        
        # Agendamentos recentes
        agendamentos_recentes = Agendamento.query.order_by(
            Agendamento.data.desc(),
            Agendamento.horario.desc()
        ).limit(10).all()
        
        return render_template('admin/dashboard.html',
                             total_clientes=total_clientes,
                             total_agendamentos=total_agendamentos,
                             agendamentos_hoje=agendamentos_hoje,
                             agendamentos_semana=agendamentos_semana,
                             pendentes=pendentes,
                             confirmados=confirmados,
                             cancelados=cancelados,
                             agendamentos_recentes=agendamentos_recentes,
                             depoimentos_pendentes=depoimentos_pendentes)
    except Exception as e:
        print(f"Erro no dashboard: {e}")
        flash('Erro ao carregar o dashboard.', 'danger')
        return redirect(url_for('main.landing'))

@admin_bp.route('/agendamentos')
@login_required
@admin_required
def agendamentos():
    status_filter = request.args.get('status', '')
    data_filter = request.args.get('data', '')
    cliente_filter = request.args.get('cliente', '')
    
    query = Agendamento.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    if data_filter:
        try:
            data_filtro = datetime.strptime(data_filter, '%Y-%m-%d').date()
            query = query.filter_by(data=data_filtro)
        except:
            pass
    if cliente_filter:
        query = query.join(User).filter(User.nome.ilike(f'%{cliente_filter}%'))
    
    agendamentos_list = query.order_by(Agendamento.data.desc(), Agendamento.horario).all()
    
    return render_template('admin/agendamentos.html', 
                         agendamentos=agendamentos_list,
                         status_filter=status_filter,
                         data_filter=data_filter,
                         cliente_filter=cliente_filter)

@admin_bp.route('/agendamento/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def alterar_status(id):
    try:
        agendamento = Agendamento.query.get_or_404(id)
        novo_status = request.json.get('status')
        
        if novo_status in ['PENDENTE', 'CONFIRMADO', 'CONCLUIDO', 'CANCELADO']:
            agendamento.status = novo_status
            db.session.commit()
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Status inválido'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/agendamento/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_agendamento(id):
    try:
        agendamento = Agendamento.query.get_or_404(id)
        db.session.delete(agendamento)
        db.session.commit()
        flash('Agendamento excluído com sucesso!', 'success')
    except Exception as e:
        flash('Erro ao excluir agendamento.', 'danger')
    
    return redirect(url_for('admin.agendamentos'))

@admin_bp.route('/clientes')
@login_required
@admin_required
def clientes():
    clientes_list = User.query.filter_by(admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/clientes.html', clientes=clientes_list)