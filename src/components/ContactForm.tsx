
import React from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Mail, Phone, MessageSquare } from 'lucide-react';

const ContactForm = () => {
  return (
    <section className="bg-white py-20">
      <div className="container mx-auto container-padding">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-12">
          <div className="lg:col-span-2">
            <h2 className="text-3xl font-bold mb-6">Fale com a <span className="text-kodiak-600">Kodiak</span></h2>
            
            <p className="text-gray-600 mb-8">
              Estamos à disposição para responder suas dúvidas, apresentar nossa 
              plataforma ou entender melhor as necessidades da sua empresa.
            </p>
            
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="bg-kodiak-50 p-3 rounded-full text-kodiak-600">
                  <Mail className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Email</h3>
                  <p className="text-gray-600 mb-1">Para suporte e dúvidas gerais:</p>
                  <a href="mailto:contato@rotaskodiak.com" className="text-kodiak-600 hover:underline">contato@rotaskodiak.com</a>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="bg-kodiak-50 p-3 rounded-full text-kodiak-600">
                  <Phone className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Telefone</h3>
                  <p className="text-gray-600 mb-1">Atendimento em horário comercial:</p>
                  <a href="tel:+551140028922" className="text-kodiak-600 hover:underline">(11) 4002-8922</a>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="bg-kodiak-50 p-3 rounded-full text-kodiak-600">
                  <MessageSquare className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Chat Online</h3>
                  <p className="text-gray-600 mb-1">Suporte imediato:</p>
                  <button className="text-kodiak-600 hover:underline">Iniciar conversa</button>
                </div>
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-3">
            <div className="bg-gray-50 rounded-xl p-8">
              <h3 className="text-2xl font-bold mb-6">Envie uma mensagem</h3>
              
              <form className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="name">Nome</Label>
                    <Input id="name" placeholder="Seu nome completo" />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input id="email" type="email" placeholder="seu@email.com" />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="company">Empresa</Label>
                    <Input id="company" placeholder="Nome da sua empresa" />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="phone">Telefone</Label>
                    <Input id="phone" placeholder="(00) 00000-0000" />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="subject">Assunto</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um assunto" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="info">Informações sobre a plataforma</SelectItem>
                      <SelectItem value="demo">Solicitar demonstração</SelectItem>
                      <SelectItem value="pricing">Dúvidas sobre preços</SelectItem>
                      <SelectItem value="support">Suporte técnico</SelectItem>
                      <SelectItem value="partnership">Parceria</SelectItem>
                      <SelectItem value="other">Outro assunto</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="message">Mensagem</Label>
                  <Textarea 
                    id="message" 
                    placeholder="Descreva como podemos ajudar..." 
                    rows={5}
                  />
                </div>
                
                <Button type="submit" className="w-full bg-kodiak-600 hover:bg-kodiak-700">
                  Enviar Mensagem
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ContactForm;
