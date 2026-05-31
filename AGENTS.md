# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Repository layout

Three-pillar monorepo for a museum-visit booking system (movie-artist former residence theme — 谢晋故居). Each app has its own `package.json` / `requirements.txt`; there is no root-level installer.

- `backend/` — FastAPI + SQLAlchemy, SQLite by default (can swap to MySQL).
- `admin/` — Vue 3 + Element Plus + Tailwind, built with Vite. SPA served as static files.
- `miniprogram/` — Uni-app (Vue 3) targeting WeChat Mini Program.

## Common commands

Backend (`cd backend`):
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload          # dev server on :8000, OpenAPI at /docs
pytest                                  # unit tests
pytest -m integration                   # integration tests (spins up MySQL via testcontainers; needs Docker)
SKIP_TESTCONTAINERS=1 pytest            # skip the MySQL-container tests
pytest tests/test_auth.py::test_name    # single test
```

Admin (`cd admin`):
```bash
npm install
npm run dev          # Vite dev server on :5173, proxies /api & /uploads → 127.0.0.1:8000
npm run build        # vue-tsc -b && vite build
npm run check        # type-check only (vue-tsc -b)
npm run lint         # ESLint
npm run lint:fix
```

Miniprogram (`cd miniprogram`):
```bash
npm install
npm run dev:mp-weixin     # produces dist/dev/mp-weixin — import this folder in WeChat DevTools
npm run build:mp-weixin   # production build
npm run type-check
```

Stack (from repo root):
```bash
docker compose up --build -d   # backend on :8000, admin on :8080
```

## Architecture notes that span files

**Standardized API envelope.** Every backend response is `{code, message, data}`. Success goes through `api_utils.api_success(...)`. Errors go through `ApiError` (4xx domain errors) or the registered handlers in `register_exception_handlers` — `RequestValidationError` → code 1001, `HTTPException` → code 1000, unexpected → code 5000 with `trace_id`. All handlers log via the rotating file handler at `backend/logs/app.log` and propagate `X-Request-ID`. New routers should raise `ApiError`/`HTTPException` rather than returning raw error dicts.

**Schema migration on boot.** `backend/app/main.py` calls `models.Base.metadata.create_all(engine)` then `run_schema_migrations(engine)` (`db_migration.py`). The latter is a hand-rolled idempotent migrator: it ensures `audio_explanation` exists and adds any missing columns to `volunteers` via `ALTER TABLE … ADD COLUMN`. When evolving a model, add a matching `_add_column_if_missing` call there instead of writing a real migration — there is no Alembic.

**Volunteers router is mounted twice.** `main.py` does `app.include_router(volunteers.router)` and `app.include_router(volunteers.router, prefix="/api")`, so endpoints are reachable at both `/volunteers/*` and `/api/volunteers/*`. Keep them in sync; the admin frontend hits one form and the miniprogram the other.

**Auth.** JWT (HS256) issued by `/api/token`. `auth.SECRET_KEY` is currently hardcoded in `backend/app/auth.py` — set via env in any deploy. Three dependencies: `get_current_user` (required), `get_current_active_user`, `get_current_admin_user`. WeChat one-click login lives at `/api/auth/wechat/login` and uses `wechat.WeChatClient.code_2_session`; when `WECHAT_APP_ID == "wx_your_app_id"` the client returns mock values so dev works without real credentials.

**Snowflake IDs.** `models.generate_snowflake_id()` (twitter-style: 41-bit ms since 2024-01-01, 10-bit node, 12-bit seq) is the PK default for `consultation`, `consultation_versions`, and `consultation_idempotency`. Don't introduce a second ID strategy for those tables.

**CORS.** Allowed origins come from `ALLOW_ORIGINS` env (comma-separated) or fall back to a hardcoded list including `localhost:5173/5174` and the `shxiejinf.cn` domains in `main.py`.

**Admin routing & auth guard.** `admin/src/router/index.ts` puts everything under a `Dashboard` parent with child routes (`/bookings`, `/blog/manage`, `/volunteers`, `/audio-explanations/manage`, …). The router guard rejects anything other than `localStorage.username === 'admin'` — backend still enforces real role checks. Axios client in `admin/src/api/index.ts` uses baseURL `/api` (so Vite dev proxy handles routing); on 401/403 it clears token/username and redirects to `/login`.

**Miniprogram API base.** `miniprogram/src/utils/api.ts` reads `VITE_API_BASE_URL` from `.env.development` / `.env.production` (default `https://api.shxiejinf.cn`). `buildApiUrl()` and `normalizeApiAssetUrl()` are the canonical helpers — use them rather than concatenating URLs, especially for `uploads/*` asset paths which need rewriting to `${API_BASE_URL}/uploads/...`. Token is stored via `uni.setStorageSync('token', …)`; reactive auth state lives in `miniprogram/src/utils/auth.ts` (`refreshAuthState`, `ensureLoginOrRedirect`, `subscribeAuthChange`).

**Miniprogram tabBar quirk.** The bottom-tab label flips between "登录" and "我的" based on auth state — `auth.ts:applyTabBar` rewrites tab text on every state change. If you add a new tab-bar route, also add it to `tabBarRoutes` in that file or the relabel logic will skip it.

**File uploads.** Backend mounts `backend/uploads/` at `/uploads` for static serving. Docker Compose bind-mounts `./backend/uploads` and `./backend/museum.db` into the container so they survive rebuilds.

## Environment & deploy

- Production domains: `shxiejinf.cn` (admin), `api.shxiejinf.cn` (backend). Nginx terminates TLS and proxies to docker containers on `:8080` (admin) and `:8000` (backend) — see `docs/DEPLOYMENT.md` and `docs/nginx.shxiejinf.cn.conf`.
- WeChat Mini Program requires HTTPS + ICP-registered domain; dev workaround is the "不校验合法域名" checkbox in WeChat DevTools.
- Required backend env vars in prod: `DATABASE_URL`, `ALLOW_ORIGINS`, `WECHAT_APP_ID`, `WECHAT_APP_SECRET`. DB pool tuning via `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` / `DB_POOL_RECYCLE` / `DB_POOL_TIMEOUT` (only applied to non-SQLite URLs).

## Notes on existing state

- `backend/museum.db` is the live SQLite file and is no longer tracked (see commit `bac5c20`). Don't recommit it.
- `backend/test_volunteers_unit.db` exists at the repo root as well — it's an old artifact from unit tests, not the dev DB.
- `docs/` and `UIDESIGN/` hold product/design materials (Chinese); `UIDESIGN/product-pages/` is untracked WIP.
