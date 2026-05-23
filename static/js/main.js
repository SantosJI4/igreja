  // 1. Sistema Interativo de Votos
    function enviarVoto(postId, acao) {
        fetch(`/votar/${postId}/${acao}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            const contador = document.getElementById(`contador-${postId}`);
            contador.innerText = data.votos;
            contador.classList.remove('positivo', 'negativo');
            if (data.votos > 0) contador.classList.add('positivo');
            if (data.votos < 0) contador.classList.add('negativo');
        });
    }

    // 2. Sistema Interativo de Comentários
    function enviarComentario(event, postId) {
        event.preventDefault(); // Impede o reload da página
        const form = event.target;
        const formData = new FormData(form);

        fetch(`/comentar/${postId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if(data.error) return;

            // Insere o comentário visualmente na lista certa
            const lista = document.getElementById(`lista-comentarios-${postId}`);
            const novoComentarioHTML = `<div class="comentario-item"><strong>${data.autor}:</strong> ${data.texto}</div>`;
            lista.insertAdjacentHTML('beforeend', novoComentarioHTML);
            
            // Limpa o campo de texto digitado
            form.querySelector('.input-comentario-texto').value = '';
            
            // Rola a caixinha de comentários para o final para mostrar a resposta
            lista.scrollTop = lista.scrollHeight;
        });
    }

    // 3. Sistema Interativo de Novas Postagens
    document.getElementById('form-nova-postagem').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);

        fetch('/criar-postagem', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if(data.error) return;

            const mural = document.getElementById('mural-postagens');
            const muralVazio = document.getElementById('mural-vazio');
            if (muralVazio) muralVazio.remove(); // Tira a mensagem de feed vazio se existir

            // Monta o HTML do novo card dinamicamente com as funções AJAX ativas
            const novoCardHTML = `
                <div class="reddit-card" id="post-card-${data.id}" style="animation: fadeIn 0.5s ease;">
                    <div class="votos-sidebar">
                        <button type="button" class="btn-voto upvote" onclick="enviarVoto('${data.id}', 'up')"><i class="fas fa-arrow-up"></i></button>
                        <span id="contador-${data.id}" class="contador-votos">${data.votos}</span>
                        <button type="button" class="btn-voto downvote" onclick="enviarVoto('${data.id}', 'down')"><i class="fas fa-arrow-down"></i></button>
                    </div>
                    <div class="conteudo-postagem-box">
                        <span class="tag-tipo">${data.tipo}</span>
                        <p class="texto-postagem">"${data.conteudo}"</p>
                        <div class="meta-postagem"><span>— Por: <strong>${data.autor}</strong></span></div>
                        <hr class="divisor-comentarios">
                        <div class="comentarios-section">
                            <h4 id="titulo-comentarios-${data.id}"><i class="far fa-comments"></i> Comentários (0)</h4>
                            <div class="lista-comentarios" id="lista-comentarios-${data.id}"></div>
                            <form onsubmit="enviarComentario(event, '${data.id}')" class="form-comentario">
                                <input type="text" name="autor_comentario" placeholder="Seu nome (opcional)" class="input-comentario-autor">
                                <div class="input-grupo-comentario">
                                    <input type="text" name="texto_comentario" placeholder="Escreva um comentário de apoio..." required class="input-comentario-texto">
                                    <button type="submit" class="btn-comentar">Responder</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            `;

            // Coloca no topo do mural das mensagens
            mural.insertAdjacentHTML('afterbegin', novoCardHTML);
            
            // Limpa o formulário de envio
            document.getElementById('form-nova-postagem').reset();
        });
    });