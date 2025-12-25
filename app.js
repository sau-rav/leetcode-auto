const today = new Date().toISOString().slice(0, 10);
const page = window.location.pathname;

fetch("data/state.json")
  .then(r => r.json())
  .then(state => render(state));

function render(state) {
  const list = document.getElementById("problem-list");
  const main = document.querySelector("main");

  let problems = state.problems;

  if (page.includes("solved.html")) {
    problems = problems.filter(p => p.status === "solved");
    addSubtitle(main, `${problems.length} problems solved`);
  }
  else if (page.includes("solve-later.html")) {
    problems = problems.filter(p => p.solve_later === true);
    addSubtitle(main, `${problems.length} problems marked for later`);
  }
  else {
    problems = problems.filter(
      p =>
        p.status === "pending" &&
        p.assigned_on === today &&
        !p.solve_later
    );
    addSubtitle(main, `${problems.length} problems for today`);
  }

  if (problems.length === 0) {
    list.innerHTML = `
      <div class="empty">
        Nothing here yet 🚀<br />
        Run generate.py or mark problems for today.
      </div>
    `;
    return;
  }

  problems.forEach(p => {
    const div = document.createElement("div");
    div.className = "problem";

    div.innerHTML = `
      <div class="problem-info">
        <a href="https://leetcode.com/problems/${p.slug}/" target="_blank">
          ${p.title}
        </a>
        <div class="meta">
          <span class="badge ${p.difficulty.toLowerCase()}">${p.difficulty}</span>
          <span>Slug: ${p.slug}</span>
        </div>
      </div>
      <div class="actions">
        <button onclick="copySlug('${p.slug}')">Copy Slug</button>
      </div>
    `;

    list.appendChild(div);
  });
}

function addSubtitle(main, text) {
  const sub = document.createElement("div");
  sub.className = "subtitle";
  sub.innerText = text;
  main.insertBefore(sub, document.getElementById("problem-list"));
}

/* ===== TOAST ===== */
function copySlug(slug) {
  navigator.clipboard.writeText(slug);
  showToast(`Copied slug: ${slug}`);
}

function showToast(text) {
  let toast = document.querySelector(".toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "toast";
    document.body.appendChild(toast);
  }

  toast.innerText = text;
  toast.classList.add("show");

  setTimeout(() => toast.classList.remove("show"), 2000);
}

