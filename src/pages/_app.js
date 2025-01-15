import '../styles/globals.css'

export default function App({ Component, pageProps }) {
  return (
    <div className="min-h-screen dark bg-background">
      <Component {...pageProps} />
    </div>
  );
}