
import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { MenuIcon, X } from "lucide-react";

const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled ? 'bg-white shadow-md py-2' : 'bg-transparent py-4'}`}>
      <div className="container mx-auto flex justify-between items-center container-padding">
        {/* Logo */}
        <div className="flex items-center">
          <div className="mr-2">
            <svg className="w-8 h-8 text-kodiak-600" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <span className="font-bold text-xl text-kodiak-800">Rotas Kodiak</span>
        </div>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-8">
          <a href="#como-funciona" className="text-gray-700 hover:text-kodiak-600 transition-colors">Como Funciona</a>
          <a href="#recursos" className="text-gray-700 hover:text-kodiak-600 transition-colors">Recursos</a>
          <a href="#casos-de-uso" className="text-gray-700 hover:text-kodiak-600 transition-colors">Casos de Uso</a>
          <a href="#planos" className="text-gray-700 hover:text-kodiak-600 transition-colors">Planos</a>
        </nav>
        
        {/* CTA Buttons */}
        <div className="hidden md:flex items-center space-x-4">
          <Button variant="outline" className="border-kodiak-600 text-kodiak-600 hover:bg-kodiak-50">Login</Button>
          <Button className="bg-kodiak-600 hover:bg-kodiak-700">Teste Grátis</Button>
        </div>
        
        {/* Mobile Menu Button */}
        <button
          className="md:hidden text-gray-700"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={24} /> : <MenuIcon size={24} />}
        </button>
      </div>
      
      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-t">
          <div className="container mx-auto py-4 px-4 space-y-4">
            <a href="#como-funciona" className="block py-2 text-gray-700 hover:text-kodiak-600" onClick={() => setMobileMenuOpen(false)}>Como Funciona</a>
            <a href="#recursos" className="block py-2 text-gray-700 hover:text-kodiak-600" onClick={() => setMobileMenuOpen(false)}>Recursos</a>
            <a href="#casos-de-uso" className="block py-2 text-gray-700 hover:text-kodiak-600" onClick={() => setMobileMenuOpen(false)}>Casos de Uso</a>
            <a href="#planos" className="block py-2 text-gray-700 hover:text-kodiak-600" onClick={() => setMobileMenuOpen(false)}>Planos</a>
            <div className="pt-2 space-y-3">
              <Button variant="outline" className="w-full border-kodiak-600 text-kodiak-600">Login</Button>
              <Button className="w-full bg-kodiak-600 hover:bg-kodiak-700">Teste Grátis</Button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;
