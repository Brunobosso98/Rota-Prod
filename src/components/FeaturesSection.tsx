
import React from 'react';
import { AlertCircle, BarChart3, Clock, Map, Repeat, Route, Smartphone, Upload, UserCog, Users } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const FeaturesSection = () => {
  const mainFeatures = [
    {
      icon: <Route className="h-8 w-8 text-kodiak-600" />,
      title: 'Otimização Inteligente',
      description: 'Algoritmos avançados (OR-Tools e OSRM) para calcular as melhores sequências de visitas, economizando até 30% em tempo e combustível.'
    },
    {
      icon: <UserCog className="h-8 w-8 text-kodiak-600" />,
      title: 'Hierarquia de Usuários',
      description: 'Sistema completo para empresas de qualquer tamanho com níveis de acesso para administradores, gerentes e vendedores.'
    },
    {
      icon: <BarChart3 className="h-8 w-8 text-kodiak-600" />,
      title: 'Relatórios Detalhados',
      description: 'Análise completa de performance de equipes, tempos de visita, distâncias percorridas e eficiência das rotas.'
    },
    {
      icon: <Upload className="h-8 w-8 text-kodiak-600" />,
      title: 'Importação em Massa',
      description: 'Importe centenas de pontos via Excel com apenas alguns cliques e otimize todas as suas rotas automaticamente.'
    },
    {
      icon: <Map className="h-8 w-8 text-kodiak-600" />,
      title: 'Monitoramento em Tempo Real',
      description: 'Acompanhe a localização e progresso das suas equipes em campo com atualizações em tempo real.'
    },
    {
      icon: <Smartphone className="h-8 w-8 text-kodiak-600" />,
      title: 'Interface Adaptativa',
      description: 'Acesse pelo computador ou celular com uma interface otimizada para cada dispositivo.'
    }
  ];

  const userRoles = [
    {
      role: 'admin',
      title: 'Administradores',
      description: 'Controle total da plataforma, com acesso a todas as funcionalidades, equipes e relatórios.',
      features: [
        'Gestão completa de usuários e permissões',
        'Acesso a relatórios completos da empresa',
        'Configuração de parâmetros do sistema',
        'Importação e exportação de dados',
        'Gerenciamento de integrações',
        'Visualização e edição global de rotas'
      ]
    },
    {
      role: 'manager',
      title: 'Gerentes',
      description: 'Gerencie equipes, crie e otimize rotas, acompanhe a performance e gere relatórios.',
      features: [
        'Criação e otimização de rotas',
        'Monitoramento de equipes em tempo real',
        'Relatórios de performance da equipe',
        'Ajustes de rotas em andamento',
        'Comunicação com equipe externa',
        'Gestão de visitas e atendimentos'
      ]
    },
    {
      role: 'field',
      title: 'Equipe de Campo',
      description: 'App móvel intuitivo para execução de rotas, check-ins, registros e navegação.',
      features: [
        'Visualização da rota otimizada',
        'Check-in e check-out nos pontos de visita',
        'Registro de atividades e ocorrências',
        'Navegação integrada com Google Maps',
        'Comunicação com central/gerentes',
        'Modo offline para áreas sem cobertura'
      ]
    }
  ];

  return (
    <section id="recursos" className="section-padding bg-white">
      <div className="container mx-auto container-padding">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="mb-4">Recursos <span className="text-kodiak-600">Avançados</span></h2>
          <p className="text-lg text-gray-600">
            Nossa plataforma oferece ferramentas poderosas para otimização de rotas e gestão 
            completa de equipes externas, com foco em produtividade e economia.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {mainFeatures.map((feature, index) => (
            <div 
              key={index}
              className="feature-card"
            >
              <div className="bg-kodiak-50 p-3 rounded-full w-fit mb-5">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="bg-gray-50 rounded-xl p-8 mt-16">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <h3 className="text-2xl font-bold mb-4">Hierarquia Inteligente de Usuários</h3>
            <p className="text-gray-600">
              Sistema completo para empresas de qualquer tamanho, com diferentes níveis de acesso e funcionalidades.
            </p>
          </div>

          <Tabs defaultValue="admin" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-8">
              <TabsTrigger value="admin">Administradores</TabsTrigger>
              <TabsTrigger value="manager">Gerentes</TabsTrigger>
              <TabsTrigger value="field">Equipe de Campo</TabsTrigger>
            </TabsList>
            
            {userRoles.map((role) => (
              <TabsContent key={role.role} value={role.role} className="pt-4">
                <div className="grid md:grid-cols-2 gap-8 items-center">
                  <div>
                    <h4 className="text-2xl font-bold mb-3">{role.title}</h4>
                    <p className="text-gray-600 mb-6">{role.description}</p>
                    
                    <ul className="space-y-3">
                      {role.features.map((feature, i) => (
                        <li key={i} className="flex items-start gap-3">
                          <span className="bg-kodiak-100 p-1 rounded-full text-kodiak-600 mt-0.5">
                            <AlertCircle className="h-4 w-4" />
                          </span>
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200">
                    {role.role === 'admin' && (
                      <div className="p-4">
                        <div className="bg-kodiak-50 rounded-lg p-4 mb-4">
                          <h5 className="font-medium mb-2">Dashboard Administrativo</h5>
                          <div className="grid grid-cols-2 gap-3">
                            <div className="bg-white p-3 rounded border">
                              <div className="text-sm text-gray-500">Equipes</div>
                              <div className="text-2xl font-bold">12</div>
                            </div>
                            <div className="bg-white p-3 rounded border">
                              <div className="text-sm text-gray-500">Usuários</div>
                              <div className="text-2xl font-bold">48</div>
                            </div>
                            <div className="bg-white p-3 rounded border">
                              <div className="text-sm text-gray-500">Rotas Hoje</div>
                              <div className="text-2xl font-bold">35</div>
                            </div>
                            <div className="bg-white p-3 rounded border">
                              <div className="text-sm text-gray-500">Economia</div>
                              <div className="text-2xl font-bold">28%</div>
                            </div>
                          </div>
                        </div>
                        <div className="bg-gray-50 rounded-lg h-48 flex justify-center items-center p-4">
                          <div className="text-center">
                            <Users className="h-12 w-12 text-kodiak-400 mx-auto mb-2" />
                            <div className="text-gray-500">Visualização de Gestão de Usuários</div>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {role.role === 'manager' && (
                      <div className="p-4">
                        <div className="mb-4 p-2 bg-gray-50 rounded flex justify-between items-center">
                          <div className="font-medium">Equipe Sul</div>
                          <div className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">Ativa</div>
                        </div>
                        <div className="h-64 bg-gray-50 rounded-lg mb-4 p-3">
                          <div className="flex justify-between mb-2">
                            <div className="text-sm font-medium">Mapa de Progresso</div>
                            <div className="text-xs text-kodiak-600">Ao Vivo</div>
                          </div>
                          <div className="h-52 bg-blue-50 rounded relative">
                            {/* Simplified map */}
                            <div className="absolute w-3 h-3 bg-green-500 rounded-full top-1/4 left-1/3"></div>
                            <div className="absolute w-3 h-3 bg-yellow-500 rounded-full top-1/2 left-1/2"></div>
                            <div className="absolute w-3 h-3 bg-blue-500 rounded-full bottom-1/4 right-1/4"></div>
                            
                            <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M33 25 L50 50 L75 75" stroke="#0d6efd" strokeWidth="2" />
                            </svg>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="p-3 bg-gray-50 rounded">
                            <div className="text-sm text-gray-500">Visitas</div>
                            <div className="flex justify-between items-end">
                              <div className="text-xl font-bold">14/20</div>
                              <div className="text-green-500 text-xs">70%</div>
                            </div>
                            <div className="w-full h-1 bg-gray-200 rounded mt-1">
                              <div className="h-1 bg-green-500 rounded" style={{ width: "70%" }}></div>
                            </div>
                          </div>
                          <div className="p-3 bg-gray-50 rounded">
                            <div className="text-sm text-gray-500">Tempo</div>
                            <div className="flex justify-between items-end">
                              <div className="text-xl font-bold">4h 20m</div>
                              <div className="text-kodiak-600 text-xs">Em andamento</div>
                            </div>
                            <div className="w-full h-1 bg-gray-200 rounded mt-1">
                              <div className="h-1 bg-kodiak-600 rounded" style={{ width: "65%" }}></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {role.role === 'field' && (
                      <div>
                        <div className="bg-kodiak-600 text-white p-4 flex justify-between items-center">
                          <h5 className="font-medium">App Rotas Kodiak</h5>
                          <Clock className="h-5 w-5" />
                        </div>
                        <div className="p-4">
                          <div className="text-center mb-4">
                            <div className="text-sm text-gray-500">Próximo cliente</div>
                            <div className="text-xl font-bold mb-1">Supermercado Silva</div>
                            <div className="text-kodiak-600 flex items-center justify-center">
                              <Clock className="h-4 w-4 mr-1" />
                              <span>Chegada prevista: 10:30</span>
                            </div>
                          </div>
                          
                          <div className="bg-gray-50 rounded-lg h-32 mb-4 flex items-center justify-center">
                            <div className="text-center">
                              <Map className="h-8 w-8 text-kodiak-400 mx-auto mb-1" />
                              <div className="text-sm text-gray-500">Mapa de Navegação</div>
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            <div className="flex justify-between items-center bg-gray-50 p-3 rounded">
                              <div className="flex items-center">
                                <div className="bg-green-100 text-green-800 h-6 w-6 rounded-full flex items-center justify-center text-xs mr-2">1</div>
                                <span>Distribuidora ABC</span>
                              </div>
                              <div className="text-green-600 text-xs font-medium">Concluído</div>
                            </div>
                            <div className="flex justify-between items-center bg-kodiak-50 p-3 rounded border border-kodiak-100">
                              <div className="flex items-center">
                                <div className="bg-kodiak-100 text-kodiak-800 h-6 w-6 rounded-full flex items-center justify-center text-xs mr-2">2</div>
                                <span className="font-medium">Supermercado Silva</span>
                              </div>
                              <div className="text-kodiak-600 text-xs font-medium">Atual</div>
                            </div>
                            <div className="flex justify-between items-center bg-gray-50 p-3 rounded">
                              <div className="flex items-center">
                                <div className="bg-gray-200 text-gray-800 h-6 w-6 rounded-full flex items-center justify-center text-xs mr-2">3</div>
                                <span>Padaria Central</span>
                              </div>
                              <div className="text-gray-500 text-xs">Próximo</div>
                            </div>
                          </div>
                          
                          <div className="mt-4 flex gap-2">
                            <Button className="w-full bg-kodiak-600">Check-in</Button>
                            <Button variant="outline" className="w-full">Reportar</Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
