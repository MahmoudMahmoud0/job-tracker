(() => {
    const boardScroll = document.getElementById("kanban-board-scroll");
    const boardContent = document.getElementById("kanban-board-content");
    const stickyScroll = document.getElementById("kanban-sticky-scroll");
    const stickyContent = document.getElementById("kanban-sticky-scroll-content");
    const stickyShell = document.getElementById("kanban-sticky-scroll-shell");

    if (!boardScroll || !boardContent || !stickyScroll || !stickyContent || !stickyShell) {
        return;
    }

    const syncStickyWidth = () => {
        stickyContent.style.width = `${boardContent.scrollWidth}px`;
    };

    const updateStickyVisibility = () => {
        const boardRect = boardScroll.getBoundingClientRect();
        const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
        const boardBottomVisible = boardRect.bottom <= viewportHeight;
        const needsHorizontalScroll = boardScroll.scrollWidth > boardScroll.clientWidth;

        stickyShell.classList.toggle("hidden", boardBottomVisible || !needsHorizontalScroll);
    };

    let syncingFromBoard = false;
    let syncingFromSticky = false;

    boardScroll.addEventListener("scroll", () => {
        if (syncingFromSticky) {
            syncingFromSticky = false;
            return;
        }

        syncingFromBoard = true;
        stickyScroll.scrollLeft = boardScroll.scrollLeft;
    });

    stickyScroll.addEventListener("scroll", () => {
        if (syncingFromBoard) {
            syncingFromBoard = false;
            return;
        }

        syncingFromSticky = true;
        boardScroll.scrollLeft = stickyScroll.scrollLeft;
    });

    window.addEventListener("resize", () => {
        syncStickyWidth();
        updateStickyVisibility();
    });
    window.addEventListener("scroll", updateStickyVisibility, { passive: true });

    syncStickyWidth();
    updateStickyVisibility();
    stickyScroll.scrollLeft = boardScroll.scrollLeft;
})();
