import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

const JapaneseQuiz = () => {
  const [verbs, setVerbs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState({ isSubmitted: false, isCorrect: false });
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadVerbs = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/verbs/random');
        if (!response.ok) {
          throw new Error('Failed to fetch verbs');
        }
        const data = await response.json();
        setVerbs(data);
        setLoading(false);
      } catch (err) {
        console.error('Error loading verbs:', err);
        setError('Failed to load verb data');
        setLoading(false);
      }
    };

    loadVerbs();
  }, []);

  const handleInputChange = (value) => {
    // Only allow hiragana characters
    const hiraganaRegex = /^[\u3040-\u309f\u30fc]*$/;
    if (value === '' || hiraganaRegex.test(value)) {
      setUserAnswer(value);
    }
  };

  const checkAnswer = () => {
    const currentVerb = verbs[currentIndex];
    const isCorrect = userAnswer === currentVerb.teForm.kana;

    setFeedback({
      isSubmitted: true,
      isCorrect,
      correctAnswer: currentVerb.teForm.kana
    });

    setScore(prev => ({
      correct: prev.correct + (isCorrect ? 1 : 0),
      total: prev.total + 1
    }));

    // Move to next word after 2 seconds
    setTimeout(() => {
      if (currentIndex < verbs.length - 1) {
        setCurrentIndex(prev => prev + 1);
        setUserAnswer('');
        setFeedback({ isSubmitted: false, isCorrect: false });
      } else {
        // Quiz completed
        setFeedback(prev => ({
          ...prev,
          quizCompleted: true
        }));
      }
    }, 2000);
  };

  if (loading) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="p-6">
          <div className="text-center">Loading verb data...</div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="p-6">
          <div className="text-red-500 text-center">{error}</div>
        </CardContent>
      </Card>
    );
  }

  const currentVerb = verbs[currentIndex];

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader className="text-center">
        <h2 className="text-2xl font-bold">て Form Quiz</h2>
        <div className="text-lg mt-2">
          Progress: {currentIndex + 1}/20
        </div>
        <div className="text-sm text-muted-foreground">
          Score: {score.correct}/{score.total}
        </div>
      </CardHeader>

      <CardContent className="p-6">
        {feedback.quizCompleted ? (
          <div className="text-center">
            <h3 className="text-xl font-bold mb-4">Quiz Complete!</h3>
            <p className="text-lg">
              Final Score: {score.correct}/{score.total} 
              ({Math.round((score.correct / score.total) * 100)}%)
            </p>
            <Button 
              onClick={() => window.location.reload()}
              className="mt-4"
            >
              Try Again
            </Button>
          </div>
        ) : (
          <>
            <div className="text-center mb-6">
              <div className="text-2xl font-japanese mb-2">
                <ruby>
                  {currentVerb.dictionaryForm.kanji || currentVerb.dictionaryForm.kana}
                  <rt>{currentVerb.dictionaryForm.kana}</rt>
                </ruby>
              </div>
              <div className="text-sm text-muted-foreground">
                Verb type: {currentVerb.verbType}
              </div>
            </div>

            <div className="mb-4">
              <Input
                value={userAnswer}
                onChange={(e) => handleInputChange(e.target.value)}
                placeholder="Enter て form in hiragana"
                className={`text-lg font-japanese ${
                  feedback.isSubmitted
                    ? feedback.isCorrect
                      ? 'border-green-500 bg-green-500/10'
                      : 'border-red-500 bg-red-500/10'
                    : ''
                }`}
                disabled={feedback.isSubmitted}
              />

              {feedback.isSubmitted && !feedback.isCorrect && (
                <div className="text-sm text-red-400 mt-1">
                  Correct answer: {feedback.correctAnswer}
                </div>
              )}
            </div>

            <Button 
              onClick={checkAnswer}
              disabled={!userAnswer || feedback.isSubmitted}
              className="w-full"
            >
              Submit
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default JapaneseQuiz;