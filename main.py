from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
# Chave secreta obrigatória para gerenciar sessões e logins seguros no Flask
app.secret_key = 'uma_chave_secreta_e_segura_da_casa_de_deus' 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunidade.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==============================================================================
# 🗄️ MODELOS DO BANCO DE DADOS
# ==============================================================================

# Mural de postagens livres da comunidade
class Postagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    autor = db.Column(db.String(100), nullable=True, default='Anônimo')
    tipo = db.Column(db.String(50), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    votos = db.Column(db.Integer, default=0)
    comentarios = db.relationship('Comentario', backref='postagem', lazy=True, cascade="all, delete-orphan")

# Comentários vinculados às postagens
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postagem_id = db.Column(db.Integer, db.ForeignKey('postagem.id'), nullable=False)
    autor = db.Column(db.String(100), nullable=True, default='Anônimo')
    texto = db.Column(db.Text, nullable=False)

# NOVA TABELA: Leituras Bíblicas, Músicas e Avisos criados pelo Admin
class ConteudoOficial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(50), nullable=False) # 'leitura', 'musica' ou 'aviso'
    titulo = db.Column(db.String(150), nullable=False)   # Ex: "Lucas 1:21" ou Nome da Música
    conteudo = db.Column(db.Text, nullable=False)        # O texto do versículo ou descrição

# NOVA TABELA: Guarda configurações do site (como a cor hexadecimal escolhida)
class Configuracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(100), nullable=False)


# Criação inicial automática do Banco e suas Tabelas
with app.app_context():
    db.create_all()
    # Se o banco for novo e não tiver cor configurada, define o verde padrão (#2d4a27)
    if not Configuracao.query.filter_by(chave='cor_principal').first():
        cor_padrao = Configuracao(chave='cor_principal', valor='#2d4a27')
        db.session.add(cor_padrao)
        db.session.commit()

# ==============================================================================
# 🔒 DECORATOR DE SEGURANÇA (BLOQUEIA ACESSO INDEVIDO)
# ==============================================================================
def login_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logado'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==============================================================================
# 🌐 ROTAS PÚBLICAS (USUÁRIOS E DEVOTOS)
# ==============================================================================

# Página Inicial (Carrega posts, sidebar oficial e a cor do banco)
@app.route('/')
def home():
    postagens = Postagem.query.order_by(Postagem.votos.desc(), Postagem.id.desc()).all()
    conteudos = ConteudoOficial.query.order_by(ConteudoOficial.id.desc()).all()
    
    # Puxa a cor ativa do site para injetar no CSS
    cor_config = Configuracao.query.filter_by(chave='cor_principal').first()
    cor_site = cor_config.valor if cor_config else '#2d4a27'
    
    # Importante: notei que seu código renderizava 'index.html'. Mantenha o nome exato aqui:
    return render_template('index.html', postagens=postagens, conteudos=conteudos, cor_site=cor_site)

# Criar nova postagem no mural (via AJAX)
@app.route('/criar-postagem', methods=['POST'])
def criar_postagem():
    autor = request.form.get('autor') or 'Anônimo'
    tipo = request.form.get('tipo')
    conteudo = request.form.get('conteudo')

    if not conteudo:
        return jsonify({'error': 'A mensagem não pode estar vazia'}), 400

    nova_postagem = Postagem(autor=autor, tipo=tipo, conteudo=conteudo)
    db.session.add(nova_postagem)
    db.session.commit()

    return jsonify({
        'id': nova_postagem.id,
        'autor': nova_postagem.autor,
        'tipo': nova_postagem.tipo,
        'conteudo': nova_postagem.conteudo,
        'votos': nova_postagem.votos
    })

# Impulsionar ou diminuir relevância de um post (via AJAX)
@app.route('/votar/<int:post_id>/<string:acao>', methods=['POST'])
def votar(post_id, acao):
    postagem = Postagem.query.get_or_404(post_id)
    if acao == 'up':
        postagem.votos += 1
    elif acao == 'down':
        postagem.votos -= 1
    db.session.commit()
    return jsonify({'votos': postagem.votos})

# Responder a uma postagem com comentário (via AJAX)
@app.route('/comentar/<int:post_id>', methods=['POST'])
def comentar(post_id):
    autor = request.form.get('autor_comentario') or 'Anônimo'
    texto = request.form.get('texto_comentario')
    
    if not texto:
        return jsonify({'error': 'O comentário não pode estar vazio'}), 400
        
    novo_comentario = Comentario(postagem_id=post_id, autor=autor, texto=texto)
    db.session.add(novo_comentario)
    db.session.commit()
    
    return jsonify({
        'autor': novo_comentario.autor,
        'texto': novo_comentario.texto
    })

# ==============================================================================
# 🔐 ROTAS PRIVADAS (PAINEL ADMINISTRATIVO)
# ==============================================================================

# Tela de autenticação do administrador
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    erro = None
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        
        # DEFINA AS CREDENCIAIS DO DONO DO SITE AQUI:
        if usuario == 'admin' and senha == '20042026':
            session['admin_logado'] = True
            return redirect(url_for('admin_painel'))
        else:
            erro = "Usuário ou senha incorretos."
            
    return render_template('admin_login.html', erro=erro)

# Rota para deslogar do sistema
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logado', None)
    return redirect(url_for('home'))

# Painel de controle interno (Lista conteúdos e exibe configurações de cores)
@app.route('/admin/painel')
@login_obrigatorio
def admin_painel():
    conteudos = ConteudoOficial.query.order_by(ConteudoOficial.id.desc()).all()
    cor_config = Configuracao.query.filter_by(chave='cor_principal').first()
    cor_atual = cor_config.valor if cor_config else '#2d4a27'
    return render_template('admin_painel.html', conteudos=conteudos, cor_atual=cor_atual)

# Modificar a cor principal do ecossistema do site
@app.route('/admin/atualizar-cor', methods=['POST'])
@login_obrigatorio
def atualizar_cor():
    nova_cor = request.form.get('cor_site')
    cor_config = Configuracao.query.filter_by(chave='cor_principal').first()
    
    if cor_config and nova_cor:
        cor_config.valor = nova_cor
        db.session.commit()
        
    return redirect(url_for('admin_painel'))

# Cadastrar novas leituras bíblicas, louvores ou avisos na barra direita
@app.route('/admin/adicionar-conteudo', methods=['POST'])
@login_obrigatorio
def adicionar_conteudo():
    categoria = request.form.get('categoria')
    titulo = request.form.get('titulo')
    conteudo = request.form.get('conteudo')
    
    if titulo and conteudo:
        novo_item = ConteudoOficial(categoria=categoria, titulo=titulo, conteudo=conteudo)
        db.session.add(novo_item)
        db.session.commit()
        
    return redirect(url_for('admin_painel'))

# Excluir um conteúdo da sidebar oficial
@app.route('/admin/deletar-conteudo/<int:id>', methods=['POST'])
@login_obrigatorio
def deletar_conteudo(id):
    item = ConteudoOficial.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_painel'))

# ==============================================================================
# 🚀 INICIALIZAÇÃO DO SERVIDOR (PRODUÇÃO / PORTA 80)
# ==============================================================================
if __name__ == '__main__':
    # Habilitado host '0.0.0.0' e porta padrão HTTP 80 para acesso externo na rede
    app.run(host='0.0.0.0', port=80, debug=True)