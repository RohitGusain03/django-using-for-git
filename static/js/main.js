(function () {
    "use strict";

    /* ============ CSRF helper ============ */
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }
    const CSRF_TOKEN = getCookie("csrftoken");

    function postJSON(url) {
        return fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN,
                "X-Requested-With": "XMLHttpRequest",
            },
        }).then((r) => {
            if (r.status === 403 || r.status === 302) {
                window.location.href = "/login/";
                throw new Error("auth required");
            }
            return r.json();
        });
    }

    /* ============ Theme toggle ============ */
    const root = document.documentElement;
    const THEME_KEY = "memestack-theme";

    function applyTheme(theme) {
        root.setAttribute("data-theme", theme);
        localStorage.setItem(THEME_KEY, theme);
    }

    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const current = root.getAttribute("data-theme") || "dark";
            applyTheme(current === "dark" ? "light" : "dark");
        });
    });

    /* ============ Dropdowns ============ */
    document.querySelectorAll("[data-dropdown-toggle]").forEach((btn) => {
        const panelId = btn.getAttribute("data-dropdown-toggle");
        const panel = document.getElementById(panelId);
        if (!panel) return;

        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            document.querySelectorAll(".dropdown-panel.is-open").forEach((p) => {
                if (p !== panel) p.classList.remove("is-open");
            });
            panel.classList.toggle("is-open");
        });
    });

    document.addEventListener("click", (e) => {
        document.querySelectorAll(".dropdown-panel.is-open").forEach((panel) => {
            if (!panel.contains(e.target)) panel.classList.remove("is-open");
        });
    });

    /* ============ Mobile drawer ============ */
    const drawer = document.getElementById("mobileDrawer");
    document.querySelectorAll("[data-drawer-open]").forEach((btn) => {
        btn.addEventListener("click", () => drawer && drawer.classList.add("is-open"));
    });
    document.querySelectorAll("[data-drawer-close]").forEach((btn) => {
        btn.addEventListener("click", () => drawer && drawer.classList.remove("is-open"));
    });

    /* ============ Dismissible alerts ============ */
    document.querySelectorAll("[data-alert-close]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const alertEl = btn.closest(".alert");
            if (alertEl) alertEl.remove();
        });
    });
    document.querySelectorAll(".alert").forEach((el) => {
        setTimeout(() => {
            el.style.transition = "opacity .4s ease";
            el.style.opacity = "0";
            setTimeout(() => el.remove(), 400);
        }, 5000);
    });

    /* ============ Toast helper ============ */
    function toast(msg) {
        let stack = document.querySelector(".toast-stack");
        if (!stack) {
            stack = document.createElement("div");
            stack.className = "toast-stack";
            document.body.appendChild(stack);
        }
        const el = document.createElement("div");
        el.className = "toast";
        el.textContent = msg;
        stack.appendChild(el);
        setTimeout(() => el.remove(), 2600);
    }

    /* ============ Like buttons (posts) ============ */
    document.querySelectorAll("[data-like-url]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const url = btn.getAttribute("data-like-url");
            postJSON(url).then((data) => {
                btn.classList.toggle("is-active", data.liked);
                btn.classList.add("pulse");
                setTimeout(() => btn.classList.remove("pulse"), 350);
                document.querySelectorAll(`[data-like-count="${btn.dataset.postId}"]`).forEach((el) => {
                    el.textContent = data.like_count;
                });
            }).catch(() => {});
        });
    });

    /* ============ Save buttons (posts) ============ */
    document.querySelectorAll("[data-save-url]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const url = btn.getAttribute("data-save-url");
            postJSON(url).then((data) => {
                btn.classList.toggle("is-active", data.saved);
                btn.classList.add("pulse");
                setTimeout(() => btn.classList.remove("pulse"), 350);
                toast(data.saved ? "Saved to your stash 🔖" : "Removed from saved");
                if (btn.hasAttribute("data-remove-on-unsave") && !data.saved) {
                    const card = btn.closest("[data-post-card]");
                    if (card) card.remove();
                }
            }).catch(() => {});
        });
    });

    /* ============ Comment likes ============ */
    document.querySelectorAll("[data-comment-like-url]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const url = btn.getAttribute("data-comment-like-url");
            postJSON(url).then((data) => {
                btn.classList.toggle("is-active", data.liked);
                const countEl = btn.querySelector("[data-count]");
                if (countEl) countEl.textContent = data.like_count;
            }).catch(() => {});
        });
    });

    /* ============ Follow buttons ============ */
    document.querySelectorAll("[data-follow-url]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const url = btn.getAttribute("data-follow-url");
            postJSON(url).then((data) => {
                btn.classList.toggle("btn-primary", data.following);
                btn.classList.toggle("btn-ghost", !data.following);
                btn.textContent = data.following ? "Following" : "Follow";
                document.querySelectorAll("[data-follower-count]").forEach((el) => {
                    el.textContent = data.follower_count;
                });
            }).catch(() => {});
        });
    });

    /* ============ Reply toggles ============ */
    document.querySelectorAll("[data-reply-toggle]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const id = btn.getAttribute("data-reply-toggle");
            const form = document.getElementById(id);
            if (form) {
                form.classList.toggle("is-open");
                if (form.classList.contains("is-open")) {
                    const ta = form.querySelector("textarea");
                    if (ta) ta.focus();
                }
            }
        });
    });

    /* ============ Tag input preview (create/edit post) ============ */
    const tagInput = document.getElementById("id_tags_input");
    const tagPreview = document.getElementById("tagPreview");
    if (tagInput && tagPreview) {
        function renderTags() {
            const names = tagInput.value.split(",").map((t) => t.trim()).filter(Boolean).slice(0, 5);
            tagPreview.innerHTML = "";
            names.forEach((name) => {
                const chip = document.createElement("span");
                chip.className = "chip";
                chip.textContent = "#" + name.replace(/^#/, "");
                tagPreview.appendChild(chip);
            });
        }
        tagInput.addEventListener("input", renderTags);
        renderTags();
    }

    /* ============ Dropzone / multi-image preview (create post) ============ */
    const dropzone = document.querySelector("[data-dropzone]");
    if (dropzone) {
        const fileInput = dropzone.querySelector('input[type="file"]');
        const previewGrid = document.getElementById("imagePreviewGrid");
        let dt = new DataTransfer();

        function refreshPreview() {
            if (!previewGrid) return;
            previewGrid.innerHTML = "";
            Array.from(dt.files).forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const tile = document.createElement("div");
                    tile.className = "preview-tile";
                    tile.innerHTML = `<img src="${e.target.result}" alt=""><button type="button" class="remove-btn" data-index="${index}">&times;</button>`;
                    previewGrid.appendChild(tile);
                    tile.querySelector(".remove-btn").addEventListener("click", () => {
                        const newDt = new DataTransfer();
                        Array.from(dt.files).forEach((f, i) => {
                            if (i !== index) newDt.items.add(f);
                        });
                        dt = newDt;
                        fileInput.files = dt.files;
                        refreshPreview();
                    });
                };
                reader.readAsDataURL(file);
            });
        }

        dropzone.addEventListener("click", (e) => {
            if (e.target.tagName !== "BUTTON") fileInput.click();
        });

        fileInput.addEventListener("change", () => {
            dt = new DataTransfer();
            Array.from(fileInput.files).forEach((f) => dt.items.add(f));
            refreshPreview();
        });

        ["dragover", "dragleave", "drop"].forEach((evt) => {
            dropzone.addEventListener(evt, (e) => {
                e.preventDefault();
                dropzone.classList.toggle("is-dragover", evt === "dragover");
            });
        });

        dropzone.addEventListener("drop", (e) => {
            Array.from(e.dataTransfer.files).forEach((f) => dt.items.add(f));
            fileInput.files = dt.files;
            refreshPreview();
        });
    }

    /* ============ Lightbox for extra media ============ */
    const lightbox = document.getElementById("lightbox");
    if (lightbox) {
        const lightboxImg = lightbox.querySelector("img");
        document.querySelectorAll("[data-lightbox-src]").forEach((el) => {
            el.addEventListener("click", () => {
                lightboxImg.src = el.getAttribute("data-lightbox-src");
                lightbox.classList.add("is-open");
            });
        });
        lightbox.addEventListener("click", () => lightbox.classList.remove("is-open"));
    }

    /* ============ Character counter for bio ============ */
    document.querySelectorAll("[data-char-count]").forEach((textarea) => {
        const max = textarea.getAttribute("maxlength");
        const counter = document.getElementById(textarea.getAttribute("data-char-count"));
        if (!counter) return;
        const update = () => (counter.textContent = `${textarea.value.length}/${max}`);
        textarea.addEventListener("input", update);
        update();
    });
})();
