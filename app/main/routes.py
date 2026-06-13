# app/main/routes.py
from flask import Blueprint, redirect, render_template, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    servicos = [
        {'nome': 'Massagem Relaxante', 'descricao': 'Técnica suave que promove relaxamento profundo e alívio do estresse.', 'duracao': '60min', 'preco': 'R$ 120'},
        {'nome': 'Ventosaterapia', 'descricao': 'Terapia que utiliza ventosas para aliviar dores e tensões musculares.', 'duracao': '45min', 'preco': 'R$ 100'},
        {'nome': 'Ventosa Deslizante', 'descricao': 'Técnica de ventosaterapia com movimentos deslizantes para maior efetividade.', 'duracao': '50min', 'preco': 'R$ 130'},
        {'nome': 'Massagem com Pedras Quentes', 'descricao': 'Pedras aquecidas proporcionam relaxamento profundo e alívio muscular.', 'duracao': '75min', 'preco': 'R$ 160'},
        {'nome': 'Liberação Muscular', 'descricao': 'Técnica focada em pontos específicos para liberar tensões crônicas.', 'duracao': '60min', 'preco': 'R$ 140'}
    ]
    
    beneficios = [
        {'titulo': 'Alívio das dores', 'descricao': 'Redução significativa de dores musculares e tensões', 'icone': 'heart-pulse'},
        {'titulo': 'Relaxamento', 'descricao': 'Relaxamento profundo do corpo e mente', 'icone': 'flower1'},
        {'titulo': 'Redução do estresse', 'descricao': 'Diminuição dos níveis de cortisol e ansiedade', 'icone': 'cloud-sun'},
        {'titulo': 'Melhor circulação', 'descricao': 'Estimulação da circulação sanguínea', 'icone': 'droplet'}
    ]
    
    depoimentos = [
        {'nome': 'Maria Silva', 'texto': 'Atendimento maravilhoso! Joyce é muito profissional e atenciosa.', 'avaliacao': 5},
        {'nome': 'Carlos Santos', 'texto': 'Excelente profissional. Saí completamente relaxado.', 'avaliacao': 5},
        {'nome': 'Ana Paula', 'texto': 'A ventosaterapia fez uma diferença enorme nas minhas dores.', 'avaliacao': 5}
    ]
    
    faq = [
        {'pergunta': 'Como funciona o atendimento residencial?', 'resposta': 'Vou até sua casa com todos os equipamentos necessários para um atendimento completo.'},
        {'pergunta': 'Qual a duração de cada sessão?', 'resposta': 'As sessões variam de 45 a 75 minutos, dependendo da técnica escolhida.'},
        {'pergunta': 'Precisa de algum preparo especial?', 'resposta': 'Apenas um ambiente tranquilo e uma maca ou superfície confortável.'},
        {'pergunta': 'Qual a forma de pagamento?', 'resposta': 'Aceito dinheiro, cartões de crédito/débito e PIX.'}
    ]
    
    return render_template('main/landing.html', 
                         servicos=servicos, 
                         beneficios=beneficios,
                         depoimentos=depoimentos,
                         faq=faq)


@main_bp.route('/landing')
def splash():
    return render_template('main/splash.html')

@main_bp.route('/landing-system')
def landing_system():
    # Sua landing page original aqui
    return redirect(url_for('main.landing'))