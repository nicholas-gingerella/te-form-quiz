import JapaneseQuiz from '@/components/JapaneseQuiz'
import { ThemeToggle } from '@/components/theme-toggle'

export default function Home() {
  return (
    <main className="container mx-auto p-4 min-h-screen relative">
      <ThemeToggle />
      <JapaneseQuiz />
    </main>
  )
}