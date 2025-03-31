
import React from 'react';
import { Star, Quote } from 'lucide-react';

const TestimonialSection = () => {
  const testimonials = [
    {
      quote: "O Rotas Kodiak transformou nossa operação de entregas. Reduzimos o tempo em trânsito em 27% e aumentamos o número de entregas diárias em mais de 30%.",
      author: "Carlos Mendes",
      position: "Diretor de Logística",
      company: "Distribuidora Central",
      rating: 5,
      avatarColor: "bg-blue-500"
    },
    {
      quote: "Nossa equipe de vendas aumentou a produtividade em 35% após implementar o Rotas Kodiak. O controle das visitas e a otimização das rotas fizeram toda a diferença.",
      author: "Ana Luiza",
      position: "Gerente Comercial",
      company: "Grupo Farma Brasil",
      rating: 5,
      avatarColor: "bg-green-500"
    },
    {
      quote: "A facilidade de uso e os relatórios detalhados nos deram visibilidade completa da operação externa. Hoje sabemos exatamente onde estão nossos técnicos e otimizamos o tempo de resposta.",
      author: "Roberto Santos",
      position: "Coordenador de Assistência Técnica",
      company: "TecnoServ",
      rating: 4,
      avatarColor: "bg-purple-500"
    }
  ];

  const stats = [
    { value: '30%', label: 'Economia média em combustível' },
    { value: '25%', label: 'Mais visitas por dia' },
    { value: '40%', label: 'Redução no tempo de planejamento' },
    { value: '99.9%', label: 'Uptime da plataforma' }
  ];

  return (
    <section className="section-padding bg-white">
      <div className="container mx-auto container-padding">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="mb-4">O Que Nossos <span className="text-kodiak-600">Clientes</span> Dizem</h2>
          <p className="text-lg text-gray-600">
            Centenas de empresas já transformaram suas operações externas com o Rotas Kodiak. 
            Veja o que elas têm a dizer.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
          {testimonials.map((testimonial, index) => (
            <div 
              key={index}
              className="bg-gray-50 rounded-lg p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-6">
                <div className={`${testimonial.avatarColor} w-12 h-12 rounded-full flex items-center justify-center text-white font-bold`}>
                  {testimonial.author.substring(0, 1)}
                </div>
                <Quote className="h-8 w-8 text-kodiak-200" />
              </div>
              
              <p className="text-gray-700 mb-6 italic">"{testimonial.quote}"</p>
              
              <div className="flex mb-3">
                {[...Array(5)].map((_, i) => (
                  <Star 
                    key={i} 
                    className={`h-5 w-5 ${i < testimonial.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`} 
                  />
                ))}
              </div>
              
              <div>
                <div className="font-bold">{testimonial.author}</div>
                <div className="text-gray-600">{testimonial.position}</div>
                <div className="text-kodiak-600 text-sm">{testimonial.company}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="bg-gradient-to-r from-kodiak-600 to-kodiak-800 rounded-lg overflow-hidden">
          <div className="grid grid-cols-1 md:grid-cols-2">
            <div className="p-8 md:p-10">
              <h3 className="text-2xl font-bold text-white mb-4">Resultados Comprovados</h3>
              <p className="text-white/90 mb-6">
                Nossos clientes experimentam melhorias significativas após implementar o Rotas Kodiak. 
                Veja alguns dos resultados médios obtidos:
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {stats.map((stat, index) => (
                  <div key={index} className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                    <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
                    <div className="text-white/80">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-white p-8 md:p-10">
              <h3 className="text-2xl font-bold text-kodiak-800 mb-4">Empresas que Confiam</h3>
              <p className="text-gray-600 mb-6">
                Empresas de diversos setores utilizam o Rotas Kodiak para otimizar suas operações externas.
              </p>
              
              <div className="grid grid-cols-3 gap-4">
                {[...Array(6)].map((_, index) => (
                  <div key={index} className="h-16 bg-gray-100 rounded flex items-center justify-center">
                    <div className="text-gray-400 font-bold">Logo</div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 text-center">
                <a href="#" className="text-kodiak-600 font-medium hover:underline">Ver todos os casos de sucesso →</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TestimonialSection;
