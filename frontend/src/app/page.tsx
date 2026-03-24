'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { Upload, Download, Zap, Shield, FileImage, Layers, ArrowRight, Check, MessageCircle, X, Send } from 'lucide-react'
import Link from 'next/link'

// Robot Assistant Component
function RobotAssistant() {
  const [isOpen, setIsOpen] = useState(true)
  const [eyePosition, setEyePosition] = useState({ x: 0, y: 0 })
  const robotRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!robotRef.current) return
      
      const rect = robotRef.current.getBoundingClientRect()
      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2
      
      const deltaX = (e.clientX - centerX) / 30
      const deltaY = (e.clientY - centerY) / 30
      
      setEyePosition({
        x: Math.max(-5, Math.min(5, deltaX)),
        y: Math.max(-5, Math.min(5, deltaY))
      })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <div className="robot-container">
      <motion.div
        ref={robotRef}
        className="robot"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="robot-eyes">
          <div 
            className="robot-eye"
            style={{ transform: `translate(${eyePosition.x}px, ${eyePosition.y}px)` }}
          />
          <div 
            className="robot-eye"
            style={{ transform: `translate(${eyePosition.x}px, ${eyePosition.y}px)` }}
          />
        </div>
      </motion.div>
      
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="absolute bottom-16 left-0 w-64 glass rounded-xl p-4"
          >
            <p className="text-sm text-slate-300">
              Hi! I'm your embroidery assistant. Upload an image and I'll convert it to embroidery format!
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Chatbot Component
function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<{role: string, content: string}[]>([
    { role: 'bot', content: 'Hello! How can I help you today?' }
  ])
  const [input, setInput] = useState('')

  const faq = {
    'pricing': 'We offer competitive pricing: Simple images (KSh 100), Complex images (KSh 250). You can also top up your wallet for convenience.',
    'how': 'Simply upload your image, choose complexity level, and we\'ll generate DST or SVG files. Payment is via M-Pesa STK Push or wallet balance.',
    'formats': 'We support PNG, JPG, JPEG, WebP, and BMP. Output formats include DST (for simple images) and SVG + JSON (for complex/wilcom designs).',
    'troubleshooting': 'For issues, check: 1) File size under 10MB 2) Supported format 3) Stable internet. Contact us on WhatsApp for further help.'
  }

  const handleSend = () => {
    if (!input.trim()) return
    
    const userMessage = input.toLowerCase()
    setMessages(prev => [...prev, { role: 'user', content: input }])
    setInput('')

    let response = 'I\'m not sure about that. Contact us on WhatsApp for more help!'
    
    if (userMessage.includes('price')) response = faq.pricing
    else if (userMessage.includes('how') || userMessage.includes('work')) response = faq.how
    else if (userMessage.includes('format') || userMessage.includes('support')) response = faq.formats
    else if (userMessage.includes('trouble') || userMessage.includes('issue') || userMessage.includes('problem')) response = faq.troubleshooting

    setTimeout(() => {
      setMessages(prev => [...prev, { role: 'bot', content: response }])
    }, 500)
  }

  return (
    <div className="chatbot-container">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="chatbot-modal"
          >
            <div className="p-4 border-b border-surface-light flex justify-between items-center">
              <h3 className="font-heading font-semibold">Chat Support</h3>
              <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>
            
            <div className="h-72 overflow-y-auto p-4 space-y-3">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-lg max-w-[80%] ${
                    msg.role === 'user' 
                      ? 'ml-auto bg-primary/20' 
                      : 'mr-auto bg-surface-light'
                  }`}
                >
                  <p className="text-sm">{msg.content}</p>
                </div>
              ))}
            </div>

            <div className="p-4 border-t border-surface-light">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Type a message..."
                  className="input flex-1 text-sm"
                />
                <button 
                  onClick={handleSend}
                  className="p-3 bg-primary rounded-lg hover:bg-primary-dark transition-colors"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        className="chatbot-toggle"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </motion.div>
    </div>
  )
}

// Feature Card Component
function FeatureCard({ icon: Icon, title, description, delay }: { icon: any, title: string, description: string, delay: number }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay }}
      className="card group"
    >
      <div className="w-14 h-14 rounded-xl bg-primary/20 flex items-center justify-center mb-4 group-hover:bg-primary/30 transition-colors">
        <Icon className="w-7 h-7 text-primary" />
      </div>
      <h3 className="text-xl font-heading font-semibold mb-2">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </motion.div>
  )
}

// Pricing Card Component
function PricingCard({ title, price, features, popular = false }: { title: string, price: string, features: string[], popular?: boolean }) {
  return (
    <div className={`card relative ${popular ? 'border-primary glow' : ''}`}>
      {popular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-primary rounded-full text-sm font-semibold">
          Most Popular
        </div>
      )}
      <h3 className="text-xl font-heading font-semibold mb-2">{title}</h3>
      <div className="text-4xl font-heading font-bold mb-4">
        {price} <span className="text-lg font-normal text-slate-400">KES</span>
      </div>
      <ul className="space-y-3">
        {features.map((feature, i) => (
          <li key={i} className="flex items-center gap-2 text-slate-300">
            <Check size={18} className="text-accent" />
            {feature}
          </li>
        ))}
      </ul>
      <button className={`w-full mt-6 ${popular ? 'btn-primary' : 'btn-secondary'}`}>
        Get Started
      </button>
    </div>
  )
}

export default function HomePage() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <main className="min-h-screen">
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'glass py-3' : 'py-6'}`}>
        <div className="container mx-auto px-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <FileImage className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-heading font-bold">StitchFlow</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-slate-300 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-slate-300 hover:text-white transition-colors">How It Works</a>
            <a href="#pricing" className="text-slate-300 hover:text-white transition-colors">Pricing</a>
          </div>

          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-slate-300 hover:text-white transition-colors">
              Dashboard
            </Link>
            <Link href="/login" className="btn-secondary text-sm py-2">
              Login
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden mesh-gradient">
        {/* Floating threads */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-32 bg-gradient-to-b from-primary/30 to-transparent"
              style={{
                left: `${10 + i * 15}%`,
                top: `${20 + (i % 3) * 25}%`,
              }}
              animate={{
                y: [0, -30, 0],
                rotate: [0, 5, 0],
              }}
              transition={{
                duration: 8,
                repeat: Infinity,
                delay: i * 0.5,
              }}
            />
          ))}
        </div>

        <div className="container mx-auto px-4 relative z-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-7xl font-heading font-bold mb-6 leading-tight">
              Transform Any Image
              <span className="block bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
                Into Embroidery
              </span>
            </h1>
            <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
              Upload your design and receive production-ready embroidery files. 
              DST for simple images, SVG + Wilcom-compatible format for complex designs.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/dashboard" className="btn-primary text-lg px-8 py-4 inline-flex items-center justify-center gap-2">
                Start Converting <ArrowRight size={20} />
              </Link>
              <a href="#how-it-works" className="btn-secondary text-lg px-8 py-4">
                Learn More
              </a>
            </div>

            {/* Stats */}
            <motion.div 
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="mt-16 flex justify-center gap-12"
            >
              <div>
                <div className="text-4xl font-heading font-bold text-primary">10K+</div>
                <div className="text-slate-400">Designs Converted</div>
              </div>
              <div>
                <div className="text-4xl font-heading font-bold text-secondary">99%</div>
                <div className="text-slate-400">Accuracy Rate</div>
              </div>
              <div>
                <div className="text-4xl font-heading font-bold text-accent"><5min</div>
                <div className="text-slate-400">Processing Time</div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-surface">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-heading font-bold mb-4">Powerful Features</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Everything you need to convert images to production-ready embroidery files
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard
              icon={Download}
              title="DST Output"
              description="Clean, optimized DST files ready for embroidery machines"
              delay={0}
            />
            <FeatureCard
              icon={Layers}
              title="SVG + Wilcom"
              description="Layered SVG with JSON structure importable to Wilcom"
              delay={0.1}
            />
            <FeatureCard
              icon={Zap}
              title="Fast Processing"
              description="Get your files in minutes, not hours"
              delay={0.2}
            />
            <FeatureCard
              icon={Shield}
              title="Secure Storage"
              description="Your files are safe with enterprise-grade security"
              delay={0.3}
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-24">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-heading font-bold mb-4">How It Works</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Three simple steps to get your embroidery files
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: 1, title: 'Upload Image', desc: 'Drag and drop your image or click to browse' },
              { step: 2, title: 'Processing', desc: 'We analyze and convert your image to embroidery format' },
              { step: 3, title: 'Download', desc: 'Get your DST or SVG files ready for production' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.2 }}
                className="text-center"
              >
                <div className="w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl font-heading font-bold text-primary">{item.step}</span>
                </div>
                <h3 className="text-xl font-heading font-semibold mb-2">{item.title}</h3>
                <p className="text-slate-400">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 bg-surface">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-heading font-bold mb-4">Simple Pricing</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Pay per conversion or top up your wallet for convenience
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <PricingCard
              title="Simple"
              price="100"
              features={[
                'DST Output',
                'Up to 5MB file',
                'Basic support',
                '24hr download'
              ]}
            />
            <PricingCard
              title="Complex"
              price="250"
              popular
              features={[
                'SVG + Wilcom JSON',
                'Up to 10MB file',
                'Priority support',
                'Layered colors',
                'Editable paths'
              ]}
            />
            <PricingCard
              title="Wallet"
              price="Top Up"
              features={[
                'Any plan type',
                'Faster checkout',
                'Save payment details',
                'Balance history'
              ]}
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-surface-light">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <FileImage className="w-4 h-4 text-white" />
              </div>
              <span className="font-heading font-bold">StitchFlow</span>
            </div>

            <div className="flex items-center gap-6">
              <a href="#" className="text-slate-400 hover:text-white transition-colors">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
              </a>
              <a href="#" className="text-slate-400 hover:text-white transition-colors">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>
              </a>
              <a href="#" className="text-slate-400 hover:text-white transition-colors">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg>
              </a>
              <a 
                href="https://wa.me/254700000000" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-accent/20 text-accent rounded-lg hover:bg-accent/30 transition-colors"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297a11.815 11.815 0 00-.713-5.489 11.886 11.886 0 00-6.671-3.875c-3.179 0-5.982 1.68-7.522 4.37a11.866 11.866 0 00-1.154 5.836c.002 5.522 4.371 9.986 9.893 9.982 2.502 0 4.828-1.025 6.571-2.735a11.883 11.883 0 003.837-5.195z"/></svg>
                Contact WhatsApp
              </a>
            </div>

            <div className="text-slate-500 text-sm">
              © 2024 StitchFlow. All rights reserved.
            </div>
          </div>
        </div>
      </footer>

      {/* Robot & Chatbot */}
      <RobotAssistant />
      <Chatbot />
    </main>
  )
}
