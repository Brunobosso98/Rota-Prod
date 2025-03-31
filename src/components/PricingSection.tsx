
import React from 'react';
import { Button } from "@/components/ui/button";
import { Check, HelpCircle } from 'lucide-react';
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const PricingSection = () => {
  const plans = [
    {
      name: 'Básico',
      description: 'Para pequenas equipes começando com otimização de rotas',
      price: 'R$97',
      period: 'por usuário/mês',
      features: [
        'Até 5 usuários',
        'Otimização básica de rotas',
        'App móvel para equipe externa',
        'Importação de pontos via Excel',
        'Confirmação de visitas',
        'Histórico de 30 dias',
        'Suporte por email'
      ],
      tooltip: 'Ideal para pequenas empresas com equipes externas reduzidas'
    },
    {
      name: 'Profissional',
      description: 'Para empresas que buscam eficiência e controle avançado',
      price: 'R$147',
      period: 'por usuário/mês',
      features: [
        'Até 20 usuários',
        'Otimização avançada de rotas',
        'App móvel com recursos completos',
        'Monitoramento em tempo real',
        'Relatórios detalhados',
        'Confirmação com foto/assinatura',
        'Integração com Waze/Google Maps',
        'Histórico de 90 dias',
        'Suporte por chat e email'
      ],
      isPopular: true,
      tooltip: 'Nossa opção mais popular, com equilíbrio entre recursos e preço'
    },
    {
      name: 'Enterprise',
      description: 'Solução personalizada para grandes operações',
      price: 'Personalizado',
      period: 'contato para cotação',
      features: [
        'Usuários ilimitados',
        'Otimização avançada de rotas',
        'API para integrações',
        'Customização de relatórios',
        'Monitoramento avançado',
        'White label disponível',
        'SLA garantido',
        'Histórico ilimitado',
        'Suporte 24/7 com gerente dedicado'
      ],
      tooltip: 'Para grandes empresas com necessidades específicas e alto volume'
    }
  ];

  return (
    <section id="planos" className="section-padding bg-white">
      <div className="container mx-auto container-padding">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="mb-4">Planos e <span className="text-kodiak-600">Preços</span></h2>
          <p className="text-lg text-gray-600">
            Escolha o plano ideal para o tamanho e necessidades da sua empresa. 
            Todos os planos incluem acesso ao app móvel e algoritmos de otimização.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div 
              key={index}
              className={`relative rounded-lg overflow-hidden shadow-sm border ${
                plan.isPopular ? 'border-kodiak-600 shadow-md' : 'border-gray-200'
              }`}
            >
              {plan.isPopular && (
                <div className="absolute top-0 right-0 bg-kodiak-600 text-white px-4 py-1 text-sm font-medium">
                  Mais Popular
                </div>
              )}
              
              <div className="p-6">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-gray-600 h-12">{plan.description}</p>
                
                <div className="my-6">
                  <span className="text-3xl font-bold">{plan.price}</span>
                  <span className="text-gray-500 ml-1">{plan.period}</span>
                </div>
                
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button 
                        className={`w-full ${
                          plan.isPopular ? 'bg-kodiak-600 hover:bg-kodiak-700' : ''
                        }`}
                        variant={plan.isPopular ? 'default' : 'outline'}
                      >
                        {plan.name === 'Enterprise' ? 'Fale Conosco' : 'Comece Agora'}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{plan.tooltip}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                
                <div className="mt-8">
                  <h4 className="font-medium text-gray-900 mb-4 flex items-center justify-between">
                    <span>Recursos Incluídos</span>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger>
                          <HelpCircle className="h-4 w-4 text-gray-400" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Todos os recursos disponíveis neste plano</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </h4>
                  
                  <ul className="space-y-3">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <div className="p-6 bg-gray-50 border-t border-gray-200">
                <div className="text-center">
                  <p className="text-sm text-gray-500">
                    {plan.name === 'Enterprise' 
                      ? 'Solução personalizada para sua empresa'
                      : 'Teste grátis por 14 dias, sem compromisso'}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-16 text-center">
          <h3 className="text-2xl font-bold mb-4">Perguntas Frequentes sobre Preços</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto mt-8 text-left">
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="font-bold text-lg mb-2">Existe período mínimo de contrato?</h4>
              <p className="text-gray-700">Não, nossos planos são mensais e você pode cancelar a qualquer momento. Também oferecemos desconto para pagamentos anuais.</p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="font-bold text-lg mb-2">Como funciona o período de teste?</h4>
              <p className="text-gray-700">Você tem acesso a todas as funcionalidades por 14 dias, sem necessidade de cartão de crédito. Ao final, escolha o plano que melhor atende às suas necessidades.</p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="font-bold text-lg mb-2">Posso mudar de plano depois?</h4>
              <p className="text-gray-700">Sim, você pode fazer upgrade ou downgrade a qualquer momento. As mudanças são aplicadas imediatamente e o valor é ajustado no próximo ciclo de faturamento.</p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="font-bold text-lg mb-2">O que acontece se eu exceder o limite de usuários?</h4>
              <p className="text-gray-700">Você receberá um alerta e a opção de fazer upgrade para um plano superior ou contratar usuários adicionais mantendo o mesmo plano.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PricingSection;
