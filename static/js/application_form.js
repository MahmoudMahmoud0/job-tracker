(() => {
    const addButton = document.getElementById("add-tag-row");
    const rowsContainer = document.getElementById("new-tag-rows");
    const tagSearchInput = document.getElementById("existing-tag-search");
    const existingTagPicker = document.getElementById("existing-tag-picker");
    const existingTagEmpty = document.getElementById("existing-tag-empty");
    const palette = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#84cc16", "#f97316"];

    if (!addButton || !rowsContainer) {
        return;
    }

    const updateExistingTagVisibility = () => {
        if (!tagSearchInput || !existingTagPicker) {
            return;
        }

        const query = tagSearchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        existingTagPicker.querySelectorAll(".existing-tag-option").forEach((option) => {
            const name = option.dataset.tagName || "";
            const isVisible = !query || name.includes(query);
            option.hidden = !isVisible;
            if (isVisible) {
                visibleCount += 1;
            }
        });

        if (existingTagEmpty) {
            existingTagEmpty.classList.toggle("hidden", visibleCount > 0 || !query);
        }
    };

    const syncExistingTagStyles = () => {
        existingTagPicker?.querySelectorAll(".existing-tag-option").forEach((option) => {
            const checkbox = option.querySelector('input[type="checkbox"]');
            const isChecked = Boolean(checkbox?.checked);
            option.classList.toggle("border-blue-300", isChecked);
            option.classList.toggle("bg-blue-50", isChecked);
            option.classList.toggle("text-blue-700", isChecked);
        });
    };

    const syncExistingTagColors = () => {
        existingTagPicker?.querySelectorAll(".existing-tag-color-dot").forEach((dot) => {
            dot.style.backgroundColor = dot.dataset.tagColor || "#10b981";
        });
    };

    const updateRemoveButtons = () => {
        const rows = rowsContainer.querySelectorAll(".tag-row");
        rows.forEach((row) => {
            const button = row.querySelector(".remove-tag-row");
            button.disabled = rows.length === 1;
            button.classList.toggle("opacity-50", rows.length === 1);
            button.classList.toggle("cursor-not-allowed", rows.length === 1);
        });
    };

    const buildRow = (color) => {
        const wrapper = document.createElement("div");
        wrapper.className = "tag-row grid gap-3 rounded-[1.25rem] border border-emerald-100 bg-white/90 p-4 md:grid-cols-[1fr_auto_auto] md:items-end";
        wrapper.innerHTML = `
            <div>
                <label class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Tag name</label>
                <input
                    type="text"
                    name="new_tag_name"
                    placeholder="Remote, urgent, referral..."
                    class="mt-2 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
                >
            </div>
            <div>
                <label class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Color</label>
                <input
                    type="color"
                    name="new_tag_color"
                    value="${color}"
                    class="mt-2 h-[50px] w-full min-w-20 rounded-2xl border border-slate-300 bg-white px-2 py-2"
                >
            </div>
            <button
                type="button"
                class="remove-tag-row inline-flex items-center justify-center rounded-full border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-100"
            >
                Remove
            </button>
        `;
        return wrapper;
    };

    addButton.addEventListener("click", () => {
        const nextColor = palette[rowsContainer.querySelectorAll(".tag-row").length % palette.length];
        rowsContainer.appendChild(buildRow(nextColor));
        updateRemoveButtons();
    });

    rowsContainer.addEventListener("click", (event) => {
        const button = event.target.closest(".remove-tag-row");
        if (!button) {
            return;
        }

        const rows = rowsContainer.querySelectorAll(".tag-row");
        if (rows.length === 1) {
            return;
        }

        button.closest(".tag-row")?.remove();
        updateRemoveButtons();
    });

    tagSearchInput?.addEventListener("input", updateExistingTagVisibility);
    existingTagPicker?.addEventListener("change", syncExistingTagStyles);
    updateRemoveButtons();
    updateExistingTagVisibility();
    syncExistingTagStyles();
    syncExistingTagColors();
})();
