const today = new Date().toISOString().slice(0, 10);
const path = window.location.pathname;

fetch("data/state.json")
  .then(res => res.json())
  .then(state => render(state))
  .catch(() => {
    document.getElementById("problem-list").innerHTML =
      "<div class='empty'>Failed to load state.json</div>";
  });

function render(state) {
  const list = document.getElementById("problem-list");
  const subtitle = document.getElementById("page-subtitle");

  let problems = [];

  if (path.includes("solved.html")) {
    problems = state.problems.filter(p => p.status === "solved");
    subtitle.innerText = `${problems.length} solved problems`;
  } 
  else if (path.includes("solve-later.html")) {
    problems = state.problems.filter(p => p.solve_later);
    subtitle.innerText = `${problems.length} problems marked for later`;
  } 
  else {
    problems = state.problems.filter(
      p =>
        p.status === "pending" &&
        p.assigned_on === today &&
        !p.solve_later
    );
    subtitle.innerText = `${problems.length} problems for today`;
  }

  if (problems.length === 0) {
    list.innerHTML = `<div class="empty">No problems to show</div>`;
    return;
  }

  list.innerHTML = "";
  problems.forEach(p => {
    const div = document.createElement("div");
    div.className = "problem";

    div.innerHTML = `
      <div>
        <a class="problem-title" target="_blank"
           href="https://leetcode.com/problems/${p.slug}/">
           ${p.title}
        </a>
        <div class="meta">
          <span class="badge ${p.difficulty.toLowerCase()}">${p.difficulty}</span>
          <span>${p.slug}</span>
        </div>
      </div>
      <div class="actions">
        <button onclick="copySlug('${p.slug}')">Copy Slug</button>
      </div>
    `;

    list.appendChild(div);
  });
}

function copySlug(slug) {
  navigator.clipboard.writeText(slug);
  const toast = document.getElementById("toast");
  toast.innerText = `Copied slug: ${slug}`;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2000);
}

