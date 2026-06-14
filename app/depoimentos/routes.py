# app/depoimentos/routes.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.depoimento import Depoimento
from datetime import datetime

depoimentos_bp = Blueprint('depoimentos', __name__)

@depoimentos_bp.route('/enviar', methods=['POST'])
@login_required
def enviar_depoimento():
    """Rota para clientes enviarem depoimentos"""
    try:
        texto = request.form.get('texto')
        avaliacao = request.form.get('avaliacao')
        
        if not texto or not avaliacao:
            return jsonify({'success': False, 'error': 'Preencha todos os campos'}), 400
        
        avaliacao = int(avaliacao)
        if avaliacao < 1 or avaliacao > 5:
            return jsonify({'success': False, 'error': 'Avaliação inválida'}), 400
        
        depoimento = Depoimento(
            usuario_id=current_user.id,
            nome=current_user.nome,
            texto=texto,
            avaliacao=avaliacao,
            status='PENDENTE'
        )
        
        db.session.add(depoimento)
        db.session.commit()
        print(f"Novo depoimento enviado: {texto[:30]}... com avaliação {avaliacao} por usuário {current_user.nome}")  # Debug: Verificar detalhes do novo depoimento
        
        return jsonify({'success': True, 'message': 'Depoimento enviado com sucesso! Aguardando aprovação.'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@depoimentos_bp.route('/listar-aprovados')
def listar_aprovados():
    """Lista depoimentos aprovados para exibição"""
    depoimentos = Depoimento.query.filter_by(status='APROVADO')\
                                   .order_by(Depoimento.aprovado_em.desc())\
                                   .limit(5)\
                                    .all()
                                    
    return jsonify([{
        'id': d.id,
        'nome': d.nome,
        'texto': d.texto,
        'avaliacao': d.avaliacao,
        'data': d.aprovado_em.strftime('%d/%m/%Y') if d.aprovado_em else d.created_at.strftime('%d/%m/%Y')
    } for d in depoimentos])

# Rotas administrativas para depoimentos
@depoimentos_bp.route('/admin/pendentes')
@login_required
def admin_pendentes():
    """Admin vê depoimentos pendentes"""
    if not current_user.admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    pendentes = Depoimento.query.filter_by(status='PENDENTE')\
                                .order_by(Depoimento.created_at.desc())\
                                .all()
    
    return render_template('admin/depoimentos_pendentes.html', depoimentos=pendentes)

@depoimentos_bp.route('/admin/aprovar/<int:id>', methods=['POST'])
@login_required
def aprovar_depoimento(id):
    if not current_user.admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    depoimento = Depoimento.query.get_or_404(id)
    depoimento.status = 'APROVADO'
    depoimento.aprovado_em = datetime.utcnow()
    db.session.commit()
    print(f"Depoimento aprovado: ID {id} por admin {current_user.nome}")  # Debug: Verificar detalhes do depoimento aprovado

    flash('Depoimento aprovado com sucesso!', 'success')
    return redirect(url_for('depoimentos.admin_pendentes'))

@depoimentos_bp.route('/admin/rejeitar/<int:id>', methods=['POST'])
@login_required
def rejeitar_depoimento(id):
    if not current_user.admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    depoimento = Depoimento.query.get_or_404(id)
    db.session.delete(depoimento)
    db.session.commit()
    print(f"Depoimento rejeitado e removido: ID {id} por admin {current_user.nome}")  # Debug: Verificar detalhes do depoimento rejeitado
    
    flash('Depoimento rejeitado e removido.', 'info')
    return redirect(url_for('depoimentos.admin_pendentes'))