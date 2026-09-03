# What Broke at 2 AM 🚨

*(A required artifact for the Razorpay AI Buildathon 2026)*

## The Incident
**Time:** 2:14 AM IST, September 1st, 2026.
**Alert:** PagerDuty went off. `CRITICAL: Frontend UI completely crashed on Vite HMR update.`

## The Investigation
I was integrating Tailwind CSS v4 and the new `framer-motion` animations to pivot our UI from a generic "dark mode AI tool" to a clean, enterprise-grade Razorpay-style dashboard.

To make the UI perfectly polished, I needed to hide the default browser scrollbars while keeping scroll functionality intact. 
I opened my terminal and confidently ran a one-liner to append a custom CSS utility class:
```powershell
echo ".scrollbar-hide::-webkit-scrollbar { display: none; }" >> src\index.css
```

Immediately, the Vite dev server crashed with a horrifying, cryptic error:
`[plugin:@tailwindcss/vite:generate:serve] Invalid declaration: \` \``

## The Root Cause
It turns out, Windows PowerShell's default `echo` (which is an alias for `Write-Output`) appends text using **UTF-16LE** encoding. 

Our original `index.css` file was standard **UTF-8**. 

By blindly piping text into the file using PowerShell, I had inadvertently created a Franken-file: half UTF-8, half UTF-16. When the Vite Tailwind parser read the file, it hit the byte-order mark and essentially saw garbage invisible characters (hence the `Invalid declaration: ' '`).

## The Fix
I had to completely delete the corrupted `index.css` file and regenerate it purely in UTF-8 using a Python script/file-writer tool instead of native Windows shell operators. 

## The Lesson
When building cross-platform (especially on Windows), never trust shell piping (`>>`) for critical text files. Always use robust programmatic file writers (`open(file, encoding='utf-8')`) or standard text editors. It cost me 30 minutes of sleep, but the scrollbar is finally hidden!

## The Follow-Up Audit

After the UI incident was closed, a security review found several issues that could have caused a different kind of 2 AM page:

- The operator API key was being sent to the browser through `VITE_ADMIN_API_KEY`. The frontend no longer ships that secret. Dashboard and fixed demo routes are public, while agent and contract management routes remain protected by `ADMIN_API_KEY`.
- Agent API keys are no longer included in normal agent list or detail responses. The key is returned only when an agent is created.
- Merchant constraints are enforced by the deterministic policy gate. Blocklisted merchants are blocked, while merchants outside an explicit allowlist go to review.
- Assessment requests now require an idempotency key. A unique `(agent_id, idempotency_key)` constraint prevents duplicate assessment and Razorpay order processing.
- Database SQL logging is controlled by `DEBUG`, and demo seeding is disabled unless debugging is explicitly enabled. For local development, the ignored `.env` sets `DEBUG=true` so the Simulator's reset button works.
- CORS is restricted to the local frontend origins, assessment list requests are capped, and `/health` provides a simple service check.

The follow-up fixes were verified with:

```text
Fresh virtual environment: requirements.txt installed successfully
Test tooling: pytest and pytest-asyncio
10 passed
Frontend production build passed
Python compilation passed
git diff --check passed
```

The lesson is broader than the original encoding mistake: security controls must be checked at every boundary, including the browser bundle, demo-only routes, database constraints, and failure paths around payment order creation.
