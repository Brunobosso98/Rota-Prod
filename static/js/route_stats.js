/**
 * Funções para carregar e exibir estatísticas de rota
 */
$(document).ready(function() {
    // Popover para exibir tempos detalhados
    $('[data-toggle="popover"]').popover();

    // Função para carregar estatísticas da rota
    function loadRouteStats(routeId) {
        $.ajax({
            url: `/routes/${routeId}/stats`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    updateStatsDisplay(response);
                } else {
                    toastr.error('Erro ao carregar estatísticas da rota.');
                }
            },
            error: function(xhr, status, error) {
                console.error('Erro ao carregar estatísticas da rota:', error);
                toastr.error('Erro ao carregar estatísticas da rota.');
            }
        });
    }

    // Função para atualizar display com as estatísticas
    function updateStatsDisplay(data) {
        $('#stats-avg-work-time').text(data.avg_work_time + ' min');
        $('#stats-avg-transit-time').text(data.avg_transit_time + ' min');
        $('#stats-total-work-time').text(data.total_work_time + ' min');
        $('#stats-total-transit-time').text(data.total_transit_time + ' min');
        
        // Calcular tempo total
        const totalTime = data.total_work_time + data.total_transit_time;
        $('#stats-total-time').text(totalTime + ' min');
        
        // Calcular eficiência
        const efficiency = data.total_transit_time > 0 ? 
            (data.total_work_time / data.total_transit_time).toFixed(2) : 'N/A';
        $('#stats-efficiency').text(efficiency);
        
        // Limpar e popular tabela de locais
        const locationsTable = $('#stats-locations-table tbody');
        locationsTable.empty();
        
        if (data.locations && data.locations.length > 0) {
            data.locations.forEach(function(loc) {
                let workTime = loc.work_time !== null ? loc.work_time + ' min' : 'N/A';
                let transitTime = loc.transit_time !== null ? loc.transit_time + ' min' : 'N/A';
                
                locationsTable.append(`
                    <tr>
                        <td>${loc.order}</td>
                        <td>${loc.name}</td>
                        <td>${loc.check_in_at || 'N/A'}</td>
                        <td>${loc.check_out_at || 'N/A'}</td>
                        <td>${workTime}</td>
                        <td>${transitTime}</td>
                    </tr>
                `);
            });
        } else {
            locationsTable.append(`
                <tr>
                    <td colspan="6" class="text-center">Nenhum dado disponível</td>
                </tr>
            `);
        }
    }

    // Carregar estatísticas quando botão for clicado
    $('.view-stats-btn').on('click', function() {
        const routeId = $(this).data('route-id');
        loadRouteStats(routeId);
    });
}); 