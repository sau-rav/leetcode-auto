fetch("../data/state.json")
  .then(r => r.json())
  .then(state => {
    const list = document.getElementById("list");

    state.problems
      .filter(p => p.status === "solved")
      .forEach(p => {
        const li = document.createElement("li");
        li.textContent = `${p.title} (${p.difficulty})`;
        list.appendChild(li);
      });
  });

