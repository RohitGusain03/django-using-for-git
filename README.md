# 🐸 MemeStack

A meme-sharing community built with Django — post memes, react, comment, follow
creators, and browse a fast, tag-driven feed.

## ✨ What's new in this pass

**New features**
- Tags on posts, with a trending-tags cloud and dedicated `#tag` pages
- Sort feed by **Latest / Trending (7-day) / Top / Following**
- Follow / unfollow other users, with followers & following list pages
- Notifications (likes, comments, replies, new followers) with a bell dropdown + inbox page
- Threaded comment replies, and likes on comments
- Post view counter
- Multi-image posts (a cover image + additional gallery images) with a drag-and-drop uploader and lightbox
- AJAX like / save / follow (instant feedback, no page reloads)
- Public profile pages with Posts / Saved / Liked tabs, bio, banner, socials
- Dark mode by default, with a light-mode toggle (remembered per-browser)

**Design**
- A distinctive "sticker board" visual language: chunky borders, hard offset
  shadows, stamp-style like/save buttons — built to fit meme culture rather
  than looking like a generic dashboard
- Fully responsive: mobile drawer nav, responsive feed grid, touch-friendly controls
- New type system (Archivo Black display / Inter body / JetBrains Mono for stats)

**Fixes**
- Removed leftover debug `print()` statements
- Fixed a static-files path mismatch that would have broken CSS once deployed (`STATICFILES_DIRS` didn't match where `style.css` actually lived)
- Added `STATIC_ROOT` so `collectstatic` works for deployment
- Added upload size limits

## 🚀 Getting started

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

Then open [dedpussy003.pythonanywhere.com](https://dedpussy003.pythonanywhere.com/?utm_source=chatgpt.com)

Your existing `db.sqlite3` and uploaded media are untouched — migrations were
generated and applied against your real data with no issues.

### Creating an admin user

```bash
python manage.py createsuperuser
```

Then visit `/admin/` to manage categories, tags, posts, and notifications.

## 🗂️ Project structure

- `blog/` — posts, comments, tags, categories, notifications, the feed
- `users/` — auth, profiles, and the follow system
- `static/` — CSS (`tokens.css`, `layout.css`, `feed.css`, `post_detail.css`,
  `pages.css`) and `js/main.js` (all the AJAX/interactive behavior)
- `media/` — user-uploaded images (created automatically)

## 🔧 Notes for going further

- Swap `EMAIL_BACKEND`/`SECRET_KEY`/`DEBUG` for real values before deploying
- The dev server is fine for local use; use gunicorn/uwsgi + a real static
  file host (WhiteNoise, S3, etc.) in production
