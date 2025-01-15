import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Papa from 'papaparse';

// Helper function to create verb objects
function createVerb({
    type, group, english, kanji, hiragana, root, romaji,
    te, ta, tai, conditional,
    nonPastPositive, nonPastNegative, politePositive, politeNegative,
    pastPositive, pastNegative, politePastPositive, politePastNegative,
    potentialPlainPositive, potentialPlainNegative,
    potentialPolitePositive, potentialPoliteNegative,
    potentialPastPositive, potentialPastNegative,
    volitionalPlainPositive, volitionalPlainNegative,
    volitionalPolitePositive, volitionalPoliteNegative
}) {
    return {
        type, group, english, kanji, hiragana, root, romaji,
        te, ta, tai, conditional,
        non_past: {
            plain: {
                positive: nonPastPositive,
                negative: nonPastNegative
            },
            polite: {
                positive: politePositive,
                negative: politeNegative
            }
        },
        past: {
            plain: {
                positive: pastPositive,
                negative: pastNegative
            },
            polite: {
                positive: politePastPositive,
                negative: politePastNegative
            }
        },
        potential: {
            plain: {
                positive: potentialPlainPositive,
                negative: potentialPlainNegative
            },
            polite: {
                positive: potentialPolitePositive,
                negative: potentialPoliteNegative
            },
            past: {
                positive: potentialPastPositive,
                negative: potentialPastNegative
            }
        },
        volitional: {
            plain: {
                positive: volitionalPlainPositive,
                negative: volitionalPlainNegative
            },
            polite: {
                positive: volitionalPolitePositive,
                negative: volitionalPoliteNegative
            }
        }
    };
}

const JapaneseQuiz = () => {
  const [words, setWords] = useState({});
  const [currentWord, setCurrentWord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userAnswers, setUserAnswers] = useState({
    nonPastPlainPositive: '',
    nonPastPlainNegative: '',
    nonPastPolitePositive: '',
    nonPastPoliteNegative: '',
    pastPlainPositive: '',
    pastPlainNegative: '',
    pastPolitePositive: '',
    pastPoliteNegative: ''
  });
  const [feedback, setFeedback] = useState({
    isSubmitted: false,
    isCorrect: false,
    correctAnswers: null
  });
  const [score, setScore] = useState({
    correct: 0,
    total: 0,
    startTime: null,
    answeredTime: null
  });

  useEffect(() => {
    const loadWords = async () => {
      try {
        const response = await fetch('/words.csv');
        if (!response.ok) {
          throw new Error('Failed to fetch words.csv');
        }
        const csvText = await response.text();
        
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            const parsedWords = {};
            
            results.data.forEach(row => {
              parsedWords[row.romaji] = createVerb({
                type: row.type,
                group: row.group,
                english: row.english,
                kanji: row.kanji,
                hiragana: row.hiragana,
                root: row.root,
                romaji: row.romaji,
                te: row.te,
                ta: row.ta,
                tai: row.tai,
                conditional: row.conditional,
                nonPastPositive: row.non_past_plain_pos,
                nonPastNegative: row.non_past_plain_neg,
                politePositive: row.non_past_polite_pos,
                politeNegative: row.non_past_polite_neg,
                pastPositive: row.past_plain_pos,
                pastNegative: row.past_plain_neg,
                politePastPositive: row.past_polite_pos,
                politePastNegative: row.past_polite_neg,
                potentialPlainPositive: row.potential_plain_pos,
                potentialPlainNegative: row.potential_plain_neg,
                potentialPolitePositive: row.potential_polite_pos,
                potentialPoliteNegative: row.potential_polite_neg,
                potentialPastPositive: row.potential_past_pos,
                potentialPastNegative: row.potential_past_neg,
                volitionalPlainPositive: row.volitional_plain_pos,
                volitionalPlainNegative: row.volitional_plain_neg,
                volitionalPolitePositive: row.volitional_polite_pos,
                volitionalPoliteNegative: row.volitional_polite_neg
              });
            });
            
            setWords(parsedWords);
            setLoading(false);
            // Select initial random word
            const wordsList = Object.values(parsedWords);
            if (wordsList.length > 0) {
              setCurrentWord(wordsList[Math.floor(Math.random() * wordsList.length)]);
            }
          },
          error: (error) => {
            console.error('Error parsing CSV:', error);
            setError('Failed to parse word data');
            setLoading(false);
          }
        });
      } catch (error) {
        console.error('Error loading CSV:', error);
        setError('Failed to load word data');
        setLoading(false);
      }
    };

    loadWords();
  }, []);

  const handleInputChange = (field, value) => {
    setUserAnswers(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const selectRandomWord = () => {
    const wordsList = Object.values(words);
    if (wordsList.length === 0) return;
    
    const randomWord = wordsList[Math.floor(Math.random() * wordsList.length)];
    setCurrentWord(randomWord);
    
    // Reset user answers
    setUserAnswers({
      nonPastPlainPositive: '',
      nonPastPlainNegative: '',
      nonPastPolitePositive: '',
      nonPastPoliteNegative: '',
      pastPlainPositive: '',
      pastPlainNegative: '',
      pastPolitePositive: '',
      pastPoliteNegative: ''
    });
    
    // Reset feedback
    setFeedback({
      isSubmitted: false,
      isCorrect: false,
      correctAnswers: null
    });
  
    // Update timer for scoring
    setScore(prev => ({
      ...prev,
      startTime: new Date()
    }));
  };

  const checkAnswers = () => {
    if (!currentWord) return;

    const isCorrect = 
      userAnswers.nonPastPlainPositive === currentWord.non_past.plain.positive &&
      userAnswers.nonPastPlainNegative === currentWord.non_past.plain.negative &&
      userAnswers.nonPastPolitePositive === currentWord.non_past.polite.positive &&
      userAnswers.nonPastPoliteNegative === currentWord.non_past.polite.negative &&
      userAnswers.pastPlainPositive === currentWord.past.plain.positive &&
      userAnswers.pastPlainNegative === currentWord.past.plain.negative &&
      userAnswers.pastPolitePositive === currentWord.past.polite.positive &&
      userAnswers.pastPoliteNegative === currentWord.past.polite.negative;

    setFeedback({
      isSubmitted: true,
      isCorrect,
      correctAnswers: {
        nonPastPlainPositive: currentWord.non_past.plain.positive,
        nonPastPlainNegative: currentWord.non_past.plain.negative,
        nonPastPolitePositive: currentWord.non_past.polite.positive,
        nonPastPoliteNegative: currentWord.non_past.polite.negative,
        pastPlainPositive: currentWord.past.plain.positive,
        pastPlainNegative: currentWord.past.plain.negative,
        pastPolitePositive: currentWord.past.polite.positive,
        pastPoliteNegative: currentWord.past.polite.negative
      }
    });

    setScore(prev => ({
      ...prev,
      correct: prev.correct + (isCorrect ? 1 : 0),
      total: prev.total + 1,
      answeredTime: new Date()
    }));

    // Move to next word after 3 seconds
    setTimeout(() => {
      setUserAnswers({
        nonPastPlainPositive: '',
        nonPastPlainNegative: '',
        nonPastPolitePositive: '',
        nonPastPoliteNegative: '',
        pastPlainPositive: '',
        pastPlainNegative: '',
        pastPolitePositive: '',
        pastPoliteNegative: ''
      });
      setFeedback({
        isSubmitted: false,
        isCorrect: false,
        correctAnswers: null
      });
      selectRandomWord();
    }, 3000);
  };

  const renderInputField = (label, field) => (
    <div>
      <label className="block text-sm font-medium mb-1 text-foreground">{label}</label>
      <Input
        value={userAnswers[field]}
        onChange={(e) => handleInputChange(field, e.target.value)}
        className={feedback.isSubmitted ? 
          (userAnswers[field] === feedback.correctAnswers?.[field] ? 'border-green-500 bg-green-500/10' : 'border-red-500 bg-red-500/10') 
          : ''}
      />
      {feedback.isSubmitted && userAnswers[field] !== feedback.correctAnswers?.[field] && (
        <div className="text-sm text-red-400 mt-1">
          Correct: {feedback.correctAnswers[field]}
        </div>
      )}
    </div>
  );

  return (
    <Card className="w-full max-w-2xl mx-auto bg-card">
      <CardHeader className="text-center">
        {loading ? (
          <div>Loading word data...</div>
        ) : error ? (
          <div className="text-red-400">{error}</div>
        ) : currentWord ? (
          <>
            <h2 className="text-2xl font-bold text-foreground">Japanese {currentWord.type === 'verb' ? 'Verb' : 'Adjective'} Quiz</h2>
            <div className="text-lg text-foreground">
              <ruby>
                {currentWord.kanji}
                <rt>{currentWord.hiragana}</rt>
              </ruby>
            </div>
            <div className="text-sm text-muted-foreground">
              {currentWord.english}
              <div className="text-xs mt-1">
                Type: {currentWord.type}
                {currentWord.group && ` (${currentWord.group}-group)`}
              </div>
            </div>
            <div className="mt-2 text-foreground">
              Score: {score.correct}/{score.total}
            </div>
          </>
        ) : null}
      </CardHeader>

      {!loading && !error && currentWord && (
        <CardContent>
          <Tabs defaultValue="present" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-muted">
              <TabsTrigger value="present">Present Tense</TabsTrigger>
              <TabsTrigger value="past">Past Tense</TabsTrigger>
            </TabsList>
            
            <TabsContent value="present" className="space-y-4">
              {renderInputField('Plain Form Positive', 'nonPastPlainPositive')}
              {renderInputField('Plain Form Negative', 'nonPastPlainNegative')}
              {renderInputField('Polite Form Positive', 'nonPastPolitePositive')}
              {renderInputField('Polite Form Negative', 'nonPastPoliteNegative')}
            </TabsContent>
            
            <TabsContent value="past" className="space-y-4">
              {renderInputField('Plain Form Positive (Past)', 'pastPlainPositive')}
              {renderInputField('Plain Form Negative (Past)', 'pastPlainNegative')}
              {renderInputField('Polite Form Positive (Past)', 'pastPolitePositive')}
              {renderInputField('Polite Form Negative (Past)', 'pastPoliteNegative')}
            </TabsContent>
          </Tabs>

          <Button 
            onClick={checkAnswers}
            disabled={feedback.isSubmitted}
            className="w-full mt-4 bg-primary text-primary-foreground hover:bg-primary/90"
          >
            Submit
          </Button>
        </CardContent>
      )}
    </Card>
  );
};

export default JapaneseQuiz;