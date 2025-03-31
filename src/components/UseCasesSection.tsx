
import React from 'react';
import { BadgeCheck, Truck, ShoppingBag, Wrench, Briefcase } from 'lucide-react';
import { Button } from "@/components/ui/button";

const UseCasesSection = () => {
  const useCases = [
    {
      icon: <ShoppingBag className="h-10 w-10 text-kodiak-600" />,
      title: 'Equipes de Vendas',
      description: 'Maximize a produtividade de vendedores externos com rotas otimizadas para visitar mais clientes em menos tempo. Controle de metas e monitoramento em tempo real.',
      benefits: [
        'Mais visitas por dia',
        'Controle de produtividade',
        'Gestão de carteira de clientes',
        'Redução de custos com deslocamento'
      ]
    },
    {
      icon: <Truck className="h-10 w-10 text-kodiak-600" />,
      title: 'Serviços de Entrega',
      description: 'Otimize entregas para reduzir custos e aumentar a satisfação do cliente com previsões de horário precisas. Confirmação de entregas e comprovante fotográfico.',
      benefits: [
        'Menor custo por entrega',
        'Rastreamento em tempo real',
        'Comprovante digital de entrega',
        'Sequência otimizada de entregas'
      ]
    },
    {
      icon: <Wrench className="h-10 w-10 text-kodiak-600" />,
      title: 'Assistência Técnica',
      description: 'Reduza o tempo de resposta e atenda mais chamados por dia com rotas organizadas por prioridade, geografia e janelas de tempo para atendimento.',
      benefits: [
        'Priorização inteligente de chamados',
        'Redução no tempo de resposta',
        'Histórico de atendimentos',
        'Registro detalhado de serviços'
      ]
    },
    {
      icon: <Briefcase className="h-10 w-10 text-kodiak-600" />,
      title: 'Equipes de Manutenção',
      description: 'Gerencie visitas periódicas ou emergenciais de manutenção com maior eficiência, garantindo cumprimento de SLAs e maximizando a produtividade das equipes.',
      benefits: [
        'Controle de SLAs',
        'Agendamento inteligente',
        'Gestão de equipamentos e peças',
        'Relatórios de manutenção com fotos'
      ]
    }
  ];

  return (
    <section id="casos-de-uso" className="section-padding bg-gray-50">
      <div className="container mx-auto container-padding">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="mb-4">Casos de <span className="text-kodiak-600">Uso</span></h2>
          <p className="text-lg text-gray-600">
            O Rotas Kodiak é versátil e atende diferentes setores e necessidades. Conheça alguns dos 
            principais casos de uso da nossa plataforma.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {useCases.map((useCase, index) => (
            <div 
              key={index}
              className="bg-white rounded-lg overflow-hidden shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="bg-kodiak-50 p-3 rounded-full w-fit mb-5">
                  {useCase.icon}
                </div>
                <h3 className="text-xl font-semibold mb-3">{useCase.title}</h3>
                <p className="text-gray-600 mb-6">{useCase.description}</p>
                
                <h4 className="text-lg font-medium mb-3">Principais Benefícios:</h4>
                <ul className="space-y-2 mb-6">
                  {useCase.benefits.map((benefit, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <BadgeCheck className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="bg-gray-50 px-6 py-4 border-t border-gray-100">
                <Button variant="outline" className="w-full border-kodiak-600 text-kodiak-600 hover:bg-kodiak-50">
                  Ver Demonstração
                </Button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-16 bg-gradient-to-r from-kodiak-600 to-kodiak-800 rounded-lg p-8 text-white">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-2xl font-bold mb-4">Não tem certeza se o Rotas Kodiak é para você?</h3>
              <p className="text-white/90 mb-4">
                Converse com um dos nossos especialistas e descubra como podemos personalizar nossa solução para seu negócio.
              </p>
              <Button className="bg-white text-kodiak-700 hover:bg-gray-100">
                Agende uma Consultoria Gratuita
              </Button>
            </div>
            
            <div className="space-y-3">
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 flex items-start gap-3">
                <BadgeCheck className="h-6 w-6 text-green-300 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-medium text-lg mb-1">Solução Personalizada</h4>
                  <p className="text-white/80">Adaptamos a plataforma para atender às necessidades específicas do seu negócio.</p>
                </div>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 flex items-start gap-3">
                <BadgeCheck className="h-6 w-6 text-green-300 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-medium text-lg mb-1">Onboarding Completo</h4>
                  <p className="text-white/80">Treinamento e suporte para garantir que sua equipe aproveite ao máximo a plataforma.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default UseCasesSection;
