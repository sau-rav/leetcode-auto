const today = new Date().toISOString().slice(0, 10);
const page = window.location.pathname;

fetch("data/state.json")
  .then(r => r.json())
  .then(data => render(data));

function render(state) {
  const list = document.getElementById("problem-list");
  let problems = state.problems;

  if (page.includes("solved.html")) {
    problems = problems.filter(p => p.status === "solved");
  } else if (page.includes("solve-later.html")) {
    problems = problems.filter(p => p.solve_later === true);
  } else {
    problems = problems.filter(
      p =>
        p.status === "pending" &&
        p.assigned_on === today &&
        !p.solve_later
    );
  }

  if (problems.length === 0) {
    list.innerHTML = "<p>No problems here 🎉</p>";
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
        <span class="badge">${p.difficulty}</span>
        <span class="badge">Slug: ${p.slug}</span>
      </div>
      <div class="actions">
        <button onclick="copySlug('${p.slug}')">Copy Slug</button>
      </div>
    `;

    list.appendChild(div);
  });
}

function copySlug(slug) {
  navigator.clipboard.writeText(slug).then(() => {
    alert(`Copied: ${slug}`);
  });
}

