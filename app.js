const today = new Date().toISOString().split("T")[0];

fetch("./data/state.json")
  .then(r => r.json())
  .then(state => {
    const list = document.getElementById("list");
    const problems = state.assigned[today] || [];

    // Only show pending problems and ignore solve_later
    const pending = problems.filter(p => p.status === "pending" && !p.solve_later);

    if (!pending.length) {
      list.innerHTML = "<li>No new problems pending today</li>";
      return;
    }

    pending.forEach(p => {
      const li = document.createElement("li");

      // Create copy button
      const copyBtn = document.createElement("button");
      copyBtn.textContent = "Copy Slug";
      copyBtn.style.marginLeft = "10px";
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(p.slug).then(() => {
          copyBtn.textContent = "Copied!";
          setTimeout(() => copyBtn.textContent = "Copy Slug", 1000);
        });
      };

      li.innerHTML = `
        <a href="https://leetcode.com/problems/${p.slug}" target="_blank">
          ${p.title}
        </a> 
        <code>(${p.slug})</code> - ${p.difficulty} - <strong>${p.status}</strong>
        ${p.solve_later ? "<span style='color:orange'>(Solve Later)</span>" : ""}
      `;
      li.appendChild(copyBtn);
      list.appendChild(li);
    });
  });

