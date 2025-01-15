import '../styles/globals.css'
import { ThemeProvider } from '@/components/theme-provider'

export default function App({ Component, pageProps }) {
  return (
    <ThemeProvider>
      <div className="min-h-screen bg-background">
        <Component {...pageProps} />
      </div>
    </ThemeProvider>
  )
}