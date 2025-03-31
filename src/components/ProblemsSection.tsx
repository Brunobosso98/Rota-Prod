
import React from 'react';
import { AlertTriangle, Clock, DollarSign, Map, Users } from 'lucide-react';

const ProblemsSection = () => {
  const problems = [
    {
      icon: <Map className="h-10 w-10 text-red-500" />,
      title: 'Rotas Ineficientes',
      description: 'Perda de tempo e recursos com rotas mal planejadas e deslocamentos desnecessários.'
    },
    {
      icon: <Users className="h-10 w-10 text-red-500" />,
      title: 'Falta de Controle',
      description: 'Dificuldade de monitorar equipes externas e confirmação de visitas realizadas.'
    },
    {
      icon: <DollarSign className="h-10 w-10 text-red-500" />,
      title: 'Custos Elevados',
      description: 'Gastos excessivos com combustível, manutenção e horas extras devido à ineficiência logística.'
    },
    {
      icon: <Clock className="h-10 w-10 text-red-500" />,
      title: 'Atrasos nas Entregas',
      description: 'Prazos perdidos e clientes insatisfeitos por falta de previsibilidade nas rotas.'
    }
  ];

  return (
    <section id="como-funciona" className="py-20 bg-gray-50">
      <div className="container mx-auto container-padding">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="mb-4">Problemas que o <span className="text-kodiak-600">Rotas Kodiak</span> Resolve</h2>
          <p className="text-lg text-gray-600">
            Nossas soluções de otimização de rotas foram desenhadas para eliminar os principais desafios 
            enfrentados por empresas com equipes externas.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {problems.map((problem, index) => (
            <div 
              key={index} 
              className="bg-white rounded-lg p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className="bg-red-50 p-3 rounded-full w-fit mb-5">
                {problem.icon}
              </div>
              <h3 className="text-xl font-semibold mb-3">{problem.title}</h3>
              <p className="text-gray-600">{problem.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-16 bg-gradient-to-r from-kodiak-600 to-kodiak-800 rounded-lg p-8 text-white">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center space-x-4">
              <AlertTriangle className="h-12 w-12 text-yellow-300" />
              <div>
                <h3 className="text-2xl font-bold mb-1">Você sabia?</h3>
                <p className="text-white/90">
                  Empresas sem otimização de rotas desperdiçam, em média, 30% do tempo em deslocamentos ineficientes.
                </p>
              </div>
            </div>
            <button className="bg-white text-kodiak-700 hover:bg-gray-100 transition-colors py-3 px-6 rounded-md font-medium whitespace-nowrap">
              Calcule sua Economia
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProblemsSection;
