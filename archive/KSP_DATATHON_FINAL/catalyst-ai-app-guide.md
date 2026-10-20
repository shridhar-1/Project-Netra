# Building an AI Q&A App on Zoho Catalyst (like the KSP Datathon workshop)

A step-by-step guide to build what was shown in the *"Hands-on Workshop with Catalyst"* video:
a web app where users **sign in**, then **ask questions in natural language** (English or Kannada) and get answers from:

1. **A structured database** (Catalyst Data Store queried with ZCQL, results interpreted by an LLM), and
2. **Your own documents (PDFs)** via **RAG** (Retrieval-Augmented Generation) using QuickML's knowledge base.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER (Slate)                       │
│  index.html + main.js + style.css                            │
│  • Embedded Catalyst Auth (iframe sign-in)                   │
│  • Calls your serverless function endpoints via fetch()      │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS (CORS whitelisted)
┌───────────────────────────▼─────────────────────────────────┐
│           SERVERLESS FUNCTION (Advanced I/O, Node.js)        │
│  index.js  → routes: /seed  /ask-db  /ask-rag                │
│  quickml.js → LLM + RAG API calls, system prompts            │
│  catalyst-config.json → env vars (project ID, org ID,        │
│                          LLM endpoint, RAG doc ID)           │
└───────┬───────────────────────────────┬─────────────────────┘
        │ ZCQL                          │ Connection (OAuth,
        ▼                               ▼  scope: quickml.deployment.read)
┌───────────────┐              ┌──────────────────────────────┐
│  DATA STORE   │              │        QUICK ML              │
│  Your table   │              │  • LLM serving (GLM 4.7      │
│  (your data)  │              │    Flash / vision model)     │
└───────────────┘              │  • RAG knowledge base (PDF)  │
                               └──────────────────────────────┘
```

**Flow for a DB question:** user query → function runs a ZCQL `SELECT` on your table → rows + user question + system prompt are sent to the QuickML LLM → LLM answers in the user's language → response returned to client.

**Flow for a document question:** user query → function calls the QuickML **RAG endpoint** with your uploaded document's ID → LLM answers from the document → response returned to client.

---

## 2. Prerequisites

- **Node.js** installed (the workshop used Node.js 24 runtime).
- A **Catalyst account** → sign up at https://catalyst.zoho.com
- Your dataset ready in two forms:
  - **Structured data** → CSV/JSON you can seed into a Data Store table.
  - **Documents** → PDFs for the RAG knowledge base.

---

## 3. Create the Project & Set Up the CLI

1. In the **Catalyst console**, click **Create Project** (e.g. `my-ai-app`).
2. On your machine:

```bash
npm install -g zcatalyst-cli
mkdir my-ai-app && cd my-ai-app
catalyst init
```

During `catalyst init`:
- **Select your project** (the one you created in the console).
- **Components** (use spacebar to select): `Functions` and `Slate` (frontend hosting).
  - (Alternative: **AppSail** if you'd rather deploy a Flask/Spring Boot/Go app as a Docker image.)
- **Function type:** `Advanced I/O` (gives you an Express-like HTTP handler).
- **Runtime:** Node.js (latest available, e.g. 24).
- **Entry point:** `index.js`, install dependencies → **Yes** (installs the Catalyst Node SDK).
- **Frontend:** `static` is fine for a vanilla HTML/CSS/JS client (or pick React/Vue etc.).

Resulting structure:

```
my-ai-app/
├── functions/
│   └── my_function/
│       ├── index.js            ← backend routes
│       ├── quickml.js          ← LLM + RAG helpers (you create this)
│       ├── mock-data.json      ← seed data (you create this)
│       ├── catalyst-config.json← env vars live here
│       └── package.json        ← per-function dependencies!
└── client/
    ├── index.html
    ├── main.js
    └── style.css
```

> ⚠️ **Important:** each function has its **own** `package.json`. If you add npm
> packages, add them inside `functions/<name>/package.json` and run `npm install`
> **inside that folder**.

---

## 4. Enable Authentication

In the console → **Cloud Scale → Authentication**:

1. Choose **Embedded Authentication** (an iframe sign-in widget inside your page)
   — or **Hosted** if you prefer a dedicated login page.
2. Enable **Public Signup** if you want anyone to register.
3. Optionally add **social login** (Google / Zoho / Microsoft 365 / LinkedIn / Facebook)
   by supplying that provider's Client ID & Client Secret.
4. Copy the provided **embedded auth code snippet** into your `index.html`.
   It loads the Catalyst **Web SDK**, initializes it, and handles auth tokens for you.

Client-side essentials (shape of it — copy the exact snippet from your console):

```html
<!-- in index.html -->
<script src="https://static.zohocdn.com/catalyst/sdk/js/4.x/catalystWebSDK.js"></script>
<script>
  window.catalyst.auth.signIn("login-container"); // renders embedded sign-in iframe
</script>
<div id="login-container"></div>
```

```js
// check session before showing the app
const result = await catalyst.auth.isUserAuthenticated();
if (!result) { /* show login */ } else { /* show app UI */ }

// sign out button
document.querySelector("#signout").onclick = () => catalyst.auth.signOut("/");
```

---

## 5. Create the Data Store Table

Console → **Cloud Scale → Data Store → Create New Table**.

Example from the workshop (adapt columns to YOUR dataset):

| Column          | Type | Notes            |
|-----------------|------|------------------|
| RecordNumber    | Text | mandatory        |
| Category        | Text | e.g. crime type  |
| District        | Text |                  |
| RecordDate      | Text | (or Date type)   |
| Status          | Text |                  |
| PartyA          | Text | e.g. accused     |
| PartyB          | Text | e.g. victim      |
| Description     | Text |                  |

**Scopes & Permissions** (Data Store → your table → permissions):
- Set access level: **Global / Org / User** (org- or user-level gives you easy multi-tenancy).
- For app users, start with **SELECT only**.
- ⚠️ To **seed data from the app**, temporarily grant **INSERT** too, seed, then revoke.
  (In the video the seed failed with *"no privileges to perform this action"* until
  INSERT permission was granted.)

---

## 6. Enable QuickML: LLM + RAG

Console → **QuickML**:

### 6a. LLM serving
- Catalyst provides hosted models — the workshop used **GLM 4.7 Flash** (text) and a
  vision model. Open the model page to get:
  - the **API endpoint / details**
  - **sample request & response**
  - tunable params: `temperature`, `max_tokens`, thinking mode, etc.

### 6b. RAG knowledge base
- In QuickML → **RAG**, upload your **PDF** to a knowledge base.
- Copy the **Document ID** shown after upload — you need it in your env vars.
- Use the **Try** button in the console to sanity-check answers *before* wiring code.

### 6c. Create a Connection (this is what authorizes your function to call QuickML)
Console → **Cloud Scale → Connections → Create**:
- Pick **Catalyst** as the service.
- Select the **QuickML** scope: `quickml.deployment.read` (as shown in the model's
  sample request page).
- Name it (e.g. `QuickML`), click **Create & Connect**, authorize.

Without this connection, QuickML API calls from your function will fail with an
authentication error.

---

## 7. Environment Variables

Put these in `functions/<name>/catalyst-config.json` (or set them in the console
under your function's settings):

```json
{
  "env_variables": {
    "CATALYST_PROJECT_ID": "<from console URL or API details page>",
    "CATALYST_ORG_ID": "<your org id>",
    "QUICKML_LLM_ENDPOINT": "<LLM endpoint from QuickML model page>",
    "QUICKML_RAG_ENDPOINT": "<RAG endpoint from QuickML>",
    "QUICKML_RAG_DOCUMENT_ID": "<document id of your uploaded PDF>",
    "QUICKML_CONNECTION_NAME": "QuickML"
  }
}
```

> Get the exact endpoint URLs from **your** console (QuickML → model → API details).
> Wrong project ID / org ID = endpoints won't work.

---

## 8. Backend Code

### `functions/<name>/quickml.js` — LLM + RAG helpers

```js
const https = require("https");

// Get an OAuth access token for QuickML via the Connection you created.
async function getAccessToken(catalystApp) {
  const connectorName = process.env.QUICKML_CONNECTION_NAME || "QuickML";
  const connection = catalystApp.connection({
    [connectorName]: {
      client_id: process.env.CLIENT_ID,       // auto-managed for Catalyst connections
      client_secret: process.env.CLIENT_SECRET,
      auth_url: process.env.AUTH_URL,
      refresh_url: process.env.REFRESH_URL,
      refresh_token: process.env.REFRESH_TOKEN
    }
  });
  const connector = connection.getConnector(connectorName);
  return await connector.getAccessToken();
}

// Generic JSON POST helper
function postJSON(url, token, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const req = https.request(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Zoho-oauthtoken ${token}`,
        "CATALYST-ORG": process.env.CATALYST_ORG_ID
      }
    }, res => {
      let out = "";
      res.on("data", c => (out += c));
      res.on("end", () => {
        try { resolve(JSON.parse(out)); } catch (e) { reject(new Error(out)); }
      });
    });
    req.on("error", reject);
    req.write(data);
    req.end();
  });
}

const SYSTEM_PROMPT = `You are an assistant for a records query system.
Answer ONLY from the records provided in the context.
If the answer is not in the records, say you don't have that information.
Reply in the same language the user asked in (e.g. English or Kannada).
Always include the relevant record numbers in your answer.`;

// Ask the LLM a question grounded in DB rows
async function askLLM(catalystApp, userQuestion, records) {
  const token = await getAccessToken(catalystApp);
  const body = {
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      { role: "user", content:
        `Records:\n${JSON.stringify(records, null, 2)}\n\nQuestion: ${userQuestion}` }
    ],
    temperature: 0.2,
    max_tokens: 1024
  };
  return await postJSON(process.env.QUICKML_LLM_ENDPOINT, token, body);
}

// Ask a question against the RAG knowledge base (your uploaded PDF)
async function askRAG(catalystApp, userQuestion) {
  const token = await getAccessToken(catalystApp);
  const body = {
    query: userQuestion,
    document_ids: [process.env.QUICKML_RAG_DOCUMENT_ID]
  };
  return await postJSON(process.env.QUICKML_RAG_ENDPOINT, token, body);
}

module.exports = { askLLM, askRAG };
```

> 🔎 The **exact request-body field names** for the LLM and RAG endpoints are shown on
> the QuickML model's *API details / sample request* page in your console — mirror
> those exactly. The structure above follows the standard chat-completions shape.

### `functions/<name>/index.js` — routes

```js
const express = require("express");
const catalystSDK = require("zcatalyst-sdk-node");
const { askLLM, askRAG } = require("./quickml");
const mockData = require("./mock-data.json");

const app = express();
app.use(express.json());

// 1) Seed the table with your data (needs INSERT permission — see section 5)
app.post("/seed", async (req, res) => {
  const catalystApp = catalystSDK.initialize(req);
  const table = catalystApp.datastore().table("Records"); // your table name
  let ok = 0, fail = 0, errors = [];
  for (const row of mockData) {
    try { await table.insertRow(row); ok++; }
    catch (e) { fail++; errors.push(e.message); }
  }
  res.json({ inserted: ok, failed: fail, errors });
});

// 2) Natural-language question over the structured DB
app.post("/ask-db", async (req, res) => {
  try {
    const catalystApp = catalystSDK.initialize(req);
    const { question } = req.body;

    // Fetch rows with ZCQL (add WHERE/LIMIT as your data grows!)
    const zcql = catalystApp.zcql();
    const rows = await zcql.executeZCQLQuery(
      "SELECT RecordNumber, Category, District, RecordDate, Status, Description FROM Records"
    );

    const answer = await askLLM(catalystApp, question, rows);
    res.json({ answer });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// 3) Natural-language question over the PDF knowledge base (RAG)
app.post("/ask-rag", async (req, res) => {
  try {
    const catalystApp = catalystSDK.initialize(req);
    const { question } = req.body;
    const answer = await askRAG(catalystApp, question);
    res.json({ answer });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

module.exports = app;
```

### Frontend `client/main.js` (essentials)

```js
// ❗ Use your FUNCTION's invocation URL from the console
// (Serverless → Functions → your function → Invocation URL)
const API_BASE =
  "https://<project>-<id>.development.catalystserverless.in/server/<function_name>";

async function askDB(question) {
  const r = await fetch(`${API_BASE}/ask-db`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",              // sends the Catalyst auth cookie
    body: JSON.stringify({ question })
  });
  return r.json();
}

async function askRAG(question) {
  const r = await fetch(`${API_BASE}/ask-rag`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ question })
  });
  return r.json();
}
```

---

## 9. Deploy

```bash
catalyst deploy
```

This deploys the function first, then builds & hosts the frontend on **Slate**
(you get a URL like `https://my-ai-app.onslate.in` — editable in the console).

### Fix CORS (the #1 thing people get stuck on!)

Your frontend (`*.onslate.in`) and backend function are on **different domains**:

1. Copy your **frontend URL**.
2. Console → **Cloud Scale → Authentication → Whitelisting**.
3. Add the frontend domain, **enable CORS**, save.
   (Enable iframe there too, only if you embed anything as an iframe.)

Also in the console you can bump the function's **allocated memory** (e.g. 512 MB)
under the function's settings.

---

## 10. Test Checklist

- [ ] App loads at the Slate URL, sign-in works.
- [ ] `/seed` succeeds (grant INSERT → seed → revoke INSERT).
- [ ] Rows visible in Data Store → Data View.
- [ ] DB question in **English** returns grounded answer with record numbers.
- [ ] Same question in **Kannada** returns a Kannada answer (LLMs handle this natively).
- [ ] RAG question answers from your **PDF** (test in console's "Try" first).
- [ ] No CORS errors in the browser dev console.

---

## 11. Going Beyond (to stand out in the Datathon)

- **Custom ML models:** QuickML's **pipeline builder** lets you train your own
  prediction/forecasting models (fraud/anomaly detection, hotspot forecasting) on
  your dataset — big differentiator vs. just LLM+RAG.
- **Voice pipeline:** chain QuickML's audio models:
  `audio → text transcription` → `text translation` (for multilingual) →
  `text-to-audio synthesis` for spoken responses.
- **Real chat UI:** turn the single textbox into a full conversation interface with
  history.
- **Roles & multi-tenancy:** use table permission levels (org/user) + user roles so
  different users see different data.
- **Vision model:** GLM vision model can analyze uploaded images if your use case
  needs it.

## Key Resources

- Catalyst console: https://catalyst.zoho.com
- Catalyst docs & tutorials: https://docs.catalyst.zoho.com
- The workshop's sample code was promised under the **Resources tab** on the
  Hack2skill KSP Datathon dashboard — grab it there for the exact QuickML request
  formats.
- Previous session: *"Introduction to Catalyst"* on the Hack2skill YouTube channel.
