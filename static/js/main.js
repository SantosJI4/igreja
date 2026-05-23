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

document.addEventListener("DOMContentLoaded", function() {
    const btnAbrir = document.getElementById('btn-fab-abrir');
    const btnFechar = document.getElementById('btn-fab-fechar');
    const modal = document.getElementById('modal-formulario-layout');
    
    const originalFormContainer = document.querySelector('.coluna-esquerda .formulario-box');
    const modalFormContainer = document.getElementById('container-formulario-dinamico');
    const formElement = document.getElementById('form-nova-postagem');

    // 1. Gerencia o posicionamento do formulário baseado no Viewport
    function gerenciarLayoutFormulario() {
        if (window.innerWidth <= 768) {
            if (btnAbrir) btnAbrir.style.display = 'flex';
            if (formElement && modalFormContainer && modalFormContainer.children.length === 0) {
                modalFormContainer.appendChild(formElement);
            }
        } else {
            if (btnAbrir) btnAbrir.style.display = 'none';
            if (modal) {
                modal.classList.remove('active');
                modal.style.display = 'none';
            }
            if (formElement && originalFormContainer && originalFormContainer.children.length === 0) {
                originalFormContainer.appendChild(formElement);
            }
        }
    }

    // 2. Ouvintes de Evento para Abrir/Fechar o Modal
    if (btnAbrir) {
        btnAbrir.addEventListener('click', () => {
            if (modal) {
                modal.style.display = 'flex'; // Garante o display antes da classe
                setTimeout(() => modal.classList.add('active'), 10);
            }
        });
    }

    if (btnFechar) {
        btnFechar.addEventListener('click', fecharModalMobile);
    }

    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                fecharModalMobile();
            }
        });
    }

    function fecharModalMobile() {
        if (modal) {
            modal.classList.remove('active');
            setTimeout(() => {
                if (!modal.classList.contains('active')) {
                    modal.style.display = 'none';
                }
            }, 300); // Tempo batendo com a animação do CSS
        }
    }

    // 3. SOLUÇÃO DO PROBLEMA: Delegação de Evento Global para o Submit
    // Isso garante que não importa onde o formulário esteja, o clique vai funcionar.
    document.addEventListener('submit', function(event) {
        // Verifica se o formulário disparado é o de nova postagem
        if (event.target && event.target.id === 'form-nova-postagem') {
            
            // Se você já tinha um event.preventDefault() na sua lógica antiga do main.js, 
            // mantenha-o aqui para a sua requisição AJAX/Fetch rodar normalmente.
            // event.preventDefault(); 

            // Se estiver no mobile, fecha o modal logo após o envio
            if (window.innerWidth <= 768) {
                fecharModalMobile();
            }
        }
    });

    // Execução inicial e monitoramento de redimensionamento
    window.addEventListener('resize', gerenciarLayoutFormulario);
    gerenciarLayoutFormulario();
});