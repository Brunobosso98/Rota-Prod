// Variáveis globais
let selectedTemplateId = null;

// Função global para carregar pontos do template
async function loadTemplatePoints(templateId) {
    console.log('Iniciando loadTemplatePoints com templateId:', templateId);
    try {
        const response = await fetch(`/templates/${templateId}/points`);
        console.log('Resposta da API:', response);
        const data = await response.json();
        console.log('Dados recebidos:', data);
        
        const pointsList = document.getElementById('routePointsList');
        if (!pointsList) {
            console.error('Elemento routePointsList não encontrado!');
            return;
        }
        
        pointsList.innerHTML = '';
        
        data.points.forEach((point) => {
            console.log('Renderizando ponto:', point);
            pointsList.innerHTML += `
                <tr data-point-id="${point.id}" data-order="${point.order}">
                    <td>${point.order}</td>
                    <td>${point.name}</td>
                    <td>${point.city}</td>
                    <td>${point.state}</td>
                    <td>
                        ${point.order === 0 ? 
                            '<span class="text-muted"><i class="fas fa-lock"></i> Ponto de Partida</span>' :
                            `<button class="btn btn-sm btn-danger" onclick="removePoint(${point.id}, ${templateId})">
                                <i class="fas fa-trash"></i>
                            </button>`
                        }
                    </td>
                </tr>
            `;
        });
    } catch (error) {
        console.error('Erro detalhado ao carregar pontos:', error);
    }
}

// Função para carregar locais disponíveis
async function loadAvailableLocations() {
    try {
        const response = await fetch('/locations/available');
        const data = await response.json();
        const locationSelect = document.getElementById('locationSelect');
        locationSelect.innerHTML = '<option value="">Selecione um local...</option>';
        
        data.locations.forEach(location => {
            locationSelect.innerHTML += `
                <option value="${location.id}">${location.name} - ${location.city}/${location.state}</option>
            `;
        });
    } catch (error) {
        console.error('Erro ao carregar locais:', error);
    }
}

// Event listener para adicionar novo local
const addLocationBtn = document.getElementById('addLocationBtn');
if (addLocationBtn) {
    addLocationBtn.addEventListener('click', function() {
        const addLocationModal = new bootstrap.Modal(document.getElementById('addLocationModal'));
        addLocationModal.show();
    });
}

// Event listener para confirmar adição de local
const confirmAddLocation = document.getElementById('confirmAddLocation');
if (confirmAddLocation) {
    confirmAddLocation.addEventListener('click', async function() {
        const locationSelect = document.getElementById('locationSelect');
        const locationId = locationSelect.value;
        
        if (!locationId) {
            alert('Por favor, selecione um local');
            return;
        }

        try {
            const response = await fetch(`/templates/${selectedTemplateId}/points`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({ location_id: locationId })
            });

            const data = await response.json();
            if (data.success) {
                loadTemplatePoints(selectedTemplateId);
                bootstrap.Modal.getInstance(document.getElementById('addLocationModal')).hide();
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Erro ao adicionar local:', error);
            alert('Erro ao adicionar local');
        }
    });
}

// Event listener para confirmar criação de rota
const confirmCreateRoute = document.getElementById('confirmCreateRoute');
if (confirmCreateRoute) {
    confirmCreateRoute.addEventListener('click', async function() {
        const newName = document.getElementById('newRouteName').value.trim();

        if (!newName) {
            alert('Por favor, insira um nome para a nova rota');
            return;
        }

        try {
            const response = await fetch(`/templates/${selectedTemplateId}/create-route`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({
                    name: newName
                })
            });

            const data = await response.json();
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert(data.message || 'Erro ao criar rota');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao criar rota');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Template interactions script carregado');
    
    const modalElement = document.getElementById('newRouteNameModal');
    if (!modalElement) {
        console.error('Modal element not found');
        return;
    }

    const modal = new bootstrap.Modal(modalElement);

    document.querySelectorAll('.create-template-btn').forEach(button => {
        button.addEventListener('click', function() {
            selectedTemplateId = this.dataset.templateId;
            console.log('Template selecionado:', selectedTemplateId);
            modal.show();
            loadTemplatePoints(selectedTemplateId);
            loadAvailableLocations();
        });
    });
});

// Função global para deletar template
function deleteTemplate(templateId) {
    if (confirm('Tem certeza que deseja excluir este template?')) {
        fetch(`/templates/${templateId}/delete`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                alert(data.message || 'Erro ao excluir template');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao excluir template');
        });
    }
}

// Função global para remover ponto
function removePoint(pointId, templateId) {
    console.log('Iniciando removePoint:', { pointId, templateId });
    
    const pointElement = document.querySelector(`tr[data-point-id="${pointId}"]`);
    const pointOrder = pointElement?.getAttribute('data-order');
    
    if (pointOrder === '0') {
        alert('Não é possível remover o ponto de partida.');
        return;
    }
    
    if (!confirm('Tem certeza que deseja remover este ponto?')) {
        console.log('Remoção cancelada pelo usuário');
        return;
    }
    
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    
    fetch(`/templates/${templateId}/points/${pointId}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        console.log('Resposta do servidor:', response);
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Ponto removido com sucesso, recarregando pontos...');
            loadTemplatePoints(templateId);
        } else {
            alert(data.message || 'Erro ao remover o ponto');
        }
    })
    .catch(error => {
        console.error('Erro detalhado na remoção:', error);
        alert('Erro ao remover ponto');
    });
}





