/**
 * Gerenciamento de interações com a página de rota
 */
$(document).ready(function () {
  // Inicializar tooltips
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // CSRF Token - Obter do meta tag ou da variável global definida no base.html
  const csrfToken =
    window.csrfToken ||
    $('meta[name="csrf-token"]').attr('content') ||
    $('input[name="csrf_token"]').val();

  console.log('CSRF Token disponível:', !!csrfToken);

  // Obter dados da rota do elemento data
  const routeDataElement = document.getElementById('route-data');
  if (!routeDataElement) {
    console.error('Elemento route-data não encontrado');
    return;
  }

  const routeId = routeDataElement.getAttribute('data-route-id');
  const isRouteCompleted =
    routeDataElement.getAttribute('data-completed') === 'true';

  // Verificar se geolocalização está disponível
  const isGeoAvailable = GeoLocationUtils.isGeolocationAvailable();

  const returnToStart = $('#returnToStartCheckbox').is(':checked'); // Assuming the checkbox has this ID
  console.log('returnToStart value:', returnToStart);

  console.log('Route', {
    routeId: routeId,
    isCompleted: isRouteCompleted,
    geoAvailable: isGeoAvailable,
  });

  // Definir a função haversineDistance caso não esteja disponível
  if (typeof haversineDistance !== 'function') {
    window.haversineDistance = function (point1, point2) {
      // Converter para números
      const lat1 = parseFloat(point1.latitude);
      const lon1 = parseFloat(point1.longitude);
      const lat2 = parseFloat(point2.latitude);
      const lon2 = parseFloat(point2.longitude);

      // Raio da Terra em metros
      const R = 6371000;

      // Converter graus para radianos
      const lat1Rad = (lat1 * Math.PI) / 180;
      const lon1Rad = (lon1 * Math.PI) / 180;
      const lat2Rad = (lat2 * Math.PI) / 180;
      const lon2Rad = (lon2 * Math.PI) / 180;

      // Diferença de latitude e longitude
      const dLat = lat2Rad - lat1Rad;
      const dLon = lon2Rad - lon1Rad;

      // Fórmula de Haversine
      const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1Rad) *
          Math.cos(lat2Rad) *
          Math.sin(dLon / 2) *
          Math.sin(dLon / 2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      const distance = R * c;

      return distance;
    };
  }

  // Obter a base URL para requisições AJAX
  const baseURL = window.location.origin; // http://127.0.0.1:5000 ou qualquer que seja o endereço atual

  // Gerenciar check-in
  $('.check-in-btn').on('click', function () {
    const locationId = $(this).data('location-id');
    const latitude = $(this).data('lat');
    const longitude = $(this).data('lon');

    console.log('Check-in button clicked', { locationId, latitude, longitude });

    // Verificar se geolocalização está disponível
    if (!isGeoAvailable) {
      toastr.error(
        'Seu navegador não suporta geolocalização. Não é possível fazer check-in.',
      );
      return;
    }

    // Solicitar posição atual do usuário
    navigator.geolocation.getCurrentPosition(
      function (position) {
        const userLat = position.coords.latitude;
        const userLon = position.coords.longitude;

        console.log('User position obtained', { userLat, userLon });

        // Enviar requisição para check-in
        sendCheckInRequest(locationId, userLat, userLon);
      },
      function (error) {
        console.error('Geolocation error:', error);
        toastr.error(
          'Não foi possível obter sua localização. Tente novamente ou verifique as permissões do navegador.',
        );
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    );
  });

  // Gerenciar check-out
  $('.check-out-btn').on('click', function () {
    const locationId = $(this).data('location-id');
    console.log('Check-out button clicked', { locationId });

    sendCheckOutRequest(locationId);
  });

  // Gerenciar toggle de visita
  $('.toggle-visited-btn').on('click', function () {
    const locationId = $(this).data('location-id');
    const latitude = $(this).data('lat');
    const longitude = $(this).data('lon');

    console.log('Toggle visited button clicked', {
      locationId,
      latitude,
      longitude,
    });

    // Verificar se geolocalização está disponível
    if (!isGeoAvailable) {
      toastr.error(
        'Seu navegador não suporta geolocalização. Não é possível marcar como visitado.',
      );
      return;
    }

    // Solicitar posição atual do usuário
    navigator.geolocation.getCurrentPosition(
      function (position) {
        const userLat = position.coords.latitude;
        const userLon = position.coords.longitude;

        console.log('User position obtained for toggle', { userLat, userLon });

        // Calcular distância
        const distance = haversineDistance(
          { latitude: userLat, longitude: userLon },
          { latitude: latitude, longitude: longitude },
        );

        // Verificar se usuário está próximo o suficiente (100 metros)
        if (distance > 100) {
          toastr.warning(
            `Você está a ${distance.toFixed(
              0,
            )} metros do local. Aproxime-se para marcar como visitado.`,
          );
          return;
        }

        // Enviar requisição para alternar status de visita
        toggleVisitedStatus(locationId);
      },
      function (error) {
        console.error('Geolocation error:', error);
        toastr.error(
          'Não foi possível obter sua localização. Tente novamente ou verifique as permissões do navegador.',
        );
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    );
  });

  // Gerenciar otimização da rota - apenas abrir o modal, não iniciar otimização
  $('#optimizeBtn').on('click', function () {
    // Apenas abre o modal definido no data-bs-target
    // Não faz nada mais aqui para evitar que a otimização inicie automaticamente
  });

  // Event handler para o botão DENTRO do modal de otimização
  $('#optimizeRouteForm').on('submit', function (e) {
    //e.preventDefault();
    console.log('Form submitted!'); // Debugging
    const routeId = getRouteId();
    if (routeId) {
      // Get the value of the return to start checkbox
      const returnToStart = $('#returnToStartCheckbox').is(':checked'); // Assuming the checkbox has this ID

      // Fecha o modal de otimização
      $('#optimizeRouteModal').modal('hide');
      // Inicia a otimização
      console.log('returnToStart value:', returnToStart); // Debugging
      alert('Optimize button clicked!'); // Debugging
      optimizeRoute(routeId, returnToStart); // Pass the returnToStart value

      // Mostra mensagem de sucesso
      toastr.success('Otimização iniciada com sucesso!');

      // Recarrega a página após 2 segundos
      setTimeout(function () {
        window.location.reload();
      }, 2000);
    } else {
      toastr.error('ID da rota não encontrado');
    }
  });

  // Remover o event handler incorreto para o trigger-optimize
  $(document).off('click', '[data-trigger-optimize]');

  // Função para verificar status de otimização
  function checkOptimizationStatus() {
    setTimeout(function () {
      $.ajax({
        url: `/routes/${routeId}/optimization-status`,
        type: 'GET',
        success: function (response) {
          if (response.status === 'optimized') {
            toastr.success('Otimização concluída com sucesso!');
            location.reload();
          } else if (response.status === 'optimizing') {
            // Continuar verificando
            checkOptimizationStatus();
          } else if (response.status === 'failed') {
            toastr.error('Falha na otimização: ' + response.message);
          }
        },
        error: function () {
          console.error('Error checking optimization status');
        },
      });
    }, 5000); // Verificar a cada 5 segundos
  }

  // Gerenciar alteração de ponto de partida
  $('#getLocationBtn').on('click', function () {
    if (!isGeoAvailable) {
      toastr.error('Seu navegador não suporta geolocalização.');
      return;
    }

    $('#geo-status')
      .removeClass('alert-info alert-danger')
      .addClass('alert-warning');
    $('#geo-message').text('Obtendo sua localização...');

    navigator.geolocation.getCurrentPosition(
      function (position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        $('#geo-latitude').val(lat);
        $('#geo-longitude').val(lon);
        $('#geo-status').removeClass('alert-warning').addClass('alert-success');
        $('#geo-message').text('Localização obtida com sucesso!');
        $('#geo-position-display').show();
        $('#geo-save-btn').prop('disabled', false);
      },
      function (error) {
        $('#geo-status').removeClass('alert-warning').addClass('alert-danger');
        $('#geo-message').text('Erro ao obter localização: ' + error.message);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    );
  });

  // Salvar ponto de partida com geolocalização
  $('#geo-save-btn').on('click', function () {
    const latitude = $('#geo-latitude').val();
    const longitude = $('#geo-longitude').val();
    const optimize = $('#geo-optimize').is(':checked');

    saveStartingPoint(latitude, longitude, 'Minha Localização', optimize);
    // Forçar o recarregamento da página
    setTimeout(() => {
      window.location.reload();
    }, 2000);
  });

  // Salvar ponto de partida manual
  $('#manual-save-btn').on('click', function () {
    const latitude = $('#manual-latitude').val();
    const longitude = $('#manual-longitude').val();
    const name = $('#manual-name').val() || 'Ponto de Partida';
    const optimize = $('#manual-optimize').is(':checked');

    if (!latitude || !longitude) {
      toastr.error('Por favor, informe latitude e longitude válidas.');
      return;
    }

    saveStartingPoint(latitude, longitude, name, optimize);
    // Forçar o recarregamento da página
    window.location.reload();
  });

  // Função para enviar requisição de check-in
  function sendCheckInRequest(locationId, userLat, userLon) {
    // Obter o token CSRF novamente para garantir que está atualizado
    const csrfToken =
      $('meta[name="csrf-token"]').attr('content') ||
      $('input[name="csrf_token"]').val();

    // Exibir dados antes do envio para debug
    console.log('Enviando requisição de check-in para:', {
      locationId,
      userLat,
      userLon,
      csrfToken: csrfToken ? csrfToken.substring(0, 10) + '...' : 'null',
      routeId: routeId, // Garantir que routeId está disponível
    });

    // Verificar se temos o ID da rota
    if (!routeId) {
      toastr.error('ID da rota não encontrado');
      return;
    }

    // Verificar se temos o token CSRF
    if (!csrfToken) {
      toastr.error(
        'Token CSRF não encontrado. Recarregue a página e tente novamente.',
      );
      return;
    }

    // Usar URL relativa para evitar problemas de domínio/porta
    const url = `/routes/${routeId}/locations/${locationId}/check-in`;
    console.log('URL da requisição:', url);

    $.ajax({
      url: url,
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        latitude: userLat,
        longitude: userLon,
        csrf_token: csrfToken,
      }),
      headers: {
        'X-CSRFToken': csrfToken,
      },
      success: function (response) {
        console.log('Check-in response:', response);

        if (response.success) {
          toastr.success('Check-in realizado com sucesso!');
          // Recarregar a página para atualizar os dados
          location.reload();
        } else {
          toastr.error(response.message || 'Erro ao realizar check-in.');
        }
      },
      error: function (xhr, status, error) {
        console.error('Check-in error:', xhr);
        console.error('Status:', status);
        console.error('Error:', error);

        let errorMsg = 'Erro ao realizar check-in.';

        if (xhr.status === 403) {
          errorMsg =
            'Erro de autenticação. Tente recarregar a página e fazer login novamente.';
          console.log('Token CSRF inválido ou expirado, recarregando...');
          // Recarregar a página para obter um novo token CSRF
          setTimeout(function () {
            location.reload();
          }, 2000);
        } else if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMsg = xhr.responseJSON.message;
        } else if (status === 'error' && error === '') {
          errorMsg =
            'Erro de conexão com o servidor. Verifique sua conexão de internet.';
        }

        toastr.error(errorMsg);
      },
    });
  }

  // Helper para obter o token CSRF
  function getCsrfToken() {
    return (
      window.csrfToken ||
      $('meta[name="csrf-token"]').attr('content') ||
      $('input[name="csrf_token"]').val()
    );
  }

  // Helper para obter o ID da rota
  function getRouteId() {
    return $('#route-data').data('route-id');
  }

  // Função para enviar requisição de check-out
  function sendCheckOutRequest(locationId) {
    const routeId = getRouteId();
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    $.ajax({
      url: `/routes/${routeId}/locations/${locationId}/check-out`,
      type: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
      },
      contentType: 'application/json',
      data: JSON.stringify({
        csrf_token: csrfToken,
      }),
      success: function (response) {
        if (response.success) {
          toastr.success('Check-out realizado com sucesso!');
          // Aguardar a mensagem de sucesso aparecer antes de recarregar
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        } else {
          toastr.error(response.message || 'Erro ao realizar check-out');
        }
      },
      error: function (xhr, status, error) {
        console.error('Erro ao processar check-out:', error);
        console.error('Status:', status);
        console.error('XHR:', xhr);

        let errorMsg = 'Erro ao processar check-out';
        if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMsg = xhr.responseJSON.message;
        }
        toastr.error(errorMsg);
      },
    });
  }

  // Função para alternar status de visita
  function toggleVisitedStatus(locationId) {
    const routeId = getRouteId();
    // Obter o token CSRF novamente para garantir que está atualizado
    const csrfToken =
      $('meta[name="csrf-token"]').attr('content') ||
      $('input[name="csrf_token"]').val();

    if (!routeId) {
      toastr.error('ID da rota não encontrado');
      return;
    }

    // Verificar se temos o token CSRF
    if (!csrfToken) {
      toastr.error(
        'Token CSRF não encontrado. Recarregue a página e tente novamente.',
      );
      return;
    }

    // Usar URL relativa para evitar problemas de domínio/porta
    const url = `/routes/${routeId}/route_points/${locationId}/toggle-visited`;
    console.log('Enviando requisição para alternar status:', url);

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
        console.log('Toggle visited response:', response);

        if (response.success) {
          toastr.success('Status de visita alterado com sucesso!');
          // Recarregar a página para atualizar os dados
          location.reload();
        } else {
          toastr.error(response.message || 'Erro ao alterar status de visita.');
        }
      },
      error: function (xhr, status, error) {
        console.error('Toggle visited error:', xhr);
        console.error('Status:', status);
        console.error('Error:', error);

        let errorMsg = 'Erro ao alterar status de visita.';

        if (xhr.status === 403) {
          errorMsg =
            'Erro de autenticação. Tente recarregar a página e fazer login novamente.';
          console.log('Token CSRF inválido ou expirado, recarregando...');
          // Recarregar a página para obter um novo token CSRF
          setTimeout(function () {
            location.reload();
          }, 2000);
        } else if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMsg = xhr.responseJSON.message;
        } else if (status === 'error' && error === '') {
          errorMsg =
            'Erro de conexão com o servidor. Verifique sua conexão de internet.';
        }

        toastr.error(errorMsg);
      },
    });
  }

  // Função para otimizar a rota
  function optimizeRoute(routeId, returnToStart) {
    // Add returnToStart as a parameter
    console.log('optimizeRoute function called'); // Debugging
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
    const url = `/routes/${routeId}/optimize`;
    console.log('Enviando requisição para otimizar rota:', url);

    // Desabilitar o botão de otimização e atualizar seu texto
    $('#optimizeBtn')
      .prop('disabled', true)
      .html('<i class="fas fa-cog fa-spin"></i> Otimizando...')
      .addClass('disabled');

    // Mostrar mensagem de início da otimização
    toastr.info(
      'Iniciando otimização da rota. Este processo pode levar alguns minutos...',
      null,
      {
        timeOut: 0,
        extendedTimeOut: 0,
        closeButton: true,
        tapToDismiss: false,
      },
    );

    // Atualizar o status de otimização na interface
    $('#optimization-status-badge')
      .removeClass('bg-success bg-secondary')
      .addClass('bg-warning')
      .text('Em otimização...');

    $.ajax({
      url: url,
      type: 'POST',
      contentType: 'application/json',
      headers: {
        'X-CSRFToken': csrfToken,
      },
      data: JSON.stringify({
        csrf_token: csrfToken,
        return_to_start: returnToStart, // Enviar o valor do checkbox
      }),
      success: function (response) {
        toastr.clear(); // Limpar mensagens anteriores

        if (response.success) {
          toastr.success(response.message || 'Rota otimizada com sucesso!');

          // Atualizar a aparência do botão temporariamente
          $('#optimizeBtn')
            .html('<i class="fas fa-check"></i> Otimizado')
            .removeClass('btn-info')
            .addClass('btn-success');

          // Atualizar o status da rota na interface
          $('#optimization-status-badge')
            .removeClass('bg-warning bg-secondary')
            .addClass('bg-success')
            .text('Otimizada');

          // Atualizar a data de otimização
          const now = new Date();
          $('#optimized-at-date').text(now.toLocaleString());

          // Recarregar a página após um breve atraso
          setTimeout(function () {
            window.location.href = response.redirect;
          }, 1500);
        } else {
          toastr.error(response.message || 'Erro ao otimizar a rota');

          // Resetar o botão de otimização
          $('#optimizeBtn')
            .prop('disabled', false)
            .html('<i class="fas fa-route"></i> Otimizar Rota')
            .removeClass('disabled');

          // Atualizar o status da rota
          $('#optimization-status-badge')
            .removeClass('bg-warning')
            .addClass('bg-secondary')
            .text('Não otimizada');
        }
      },
      error: function (xhr, status, error) {
        console.error('Optimize error:', xhr);
        console.error('Status:', status);
        console.error('Error:', error);

        toastr.clear(); // Limpar mensagens anteriores

        let errorMsg = 'Erro ao otimizar a rota';

        if (xhr.status === 403) {
          errorMsg =
            'Erro de autenticação. Tente recarregar a página e fazer login novamente.';
          console.log('Token CSRF inválido ou expirado, recarregando...');
          // Recarregar a página para obter um novo token CSRF
          setTimeout(function () {
            location.reload();
          }, 2000);
        } else if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMsg = xhr.responseJSON.message;
        } else if (status === 'error' && error === '') {
          errorMsg =
            'Erro de conexão com o servidor. Verifique sua conexão de internet.';
        }

        toastr.error(errorMsg);

        // Resetar o botão de otimização
        $('#optimizeBtn')
          .prop('disabled', false)
          .html('<i class="fas fa-route"></i> Otimizar Rota')
          .removeClass('disabled');

        // Atualizar o status da rota
        $('#optimization-status-badge')
          .removeClass('bg-warning')
          .addClass('bg-secondary')
          .text('Não otimizada');
      },
    });
  }

  // Função para salvar ponto de partida
  function saveStartingPoint(latitude, longitude, name, optimize) {
    const routeId = getRouteId();
    // Obter o token CSRF novamente para garantir que está atualizado
    const csrfToken =
      $('meta[name="csrf-token"]').attr('content') ||
      $('input[name="csrf_token"]').val();

    if (!routeId) {
      toastr.error('ID da rota não encontrado');
      return;
    }

    // Verificar se temos o token CSRF
    if (!csrfToken) {
      toastr.error(
        'Token CSRF não encontrado. Recarregue a página e tente novamente.',
      );
      return;
    }

    // Mostrar mensagem de processamento
    toastr.info('Salvando ponto de partida...');

    // Desabilitar botões para evitar múltiplos cliques
    $('#geo-save-btn').prop('disabled', true);
    $('#manual-save-btn').prop('disabled', true);

    // Usar URL relativa para evitar problemas de domínio/porta
    const url = `/routes/${routeId}/change-starting-point`;
    console.log('Enviando requisição para alterar ponto de partida:', url);

    $.ajax({
      url: url,
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        latitude: latitude,
        longitude: longitude,
        name: name,
        optimize: optimize,
        csrf_token: csrfToken,
      }),
      headers: {
        'X-CSRFToken': csrfToken,
      },
      success: function (response) {
        console.log('Save starting point response:', response);

        if (response.success) {
          toastr.success('Ponto de partida alterado com sucesso!');

          // Fechar o modal
          $('#changeStartingPointModal').modal('hide');

          // Recarregar a página imediatamente
          location.reload();
        } else {
          // Reativar botões em caso de erro
          $('#geo-save-btn').prop('disabled', false);
          $('#manual-save-btn').prop('disabled', false);
          toastr.error(response.message || 'Erro ao alterar ponto de partida.');
        }
      },
      error: function (xhr, status, error) {
        console.error('Save starting point error:', xhr);
        console.error('Status:', status);
        console.error('Error:', error);

        // Reativar botões em caso de erro
        $('#geo-save-btn').prop('disabled', false);
        $('#manual-save-btn').prop('disabled', false);

        let errorMsg = 'Erro ao alterar ponto de partida.';

        if (xhr.status === 403) {
          errorMsg =
            'Erro de autenticação. Tente recarregar a página e fazer login novamente.';
          console.log('Token CSRF inválido ou expirado, recarregando...');
          // Recarregar a página para obter um novo token CSRF
          setTimeout(function () {
            location.reload();
          }, 2000);
        } else if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMsg = xhr.responseJSON.message;
        } else if (status === 'error' && error === '') {
          errorMsg =
            'Erro de conexão com o servidor. Verifique sua conexão de internet.';
        }

        toastr.error(errorMsg);
      },
    });
  }

  // Função para atualizar o contador de progresso
  function updateProgressCounter() {
    const totalPoints = $('.list-group-item').length - 1; // -1 para excluir o ponto de partida
    const visitedPoints = $('.list-group-item-success').length - 1;
    const percent = (visitedPoints / totalPoints) * 100;

    $('.progress-bar')
      .css('width', percent + '%')
      .attr('aria-valuenow', percent);
    $('.progress-bar').text(Math.round(percent) + '%');
    $('.visited-count').text(visitedPoints);
    $('.total-count').text(totalPoints);
  }

  // Função para salvar a rota como template
  function saveAsTemplate(routeId) {
    if (confirm('Deseja salvar esta rota como template?')) {
      fetch(`/routes/${routeId}/save-template`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')
            .content,
        },
        credentials: 'same-origin',
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            alert(data.message);
            window.location.href = '/templates';
          } else {
            alert(data.message || 'Erro ao salvar template');
          }
        })
        .catch((error) => {
          console.error('Erro:', error);
          alert('Erro ao salvar template');
        });
    }
  }

  // Função para criar rota a partir de template
  function createFromTemplate(templateId) {
    if (confirm('Deseja criar uma nova rota a partir deste template?')) {
      fetch(`/templates/${templateId}/create-route`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')
            .content,
        },
        credentials: 'same-origin',
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            window.location.href = data.redirect_url;
          } else {
            alert(data.message || 'Erro ao criar rota');
          }
        })
        .catch((error) => {
          console.error('Erro:', error);
          alert('Erro ao criar rota');
        });
    }
  }

  // Função para excluir template
  function deleteTemplate(templateId) {
    if (confirm('Tem certeza que deseja excluir este template?')) {
      fetch(`/route/template/${templateId}/delete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')
            .content,
        },
        credentials: 'same-origin',
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            window.location.reload();
          } else {
            alert(data.message || 'Erro ao excluir template');
          }
        })
        .catch((error) => {
          console.error('Erro:', error);
          alert('Erro ao excluir template');
        });
    }
  }
});
