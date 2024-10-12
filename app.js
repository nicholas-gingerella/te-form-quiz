const words = [
    { kanji: "食べる", hiragana: "たべる", teForm: "たべて", kanjiTeForm: "食べて", romajiTeForm: "tabete" },
    { kanji: "行く", hiragana: "いく", teForm: "いって", kanjiTeForm: "行って", romajiTeForm: "itte" },
    { kanji: "見る", hiragana: "みる", teForm: "みて", kanjiTeForm: "見て", romajiTeForm: "mite" },
    { kanji: "来る", hiragana: "くる", teForm: "きて", kanjiTeForm: "来て", romajiTeForm: "kite" },
    { kanji: "する", hiragana: "する", teForm: "して", kanjiTeForm: "して", romajiTeForm: "shite" },
    { kanji: "話す", hiragana: "はなす", teForm: "はなして", kanjiTeForm: "話して", romajiTeForm: "hanashite" },
    { kanji: "書く", hiragana: "かく", teForm: "かいて", kanjiTeForm: "書いて", romajiTeForm: "kaite" },
    { kanji: "読む", hiragana: "よむ", teForm: "よんで", kanjiTeForm: "読んで", romajiTeForm: "yonde" },
    { kanji: "聞く", hiragana: "きく", teForm: "きいて", kanjiTeForm: "聞いて", romajiTeForm: "kiite" },
    { kanji: "飲む", hiragana: "のむ", teForm: "のんで", kanjiTeForm: "飲んで", romajiTeForm: "nonde" },
    { kanji: "買う", hiragana: "かう", teForm: "かって", kanjiTeForm: "買って", romajiTeForm: "katte" },
    { kanji: "待つ", hiragana: "まつ", teForm: "まって", kanjiTeForm: "待って", romajiTeForm: "matte" },
    { kanji: "作る", hiragana: "つくる", teForm: "つくって", kanjiTeForm: "作って", romajiTeForm: "tsukutte" },
    { kanji: "使う", hiragana: "つかう", teForm: "つかって", kanjiTeForm: "使って", romajiTeForm: "tsukatte" },
    { kanji: "走る", hiragana: "はしる", teForm: "はしって", kanjiTeForm: "走って", romajiTeForm: "hashitte" },
    { kanji: "持つ", hiragana: "もつ", teForm: "もって", kanjiTeForm: "持って", romajiTeForm: "motte" },
    { kanji: "死ぬ", hiragana: "しぬ", teForm: "しんで", kanjiTeForm: "死んで", romajiTeForm: "shinde" },
    { kanji: "帰る", hiragana: "かえる", teForm: "かえって", kanjiTeForm: "帰って", romajiTeForm: "kaette" },
    { kanji: "泳ぐ", hiragana: "およぐ", teForm: "およいで", kanjiTeForm: "泳いで", romajiTeForm: "oyoide" },
    { kanji: "遊ぶ", hiragana: "あそぶ", teForm: "あそんで", kanjiTeForm: "遊んで", romajiTeForm: "asonde" },
    { kanji: "立つ", hiragana: "たつ", teForm: "たって", kanjiTeForm: "立って", romajiTeForm: "tatte" },
    { kanji: "読む", hiragana: "よむ", teForm: "よんで", kanjiTeForm: "読んで", romajiTeForm: "yonde" },
    { kanji: "会う", hiragana: "あう", teForm: "あって", kanjiTeForm: "会って", romajiTeForm: "atte" },
    { kanji: "分かる", hiragana: "わかる", teForm: "わかって", kanjiTeForm: "分かって", romajiTeForm: "wakatte" },
    { kanji: "聞く", hiragana: "きく", teForm: "きいて", kanjiTeForm: "聞いて", romajiTeForm: "kiite" },
    { kanji: "教える", hiragana: "おしえる", teForm: "おしえて", kanjiTeForm: "教えて", romajiTeForm: "oshiete" },
    { kanji: "立つ", hiragana: "たつ", teForm: "たって", kanjiTeForm: "立って", romajiTeForm: "tatte" },
    { kanji: "運ぶ", hiragana: "はこぶ", teForm: "はこんで", kanjiTeForm: "運んで", romajiTeForm: "hakonde" },
    { kanji: "洗う", hiragana: "あらう", teForm: "あらって", kanjiTeForm: "洗って", romajiTeForm: "aratte" },
    { kanji: "走る", hiragana: "はしる", teForm: "はしって", kanjiTeForm: "走って", romajiTeForm: "hashitte" },
    { kanji: "開ける", hiragana: "あける", teForm: "あけて", kanjiTeForm: "開けて", romajiTeForm: "akete" },
    { kanji: "乗る", hiragana: "のる", teForm: "のって", kanjiTeForm: "乗って", romajiTeForm: "notte" },
    { kanji: "降りる", hiragana: "おりる", teForm: "おりて", kanjiTeForm: "降りて", romajiTeForm: "orite" },
    { kanji: "使う", hiragana: "つかう", teForm: "つかって", kanjiTeForm: "使って", romajiTeForm: "tsukatte" },
    { kanji: "選ぶ", hiragana: "えらぶ", teForm: "えらんで", kanjiTeForm: "選んで", romajiTeForm: "erande" },
    { kanji: "着る", hiragana: "きる", teForm: "きて", kanjiTeForm: "着て", romajiTeForm: "kite" },
    { kanji: "切る", hiragana: "きる", teForm: "きって", kanjiTeForm: "切って", romajiTeForm: "kitte" },
    { kanji: "寝る", hiragana: "ねる", teForm: "ねて", kanjiTeForm: "寝て", romajiTeForm: "nete" },
    { kanji: "起きる", hiragana: "おきる", teForm: "おきて", kanjiTeForm: "起きて", romajiTeForm: "okite" },
    { kanji: "終わる", hiragana: "おわる", teForm: "おわって", kanjiTeForm: "終わって", romajiTeForm: "owatte" },
    { kanji: "始める", hiragana: "はじめる", teForm: "はじめて", kanjiTeForm: "始めて", romajiTeForm: "hajimete" },
    { kanji: "送る", hiragana: "おくる", teForm: "おくって", kanjiTeForm: "送って", romajiTeForm: "okutte" },
    { kanji: "受ける", hiragana: "うける", teForm: "うけて", kanjiTeForm: "受けて", romajiTeForm: "ukete" },
    { kanji: "立てる", hiragana: "たてる", teForm: "たてて", kanjiTeForm: "立てて", romajiTeForm: "tatete" }
];
  
  let currentWordIndex = 0;
  let score = 0;
  let userAnswers = [];
  let isAnswerSubmitted = false;
  
  document.getElementById("start-button").addEventListener("click", startQuiz);
  document.getElementById("submit-button").addEventListener("click", handleSubmit);
  document.getElementById("answer-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
      handleSubmit();
    }
  });
  
  function startQuiz() {
    document.getElementById("start-button").style.display = "none";
    document.getElementById("quiz-area").style.display = "block";
    shuffleWords();
    showWord();
  }
  
  function shuffleWords() {
    for (let i = words.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [words[i], words[j]] = [words[j], words[i]];
    }
  }
  
  function showWord() {
    const word = words[currentWordIndex];
    document.getElementById("word-display").innerText = `${word.kanji} / ${word.hiragana}`;
    document.getElementById("answer-input").value = "";
    document.getElementById("feedback").innerText = "";
    document.getElementById("answer-input").focus();
    document.getElementById("submit-button").disabled = false;
    isAnswerSubmitted = false;
  }
  
  function handleSubmit() {
    if (!isAnswerSubmitted) {
      isAnswerSubmitted = true;
      document.getElementById("submit-button").disabled = true;
      checkAnswer();
    }
  }
  
  function checkAnswer() {
    const userAnswer = document.getElementById("answer-input").value.trim().toLowerCase();
    const word = words[currentWordIndex];
    const correctAnswers = [word.teForm, word.kanjiTeForm, word.romajiTeForm];
    
    const isCorrect = correctAnswers.includes(userAnswer);
    if (isCorrect) {
      score++;
      document.getElementById("feedback").innerText = "Correct!";
      document.getElementById("feedback").style.color = "green";
    } else {
      document.getElementById("feedback").innerText = `Incorrect. The correct answer is ${word.kanjiTeForm} (${word.teForm} / ${word.romajiTeForm}).`;
      document.getElementById("feedback").style.color = "red";
    }
  
    userAnswers.push({ word, userAnswer, isCorrect });
    
    setTimeout(nextWord, isCorrect ? 1500 : 3000);
  }
  
  function nextWord() {
    currentWordIndex++;
    
    if (currentWordIndex < words.length) {
      showWord();
    } else {
      showResults();
    }
  }
  
  function showResults() {
    document.getElementById("quiz-area").style.display = "none";
    const resultsContainer = document.createElement("div");
    resultsContainer.id = "results-container";
    resultsContainer.innerHTML = `
      <h2>Quiz Complete!</h2>
      <p>Your score: ${score} / ${words.length}</p>
      <h3>Results:</h3>
      <ul id="results-list"></ul>
      <button id="restart-button">Restart Quiz</button>
    `;
    document.querySelector(".container").appendChild(resultsContainer);
    
    const resultsList = document.getElementById("results-list");
    userAnswers.forEach(({ word, userAnswer, isCorrect }) => {
      const listItem = document.createElement("li");
      listItem.className = isCorrect ? "correct" : "incorrect";
      listItem.innerHTML = `
        <strong>${word.kanji} / ${word.hiragana}</strong><br>
        Correct: ${word.kanjiTeForm} (${word.teForm} / ${word.romajiTeForm})<br>
        Your answer: ${userAnswer}
      `;
      resultsList.appendChild(listItem);
    });
    
    document.getElementById("restart-button").addEventListener("click", () => {
      location.reload();
    });
  }