fetch("../data/state.json")
  .then(r => r.json())
  .then(state => {
    const today = new Date().toISOString().slice(0, 10);
    const list = document.getElementById("list");

    state.problems
      .filter(p =>
        p.assigned_on === today &&
        p.status === "pending" &&
        !p.solve_later
      )
      .forEach(p => {
        const li = document.createElement("li");
        li.innerHTML = `
          <a href="https://leetcode.com/problems/${p.slug}/" target="_blank">
            ${p.title}
          </a>
          (${p.difficulty})
          <code>${p.slug}</code>
        `;
        list.appendChild(li);
      });
  });

