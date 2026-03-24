import type { Metadata } from 'next'
import { Toaster } from 'react-hot-toast'
import './globals.css'

export const metadata: Metadata = {
  title: 'StitchFlow - Transform Images to Embroidery',
  description: 'Upload any image and get production-ready embroidery files. DST for simple images, SVG + Wilcom-compatible for complex designs.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-body bg-background text-slate-50">
        {children}
        <Toaster 
          position="top-right"
          toastOptions={{
            style: {
              background: '#1E293B',
              color: '#F8FAFC',
              border: '1px solid #334155',
            },
          }}
        />
      </body>
    </html>
  )
}
