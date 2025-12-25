const today = new Date().toISOString().split("T")[0];

fetch("./data/state.json")
  .then(r => r.json())
  .then(state => {
    const list = document.getElementById("list");
    const problems = state.assigned[today] || [];

    if (!problems.length) {
      list.innerHTML = "<li>No problems assigned today</li>";
      return;
    }

    problems.forEach(p => {
      const li = document.createElement("li");
      li.innerHTML = `
        <a href="https://leetcode.com/problems/${p.slug}" target="_blank">
          ${p.title} (${p.difficulty})
        </a>
        — ${p.status}
        ${p.solve_later ? "<span style='color:orange'>(Solve Later)</span>" : ""}
      `;
      list.appendChild(li);
    });
  });

