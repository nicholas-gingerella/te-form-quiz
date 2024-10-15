const words = [
    { kanji: "食べる", hiragana: "たべる", teForm: "たべて", kanjiTeForm: "食べて", romajiTeForm: "tabete", english: "to eat" },
    { kanji: "行く", hiragana: "いく", teForm: "いって", kanjiTeForm: "行って", romajiTeForm: "itte", english: "to go" },
    { kanji: "見る", hiragana: "みる", teForm: "みて", kanjiTeForm: "見て", romajiTeForm: "mite", english: "to look/see" },
    { kanji: "来る", hiragana: "くる", teForm: "きて", kanjiTeForm: "来て", romajiTeForm: "kite", english: "to come" },
    { kanji: "する", hiragana: "する", teForm: "して", kanjiTeForm: "して", romajiTeForm: "shite", english: "to do" },
    { kanji: "話す", hiragana: "はなす", teForm: "はなして", kanjiTeForm: "話して", romajiTeForm: "hanashite", english: "to speak/converse" },
    { kanji: "書く", hiragana: "かく", teForm: "かいて", kanjiTeForm: "書いて", romajiTeForm: "kaite", english: "to write" },
    { kanji: "読む", hiragana: "よむ", teForm: "よんで", kanjiTeForm: "読んで", romajiTeForm: "yonde", english: "to read" },
    { kanji: "聞く", hiragana: "きく", teForm: "きいて", kanjiTeForm: "聞いて", romajiTeForm: "kiite", english: "to hear/listen" },
    { kanji: "飲む", hiragana: "のむ", teForm: "のんで", kanjiTeForm: "飲んで", romajiTeForm: "nonde", english: "to drink" },
    { kanji: "買う", hiragana: "かう", teForm: "かって", kanjiTeForm: "買って", romajiTeForm: "katte", english: "" },
    { kanji: "待つ", hiragana: "まつ", teForm: "まって", kanjiTeForm: "待って", romajiTeForm: "matte", english: "to wait" },
    { kanji: "作る", hiragana: "つくる", teForm: "つくって", kanjiTeForm: "作って", romajiTeForm: "tsukutte", english: "to make" },
    { kanji: "使う", hiragana: "つかう", teForm: "つかって", kanjiTeForm: "使って", romajiTeForm: "tsukatte", english: "to use" },
    { kanji: "走る", hiragana: "はしる", teForm: "はしって", kanjiTeForm: "走って", romajiTeForm: "hashitte", english: "" },
    { kanji: "持つ", hiragana: "もつ", teForm: "もって", kanjiTeForm: "持って", romajiTeForm: "motte", english: "" },
    { kanji: "死ぬ", hiragana: "しぬ", teForm: "しんで", kanjiTeForm: "死んで", romajiTeForm: "shinde", english: "" },
    { kanji: "帰る", hiragana: "かえる", teForm: "かえって", kanjiTeForm: "帰って", romajiTeForm: "kaette", english: "" },
    { kanji: "泳ぐ", hiragana: "およぐ", teForm: "およいで", kanjiTeForm: "泳いで", romajiTeForm: "oyoide", english: "" },
    { kanji: "遊ぶ", hiragana: "あそぶ", teForm: "あそんで", kanjiTeForm: "遊んで", romajiTeForm: "asonde", english: "" },
    { kanji: "会う", hiragana: "あう", teForm: "あって", kanjiTeForm: "会って", romajiTeForm: "atte", english: "" },
    { kanji: "分かる", hiragana: "わかる", teForm: "わかって", kanjiTeForm: "分かって", romajiTeForm: "wakatte", english: "" },
    { kanji: "教える", hiragana: "おしえる", teForm: "おしえて", kanjiTeForm: "教えて", romajiTeForm: "oshiete", english: "" },
    { kanji: "立つ", hiragana: "たつ", teForm: "たって", kanjiTeForm: "立って", romajiTeForm: "tatte", english: "" },
    { kanji: "運ぶ", hiragana: "はこぶ", teForm: "はこんで", kanjiTeForm: "運んで", romajiTeForm: "hakonde", english: "" },
    { kanji: "洗う", hiragana: "あらう", teForm: "あらって", kanjiTeForm: "洗って", romajiTeForm: "aratte", english: "" },
    { kanji: "開ける", hiragana: "あける", teForm: "あけて", kanjiTeForm: "開けて", romajiTeForm: "akete", english: "" },
    { kanji: "乗る", hiragana: "のる", teForm: "のって", kanjiTeForm: "乗って", romajiTeForm: "notte", english: "" },
    { kanji: "降りる", hiragana: "おりる", teForm: "おりて", kanjiTeForm: "降りて", romajiTeForm: "orite", english: "" },
    { kanji: "選ぶ", hiragana: "えらぶ", teForm: "えらんで", kanjiTeForm: "選んで", romajiTeForm: "erande", english: "" },
    { kanji: "着る", hiragana: "きる", teForm: "きて", kanjiTeForm: "着て", romajiTeForm: "kite", english: "" },
    { kanji: "切る", hiragana: "きる", teForm: "きって", kanjiTeForm: "切って", romajiTeForm: "kitte", english: "" },
    { kanji: "寝る", hiragana: "ねる", teForm: "ねて", kanjiTeForm: "寝て", romajiTeForm: "nete", english: "" },
    { kanji: "起きる", hiragana: "おきる", teForm: "おきて", kanjiTeForm: "起きて", romajiTeForm: "okite", english: "" },
    { kanji: "終わる", hiragana: "おわる", teForm: "おわって", kanjiTeForm: "終わって", romajiTeForm: "owatte", english: "" },
    { kanji: "始める", hiragana: "はじめる", teForm: "はじめて", kanjiTeForm: "始めて", romajiTeForm: "hajimete", english: "" },
    { kanji: "送る", hiragana: "おくる", teForm: "おくって", kanjiTeForm: "送って", romajiTeForm: "okutte", english: "" },
    { kanji: "受ける", hiragana: "うける", teForm: "うけて", kanjiTeForm: "受けて", romajiTeForm: "ukete", english: "" },
    { kanji: "立てる", hiragana: "たてる", teForm: "たてて", kanjiTeForm: "立てて", romajiTeForm: "tatete", english: "" }
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
    document.getElementById("english").innerText = "";
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
      document.getElementById("english").innerText = `${word.english}`;
      document.getElementById("feedback").style.color = "green";
      document.getElementById("english").style.color = "green";
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