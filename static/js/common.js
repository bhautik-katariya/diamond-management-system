// =================== COMMON.JS ===================
// Shared helper functions for dashboard, cart, orders, and diamonds pages.

// ---- Checkbox: Select All logic ----
function initSelectAllFeature(containerId = null) {
  const container = containerId ? document.getElementById(containerId) : document;
  if (!container) return;

  const selectAll = container.querySelector("#select-all");
  const rowChecks = container.querySelectorAll(".row-checkbox");
  if (!selectAll || rowChecks.length === 0) return;

  selectAll.addEventListener("change", () => {
    rowChecks.forEach(cb => cb.checked = selectAll.checked);
    selectAll.indeterminate = false;
  });

  rowChecks.forEach(cb => {
    cb.addEventListener("change", () => {
      const total = rowChecks.length;
      const checked = Array.from(rowChecks).filter(x => x.checked).length;
      selectAll.checked = checked === total;
      selectAll.indeterminate = checked > 0 && checked < total;
    });
  });
}

// ---- Pagination Input (Enter/Blur) ----
// wrapperSelector = parent element that contains pagination inputs
// loadCallback = function that fetches new data when page changes
function initPageInput(wrapperSelector, loadCallback) {
  if (!loadCallback) return;

  function applyPageInput(input) {
    let page = parseInt(input.value);
    if (isNaN(page) || page < 1) page = 1;
    if (page > parseInt(input.max)) page = input.max;

    const url = new URL(window.location);
    url.searchParams.set("page", page);
    loadCallback(url.toString());
    history.pushState({}, "", url);
  }

  // Handle Enter key
  document.addEventListener("keydown", e => {
    const target = e.target;
    if (
      (target.classList.contains("ajax-page-input") || target.classList.contains("page-input")) &&
      e.key === "Enter" &&
      (!wrapperSelector || target.closest(wrapperSelector))
    ) {
      e.preventDefault();
      applyPageInput(target);
    }
  });

  // Handle Blur (when leaving field)
  document.addEventListener("blur", e => {
    const target = e.target;
    if (
      (target.classList.contains("ajax-page-input") || target.classList.contains("page-input")) &&
      (!wrapperSelector || target.closest(wrapperSelector))
    ) {
      applyPageInput(target);
    }
  }, true);
}

// ---- Scroll to wrapper after reload ----
// wrapperId = ID of main table/list container
// offset = distance from top (account for header/navbar height)
function scrollToWrapper(wrapperId, offset = 120) {
  const wrapper = document.getElementById(wrapperId);
  if (wrapper) {
    const elementPosition = wrapper.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo({ top: elementPosition - offset, behavior: "smooth" });
  }
}
