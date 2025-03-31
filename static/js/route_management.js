// Script para gerenciar locais visitados nas rotas
$(document).ready(function () {
  // Função para marcar/desmarcar local como visitado
  $('.toggle-visited').on('click', function (e) {
    e.preventDefault();
    var btn = $(this);
    var routeId = btn.data('route-id');
    var locationId = btn.data('location-id');

    console.log("Enviando requisição para marcar/desmarcar local como visitado");
    console.log("Route ID:", routeId);
    console.log("Location ID:", locationId);

    $.ajax({
      url: '/routes/' + routeId + '/locations/' + locationId + '/toggle_visited',
      type: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
      },
      success: function (response) {
        console.log("Resposta recebida:", response);
        if (response.success) {
          // Atualizar estado do botão
          if (response.visited) {
            btn.removeClass('btn-secondary').addClass('btn-success');
            btn.find('i').removeClass('fa-square').addClass('fa-check-square');
            btn.closest('.list-group-item').addClass('list-group-item-success');
            btn.html('<i class="fas fa-check-square"></i> Visitado');
          } else {
            btn.removeClass('btn-success').addClass('btn-secondary');
            btn.find('i').removeClass('fa-check-square').addClass('fa-square');
            btn
              .closest('.list-group-item')
              .removeClass('list-group-item-success');
            btn.html('<i class="fas fa-square"></i> Marcar como visitado');
          }

          // Se a rota foi concluída, atualizar a interface
          if (response.route_completed) {
            $('#route-status')
              .removeClass('badge-warning')
              .addClass('badge-success')
              .html('<i class="fas fa-check"></i> Concluída');

            // Esconder botão de concluir rota se existir
            $('.complete-route-btn').hide();
          } else {
            $('#route-status')
              .removeClass('badge-success')
              .addClass('badge-warning')
              .html('<i class="fas fa-clock"></i> Em andamento');

            // Mostrar botão de concluir rota se existir
            $('.complete-route-btn').show();
          }
          
          // Recarregar a página para atualizar o mapa
          // Isso garante que os marcadores no mapa sejam atualizados
          setTimeout(function() {
            location.reload();
          }, 1000); // Recarrega após 1 segundo
        }
      },
      error: function (xhr, status, error) {
        console.error("Erro ao atualizar status:", error);
        console.error("Status:", status);
        console.error("Resposta:", xhr.responseText);
        // alert('Ocorreu um erro ao atualizar o status do local.');
      },
    });
  });

  // Inicializar token CSRF a partir de um elemento meta
  var csrfToken = $('meta[name="csrf-token"]').attr('content');
});
