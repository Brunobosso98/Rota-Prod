
import React from 'react';
import { Button } from "@/components/ui/button";
import { CheckCircle } from "lucide-react";

const CallToAction = () => {
  return (
    <section className="bg-gray-50 py-20">
      <div className="container mx-auto container-padding">
        <div className="bg-white rounded-2xl overflow-hidden shadow-xl border border-gray-100">
          <div className="grid grid-cols-1 lg:grid-cols-2">
            <div className="p-8 lg:p-12">
              <h2 className="text-3xl lg:text-4xl font-bold mb-6">
                Pronto para <span className="text-kodiak-600">otimizar</span> suas rotas?
              </h2>
              
              <p className="text-lg text-gray-600 mb-8">
                Comece hoje mesmo a economizar tempo e dinheiro com o Rotas Kodiak.
                Teste gratuitamente por 14 dias, sem compromisso.
              </p>
              
              <div className="space-y-4 mb-8">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="text-green-500 mt-1 h-5 w-5 flex-shrink-0" />
                  <p className="text-gray-700">Configuração simples em minutos</p>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="text-green-500 mt-1 h-5 w-5 flex-shrink-0" />
                  <p className="text-gray-700">Suporte gratuito durante o período de teste</p>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="text-green-500 mt-1 h-5 w-5 flex-shrink-0" />
                  <p className="text-gray-700">Cancele a qualquer momento</p>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <Button size="lg" className="bg-kodiak-600 hover:bg-kodiak-700">
                  Comece Gratuitamente
                </Button>
                <Button 
                  size="lg" 
                  variant="outline"
                  className="border-kodiak-600 text-kodiak-600"
                >
                  Fale com um Especialista
                </Button>
              </div>
              
              <p className="text-sm text-gray-500 mt-4">
                Não é necessário cartão de crédito. Teste grátis por 14 dias.
              </p>
            </div>
            
            <div className="bg-gradient-to-br from-kodiak-600 to-kodiak-800 p-8 lg:p-12 flex items-center">
              <div className="text-white space-y-6 max-w-lg">
                <div className="inline-block bg-white/20 backdrop-blur-sm rounded-full px-4 py-1 text-sm font-medium">
                  Depoimento em Destaque
                </div>
                
                <blockquote className="text-xl lg:text-2xl font-medium leading-relaxed">
                  "Implementar o Rotas Kodiak foi uma das melhores decisões que tomamos. 
                  Reduzimos custos operacionais, melhoramos a satisfação dos clientes e 
                  aumentamos a produtividade das nossas equipes de campo."
                </blockquote>
                
                <div className="flex items-center">
                  <div className="mr-4 w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-white font-bold">
                    M
                  </div>
                  <div>
                    <div className="font-bold">Marcelo Almeida</div>
                    <div className="text-white/80">Diretor de Operações, TechDelivery</div>
                  </div>
                </div>
                
                <div className="pt-4">
                  <div className="flex items-center justify-between bg-white/10 backdrop-blur-sm rounded-lg p-4">
                    <div>
                      <div className="text-white/80 text-sm">Economia Mensal</div>
                      <div className="text-2xl font-bold">R$ 15.000,00</div>
                    </div>
                    <div className="h-10 w-px bg-white/20"></div>
                    <div>
                      <div className="text-white/80 text-sm">Aumento de Produtividade</div>
                      <div className="text-2xl font-bold">+32%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CallToAction;
