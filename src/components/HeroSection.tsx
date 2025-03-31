
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CheckCircle, Timer, TrendingUp } from "lucide-react";

const HeroSection = () => {
  const [showDialog, setShowDialog] = useState(false);
  
  return (
    <section className="pt-28 pb-16 md:pt-32 md:pb-24 bg-gradient-to-b from-blue-50 to-white overflow-hidden">
      <div className="container mx-auto container-padding">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6 max-w-xl">
            <h1 className="font-bold tracking-tight">
              <span className="gradient-text">Otimize suas rotas.</span>{" "}
              <span className="block">Economize tempo e dinheiro.</span>
            </h1>
            
            <p className="text-xl text-gray-600">
              Transforme a maneira como sua empresa gerencia entregas e visitas externas. 
              Economize até 30% em tempo e combustível com algoritmos de otimização de rotas.
            </p>
            
            <div className="space-y-4 pt-2">
              <div className="flex items-start space-x-3">
                <CheckCircle className="text-kodiak-600 mt-1 h-5 w-5 flex-shrink-0" />
                <p className="text-gray-700">Algoritmos avançados que calculam as melhores rotas</p>
              </div>
              <div className="flex items-start space-x-3">
                <Timer className="text-kodiak-600 mt-1 h-5 w-5 flex-shrink-0" />
                <p className="text-gray-700">Reduza o tempo de deslocamento em até 30%</p>
              </div>
              <div className="flex items-start space-x-3">
                <TrendingUp className="text-kodiak-600 mt-1 h-5 w-5 flex-shrink-0" />
                <p className="text-gray-700">Aumente a produtividade das suas equipes externas</p>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 pt-2">
              <Button size="lg" className="bg-kodiak-600 hover:bg-kodiak-700 text-white">
                Comece Gratuitamente
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="border-kodiak-600 text-kodiak-600"
                onClick={() => setShowDialog(true)}
              >
                Agende uma Demonstração
              </Button>
            </div>
            
            <p className="text-sm text-gray-500">
              Não é necessário cartão de crédito. Teste grátis por 14 dias.
            </p>
          </div>
          
          <div className="relative flex justify-center lg:justify-end">
            <div className="relative w-full max-w-lg">
              <div className="absolute -top-4 -right-4 w-72 h-72 bg-kodiak-200 rounded-full mix-blend-multiply filter blur-2xl opacity-70 animate-blob"></div>
              <div className="absolute -bottom-8 left-20 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-2xl opacity-70 animate-blob animation-delay-4000"></div>
              
              <div className="relative bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100 animate-float">
                <div className="bg-gray-50 p-4 border-b border-gray-100">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                    <div className="ml-2 text-sm text-gray-500">Dashboard de Rotas</div>
                  </div>
                </div>
                
                <div className="p-4">
                  <div className="rounded-lg bg-kodiak-50 p-4 mb-4 border border-kodiak-100">
                    <div className="flex justify-between items-center mb-3">
                      <div className="font-medium text-kodiak-800">Otimização de Rota</div>
                      <div className="text-xs px-2 py-1 bg-kodiak-600 text-white rounded-full">Otimizado</div>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full">
                      <div className="h-2 bg-kodiak-600 rounded-full w-3/4"></div>
                    </div>
                    <div className="flex justify-between mt-1 text-xs text-gray-500">
                      <span>15km economizados</span>
                      <span>30% mais eficiente</span>
                    </div>
                  </div>
                  
                  <div className="bg-gray-100 rounded-lg h-40 mb-4 relative overflow-hidden">
                    {/* Simplified map visualization */}
                    <div className="w-full h-full bg-blue-50">
                      <div className="absolute top-1/3 left-1/4 w-2 h-2 bg-red-500 rounded-full"></div>
                      <div className="absolute top-1/2 left-1/2 w-2 h-2 bg-red-500 rounded-full"></div>
                      <div className="absolute bottom-1/4 right-1/3 w-2 h-2 bg-red-500 rounded-full"></div>
                      <div className="absolute border-2 border-dashed border-kodiak-600 h-24 w-32 rounded-full top-1/4 left-1/4"></div>
                      
                      {/* Route line */}
                      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M25 35 L50 50 L70 75" stroke="#0d6efd" strokeWidth="2" strokeDasharray="2 2" />
                      </svg>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between items-center p-2 rounded bg-gray-50">
                      <div className="flex items-center">
                        <div className="w-6 h-6 rounded-full bg-kodiak-100 flex items-center justify-center mr-2">1</div>
                        <span className="text-sm">Cliente A</span>
                      </div>
                      <span className="text-xs text-gray-500">09:15</span>
                    </div>
                    <div className="flex justify-between items-center p-2 rounded bg-gray-50">
                      <div className="flex items-center">
                        <div className="w-6 h-6 rounded-full bg-kodiak-100 flex items-center justify-center mr-2">2</div>
                        <span className="text-sm">Cliente B</span>
                      </div>
                      <span className="text-xs text-gray-500">10:30</span>
                    </div>
                    <div className="flex justify-between items-center p-2 rounded bg-gray-50">
                      <div className="flex items-center">
                        <div className="w-6 h-6 rounded-full bg-kodiak-100 flex items-center justify-center mr-2">3</div>
                        <span className="text-sm">Cliente C</span>
                      </div>
                      <span className="text-xs text-gray-500">11:45</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Demo Request Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Agende uma Demonstração</DialogTitle>
            <DialogDescription>
              Preencha o formulário abaixo e entraremos em contato para agendar uma demonstração personalizada.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-1 gap-2">
              <Label htmlFor="name">Nome</Label>
              <Input id="name" />
            </div>
            <div className="grid grid-cols-1 gap-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" />
            </div>
            <div className="grid grid-cols-1 gap-2">
              <Label htmlFor="company">Empresa</Label>
              <Input id="company" />
            </div>
            <div className="grid grid-cols-1 gap-2">
              <Label htmlFor="phone">Telefone</Label>
              <Input id="phone" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>Cancelar</Button>
            <Button type="submit" onClick={() => setShowDialog(false)}>Solicitar Demo</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
};

export default HeroSection;
