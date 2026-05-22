from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração corrigida do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunidade.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo das Postagens (Adicionado o sistema de votos)
class Postagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    autor = db.Column(db.String(100), nullable=True, default='Anônimo')
    tipo = db.Column(db.String(50), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    votos = db.Column(db.Integer, default=0) # Contador estilo Reddit (Upvotes - Downvotes)
    
    # Relação para puxar os comentários dessa postagem automaticamente
    comentarios = db.relationship('Comentario', backref='postagem', lazy=True, cascade="all, delete-orphan")

# Novo Modelo: Tabela para armazenar os Comentários
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postagem_id = db.Column(db.Integer, db.ForeignKey('postagem.id'), nullable=False)
    autor = db.Column(db.String(100), nullable=True, default='Anônimo')
    texto = db.Column(db.Text, nullable=False)

# Criar o banco de dados e as tabelas
with app.app_context():
    db.create_all()

# Rota Principal
@app.route('/')
def home():
    # Puxa as postagens com mais votos primeiro (ou você pode mudar para Postagem.id.desc() se preferir por data)
    postagens = Postagem.query.order_by(Postagem.votos.desc(), Postagem.id.desc()).all()
    return render_template('index.html', postagens=postagens)

# Rota para Criar Postagem
@app.route('/criar-postagem', methods=['POST'])
def criar_postagem():
    autor = request.form.get('autor')
    tipo = request.form.get('tipo')
    conteudo = request.form.get('conteudo')

    nova_postagem = Postagem(autor=autor, tipo=tipo, conteudo=conteudo)
    db.session.add(nova_postagem)
    db.session.commit()
    return redirect(url_for('home'))

# Rota para Sistema de Votação (Upvote / Downvote)
# Rota para Sistema de Votação (Upvote / Downvote)
@app.route('/votar/<int:post_id>/<string:acao>', methods=['POST'])
def votar(post_id, acao):
    # Mudado de get_or_400 para get_or_404
    postagem = Postagem.query.get_or_404(post_id)
    
    if acao == 'up':
        postagem.votos += 1
    elif acao == 'down':
        postagem.votos -= 1
    
    db.session.commit()
    return redirect(url_for('home'))

# Rota para Adicionar Comentário
@app.route('/comentar/<int:post_id>', methods=['POST'])
def comentar(post_id):
    autor = request.form.get('autor_comentario')
    texto = request.form.get('texto_comentario')
    
    if texto: # Garante que o comentário não está vazio
        novo_comentario = Comentario(postagem_id=post_id, autor=autor, texto=texto)
        db.session.add(novo_comentario)
        db.session.commit()
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    # host='0.0.0.0' permite conexões externas
    # port=80 é a porta padrão da internet (HTTP)
    app.run(host='0.0.0.0', port=80, debug=True)