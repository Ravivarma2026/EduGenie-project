/* EduGenie frontend: task dropdown -> FastAPI endpoints -> rendered result */
(function () {
  "use strict";

  const TASKS = {
    qa: {
      label: "Your question", title: "Answer", button: "Ask",
      placeholder: "Which is the largest ocean?",
      examples: ["Which is the largest ocean?", "Why is the sky blue?", "Who discovered penicillin?"],
    },
    explain: {
      label: "Concept to explain", title: "Explanation", button: "Explain",
      placeholder: "quantum computing",
      examples: ["Quantum computing", "Photosynthesis", "Recursion in programming"],
    },
    quiz: {
      label: "Passage or topic for the quiz", title: "Quiz", button: "Generate Quiz",
      placeholder: "Paste a passage or type a topic, e.g. The Pythagoras Theorem",
      examples: ["The Pythagoras Theorem", "The water cycle", "Newton's laws of motion"],
    },
    summarize: {
      label: "Text to summarize", title: "Summary", button: "Summarize",
      placeholder: "Paste a long paragraph or article here...",
      examples: [],
    },
    recommend: {
      label: "Topic you want to learn", title: "Learning Path", button: "Create Learning Path",
      placeholder: "SQL",
      examples: ["SQL", "Machine Learning", "Web development"],
    },
  };

  const $ = (id) => document.getElementById(id);
  const form = $("edu-form"), taskEl = $("task"), inputEl = $("user-input");
  const submitBtn = $("submit-btn"), btnText = $("btn-text");
  const resultCard = $("result-card"), resultEl = $("result"), resultTitle = $("result-title");

  function escapeHtml(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function inline(s) {
    let t = escapeHtml(s);
    t = t.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    t = t.replace(/(^|[^*])\*(?!\s)([^*]+?)\*(?!\*)/g, "$1<em>$2</em>");
    t = t.replace(/`([^`]+)`/g, "<code>$1</code>");
    t = t.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    return t;
  }

  /* Small, safe Markdown renderer (headings, lists, bold, links, paragraphs). */
  function renderMarkdown(md) {
    const lines = String(md).replace(/\r/g, "").split("\n");
    let html = "", list = null;
    const close = () => { if (list) { html += `</${list}>`; list = null; } };
    for (const raw of lines) {
      const line = raw.replace(/\s+$/, "");
      let m;
      if (!line.trim()) { close(); continue; }
      if ((m = line.match(/^\s*(#{1,6})\s+(.*)$/))) {
        close();
        const lvl = Math.min(m[1].length + 2, 5);
        html += `<h${lvl}>${inline(m[2])}</h${lvl}>`;
      } else if ((m = line.match(/^\s*[*\-+]\s+(.*)$/))) {
        if (list !== "ul") { close(); html += "<ul>"; list = "ul"; }
        html += `<li>${inline(m[1])}</li>`;
      } else if ((m = line.match(/^\s*\d+[.)]\s+(.*)$/))) {
        if (list !== "ol") { close(); html += "<ol>"; list = "ol"; }
        html += `<li>${inline(m[1])}</li>`;
      } else {
        close();
        html += `<p>${inline(line.trim())}</p>`;
      }
    }
    close();
    return html;
  }

  function applyTask() {
    const t = TASKS[taskEl.value];
    $("input-label").textContent = t.label;
    inputEl.placeholder = t.placeholder;
    btnText.textContent = t.button;
    const box = $("examples");
    box.innerHTML = "";
    t.examples.forEach((ex) => {
      const chip = document.createElement("button");
      chip.type = "button"; chip.className = "chip"; chip.textContent = ex;
      chip.addEventListener("click", () => { inputEl.value = ex; inputEl.focus(); });
      box.appendChild(chip);
    });
  }

  function setLoading(on) {
    submitBtn.disabled = on;
    submitBtn.classList.toggle("loading", on);
  }

  function showResult(title, html, isError) {
    resultTitle.textContent = title;
    resultEl.innerHTML = isError ? `<div class="error">${html}</div>` : html;
    resultCard.classList.remove("hidden");
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  async function callApi(task, text) {
    let res;
    if (task === "qa") {
      res = await fetch("/qa?question=" + encodeURIComponent(text));
    } else {
      const map = {
        explain: ["/explain/", { topic: text }],
        quiz: ["/quiz", { text: text }],
        summarize: ["/summarize/", { text: text }],
        recommend: ["/learn/recommendations", { topic: text }],
      };
      const [url, body] = map[task];
      res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    }
    let data = {};
    try { data = await res.json(); } catch (_) { /* non-JSON error page */ }
    if (!res.ok || data.error) {
      throw new Error(data.error || data.detail || `Request failed (${res.status})`);
    }
    return data;
  }

  function renderQuiz(quiz) {
    resultEl.innerHTML = "";
    let answered = 0, correct = 0;
    const score = document.createElement("div");
    score.className = "score";

    quiz.forEach((q, i) => {
      const box = document.createElement("div");
      box.className = "q";
      const title = document.createElement("div");
      title.className = "q-title";
      title.textContent = `Q${i + 1}. ${q.question}`;
      box.appendChild(title);
      const fb = document.createElement("div");
      fb.className = "feedback";
      const buttons = [];

      q.options.forEach((opt, idx) => {
        const b = document.createElement("button");
        b.type = "button"; b.className = "opt";
        b.textContent = `${String.fromCharCode(65 + idx)}. ${opt}`;
        b.addEventListener("click", () => {
          buttons.forEach((x) => (x.disabled = true));
          const isRight = opt === q.answer;
          b.classList.add(isRight ? "correct" : "wrong");
          if (isRight) {
            fb.className = "feedback ok"; fb.textContent = "Correct!"; correct++;
          } else {
            buttons.forEach((x) => { if (x.dataset.opt === q.answer) x.classList.add("correct"); });
            fb.className = "feedback bad"; fb.textContent = `Not quite. Correct answer: ${q.answer}`;
          }
          answered++;
          if (answered === quiz.length) score.textContent = `Your score: ${correct} / ${quiz.length}`;
        });
        b.dataset.opt = opt;
        buttons.push(b);
        box.appendChild(b);
      });
      box.appendChild(fb);
      resultEl.appendChild(box);
    });
    resultEl.appendChild(score);
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const task = taskEl.value, text = inputEl.value.trim();
    if (!text) {
      showResult("Oops", "Please enter some text first.", true);
      return;
    }
    setLoading(true);
    try {
      const data = await callApi(task, text);
      const title = TASKS[task].title;
      if (task === "quiz") {
        resultTitle.textContent = title;
        resultCard.classList.remove("hidden");
        renderQuiz(data.quiz);
        resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
      } else {
        const body = data.answer || data.explanation || data.summary || data.recommendations || "";
        showResult(title, renderMarkdown(body), false);
      }
    } catch (err) {
      showResult("Error", escapeHtml(err.message || "Something went wrong."), true);
    } finally {
      setLoading(false);
    }
  });

  taskEl.addEventListener("change", applyTask);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) form.requestSubmit();
  });
  applyTask();
})();
