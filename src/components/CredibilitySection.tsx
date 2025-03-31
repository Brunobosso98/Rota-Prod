
import React from 'react';
import { ShieldCheck, Code, Badge, HeadphonesIcon } from 'lucide-react';

const CredibilitySection = () => {
  const techPartners = [
    {
      name: "Google Cloud",
      logoClass: "bg-[#4285F4]"
    },
    {
      name: "OR-Tools",
      logoClass: "bg-[#EA4335]"
    },
    {
      name: "OSRM",
      logoClass: "bg-[#34A853]"
    },
    {
      name: "AWS",
      logoClass: "bg-[#FF9900]"
    }
  ];

  const credibilityItems = [
    {
      icon: <ShieldCheck className="h-10 w-10 text-kodiak-600" />,
      title: 'Segurança Garantida',
      description: 'Seus dados são protegidos com criptografia de ponta a ponta e nossa infraestrutura segue os mais rigorosos padrões de segurança.'
    },
    {
      icon: <Code className="h-10 w-10 text-kodiak-600" />,
      title: 'Tecnologia de Ponta',
      description: 'Utilizamos algoritmos avançados como OR-Tools do Google e OSRM para garantir as melhores rotas possíveis em qualquer cenário.'
    },
    {
      icon: <Badge className="h-10 w-10 text-kodiak-600" />,
      title: 'Disponibilidade 99.9%',
      description: 'Nossa plataforma possui alta disponibilidade com redundância geográfica e backup automático de dados.'
    },
    {
      icon: <HeadphonesIcon className="h-10 w-10 text-kodiak-600" />,
      title: 'Suporte Especializado',
      description: 'Nossa equipe de suporte técnico está pronta para ajudar em qualquer questão, com atendimento rápido e personalizado.'
    }
  ];

  return (
    <section className="section-padding bg-gray-50">
      <div className="container mx-auto container-padding">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="mb-4">Por Que <span className="text-kodiak-600">Confiar</span> no Rotas Kodiak?</h2>
          <p className="text-lg text-gray-600">
            Utilizamos tecnologias reconhecidas mundialmente e mantemos os mais altos padrões de segurança 
            e disponibilidade para sua tranquilidade.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {credibilityItems.map((item, index) => (
            <div 
              key={index}
              className="bg-white rounded-lg p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className="bg-kodiak-50 p-3 rounded-full w-fit mb-5">
                {item.icon}
              </div>
              <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
              <p className="text-gray-600">{item.description}</p>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-lg p-8 shadow-sm border border-gray-100">
          <div className="text-center mb-10">
            <h3 className="text-2xl font-bold mb-3">Integrado com Tecnologias Reconhecidas</h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              O Rotas Kodiak utiliza e se integra com as melhores tecnologias do mercado para 
              garantir performance, confiabilidade e resultados superiores.
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {techPartners.map((partner, index) => (
              <div key={index} className="flex flex-col items-center">
                <div className={`w-16 h-16 ${partner.logoClass} rounded-lg flex items-center justify-center text-white font-bold mb-3`}>
                  {partner.name.substring(0, 1)}
                </div>
                <span className="font-medium">{partner.name}</span>
              </div>
            ))}
          </div>
          
          <div className="mt-10 pt-8 border-t border-gray-100">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="text-center md:text-left">
                <h4 className="text-xl font-bold mb-2">API Aberta para Integrações</h4>
                <p className="text-gray-600">
                  Nossa API documentada permite integrar o Rotas Kodiak com seus sistemas existentes.
                </p>
              </div>
              
              <button className="px-6 py-2 border border-kodiak-600 text-kodiak-600 rounded-md hover:bg-kodiak-50 transition-colors font-medium">
                Documentação da API
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CredibilitySection;
