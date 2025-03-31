// Funções para gerenciar check-in e check-out
$(document).ready(function () {
  // CSRF Token - usar a variável global ou obter do meta tag ou input
  const csrfToken =
    window.csrfToken ||
    $('meta[name="csrf-token"]').attr('content') ||
    $('input[name="csrf_token"]').val();

  // Base URL para APIs
  const baseURL = window.location.origin;

  // Verificar se a rota está concluída
  const isRouteCompleted = $('#route-data').data('completed') === true;
  const routeId = $('#route-data').data('route-id');

  // Verificar se geolocalização está disponível
  const isGeoAvailable = GeoLocationUtils.isGeolocationAvailable();

  // Não definimos event handlers aqui, pois já estão em route_interactions.js
  // Este arquivo contém apenas funções auxiliares que podem ser usadas por outros scripts

  // Função para enviar requisição de check-in
  window.sendCheckInRequest = function (
    routeId,
    locationId,
    latitude,
    longitude,
    btn,
    listItem,
  ) {
    // Obter o token CSRF novamente para garantir que está atualizado
    const csrfToken =
      $('meta[name="csrf-token"]').attr('content') ||
      $('input[name="csrf_token"]').val();

    // Verificar se temos o token CSRF
    if (!csrfToken) {
      toastr.error(
        'Token CSRF não encontrado. Recarregue a página e tente novamente.',
      );
      return;
    }

    // Preparar dados da requisição
    const requestData = {
      latitude: latitude,
      longitude: longitude,
      csrf_token: csrfToken,
    };

    // Usar URL relativa para evitar problemas de domínio/porta
    const url = `/routes/${routeId}/locations/${locationId}/check-in`;

    $.ajax({
      url: url,
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(requestData),
      headers: {
        'X-CSRFToken': csrfToken,
      },
      success: function (response) {
        if (response.success) {
          // Atualiza a UI para mostrar o check-in
          toastr.success('Check-in realizado com sucesso!');

          // Recarregar a página para atualizar todos os dados
          setTimeout(function () {
            location.reload();
          }, 1500);
        } else {
          toastr.error(response.message || 'Erro ao registrar check-in.');
          if (btn)
            btn
              .prop('disabled', false)
              .html('<i class="fas fa-sign-in-alt"></i> Check-in');
        }
      },
      error: function (xhr, status, error) {
        console.error('Erro ao registrar check-in:', error);
        console.error('Status:', status);
        console.error('XHR:', xhr);

        try {
          let errorMsg = 'Erro ao registrar check-in.';

          if (xhr.status === 403) {
            errorMsg =
              'Erro de autenticação. Tente recarregar a página e fazer login novamente.';
            // Recarregar a página para obter um novo token CSRF
            setTimeout(function () {
              location.reload();
            }, 2000);
          } else if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMsg = xhr.responseJSON.message;
          } else if (xhr.status === 400) {
            const response = xhr.responseJSON || JSON.parse(xhr.responseText);
            errorMsg = response.message || 'Erro na validação da localização.';
          } else if (status === 'error' && error === '') {
            errorMsg =
              'Erro de conexão com o servidor. Verifique sua conexão de internet.';
          } else {
            errorMsg = 'Erro ao processar solicitação.';
          }

          toastr.error(errorMsg);
        } catch (e) {
          toastr.error('Erro ao processar solicitação: ' + error);
        }

        if (btn)
          btn
            .prop('disabled', false)
            .html('<i class="fas fa-sign-in-alt"></i> Check-in');
      },
    });
  };

  // Função para enviar requisição de check-out
  window.sendCheckOutRequest = function (routeId, locationId, btn, listItem) {
    // Obter o token CSRF novamente para garantir que está atualizado
    const csrfToken =
      $('meta[name="csrf-token"]').attr('content') ||
      $('input[name="csrf_token"]').val();

    // Verificar se temos o token CSRF
    if (!csrfToken) {
      toastr.error(
        'Token CSRF não encontrado. Recarregue a página e tente novamente.',
      );
      return;
    }

    // Usar URL relativa para evitar problemas de domínio/porta
    const url = `/routes/${routeId}/locations/${locationId}/check-out`;

    $.ajax({
      url: url,
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        csrf_token: csrfToken,
      }),
      headers: {
        'X-CSRFToken': csrfToken,
      },
      success: function (response) {
        if (response.success) {
          // Atualiza a UI para mostrar o check-out
          toastr.success('Check-out realizado com sucesso!');

          // Recarregar a página para atualizar todos os dados
          setTimeout(function () {
            location.reload();
          }, 1500);
        } else {
          toastr.error(response.message || 'Erro ao registrar check-out.');
          if (btn)
            btn
              .prop('disabled', false)
              .html('<i class="fas fa-sign-out-alt"></i> Check-out');
        }
      },
      error: function (xhr, status, error) {
        console.error('Erro ao registrar check-out:', error);
        console.error('Status:', status);
        console.error('XHR:', xhr);

        try {
          let errorMsg = 'Erro ao registrar check-out.';

          if (xhr.status === 403) {
            errorMsg =
              'Erro de autenticação. Tente recarregar a página e fazer login novamente.';
            // Recarregar a página para obter um novo token CSRF
            setTimeout(function () {
              location.reload();
            }, 2000);
          } else if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMsg = xhr.responseJSON.message;
          } else if (status === 'error' && error === '') {
            errorMsg =
              'Erro de conexão com o servidor. Verifique sua conexão de internet.';
          } else {
            errorMsg = 'Erro ao processar solicitação.';
          }

          toastr.error(errorMsg);
        } catch (e) {
          toastr.error('Erro ao processar solicitação: ' + error);
        }

        if (btn)
          btn
            .prop('disabled', false)
            .html('<i class="fas fa-sign-out-alt"></i> Check-out');
      },
    });
  };
});
