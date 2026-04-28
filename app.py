# ============================================================
#  LEGAL DOCUMENT CHECKER — VERSION 2
#  NEW FEATURE: Auto-detects if uploaded file is legal or not
#  Using GROQ API — 100% FREE
# ============================================================

# ── PART 1: IMPORT LIBRARIES ─────────────────────────────────
import streamlit as st
import pdfplumber
from groq import Groq
from dotenv import load_dotenv
import os
import time
import re

# ── PART 2: LOAD YOUR FREE API KEY ───────────────────────────
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── PART 3: PAGE SETTINGS ────────────────────────────────────
st.set_page_config(
    page_title="Legal Document Checker",
    page_icon="📄",
    layout="wide"
)

# ══════════════════════════════════════════════════════════════
# NEW FUNCTION — DETECT IF DOCUMENT IS LEGAL OR NOT
# Reads first 1500 characters and checks:
#   Step 1 — keyword count (instant, no API)
#   Step 2 — if unclear, asks AI to confirm
# ══════════════════════════════════════════════════════════════
def is_legal_document(text):
    legal_keywords = [
        "agreement", "contract", "party", "parties", "clause",
        "terms", "conditions", "hereby", "whereas", "hereinafter",
        "obligation", "liability", "termination", "confidential",
        "indemnify", "arbitration", "jurisdiction", "witness whereof",
        "nda", "non-disclosure", "employment", "signed", "executed",
        "governed by", "intellectual property", "warranty", "breach",
        "consideration", "covenants", "representations", "obligations"
    ]

    text_lower = text.lower()
    keyword_hits = sum(1 for kw in legal_keywords if kw in text_lower)

    # 4+ legal keywords → definitely legal, no AI needed
    if keyword_hits >= 4:
        return True, keyword_hits

    # 1-3 keywords → ask AI to confirm
    if keyword_hits >= 1:
        sample = text[:1500]
        prompt = f"""Read this document text.
Is this a legal document (contract, agreement, NDA, terms, employment letter)?
Reply ONLY: LEGAL or NOTLEGAL

Text:
{sample}"""
        try:
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10
            )
            ans = resp.choices[0].message.content.strip().upper()
            return ("LEGAL" in ans and "NOT" not in ans), keyword_hits
        except:
            return keyword_hits >= 2, keyword_hits

    # 0 keywords → not legal
    return False, keyword_hits


# ── DETECT DOCUMENT TYPE ─────────────────────────────────────
def detect_document_type(text):
    t = text.lower()
    types = []
    if any(w in t for w in ["non-disclosure", "nda", "confidential information"]):
        types.append("NDA / Confidentiality Agreement")
    if any(w in t for w in ["employment", "employee", "employer", "salary", "job"]):
        types.append("Employment Contract")
    if any(w in t for w in ["rent", "tenant", "landlord", "lease", "premises"]):
        types.append("Rental / Lease Agreement")
    if any(w in t for w in ["freelance", "deliverable", "milestone", "scope of work"]):
        types.append("Freelance / Service Contract")
    if any(w in t for w in ["terms of service", "terms and conditions", "user agreement"]):
        types.append("Terms of Service")
    if any(w in t for w in ["partnership", "joint venture", "profit sharing"]):
        types.append("Partnership Agreement")
    if any(w in t for w in ["loan", "borrower", "lender", "repayment", "interest rate"]):
        types.append("Loan Agreement")
    if any(w in t for w in ["purchase", "sale", "buyer", "seller", "vendor"]):
        types.append("Purchase / Sale Agreement")
    return types if types else ["General Legal Contract"]


# ── AI FUNCTION 1 — EXPLAIN A CLAUSE ─────────────────────────
def explain_clause(clause_text):
    clause_text = clause_text[:800]
    prompt = f"""You are a helpful legal assistant for non-lawyers.
Read this contract clause and explain it in very simple English.
Also say clearly if it is RISKY or SAFE for the person signing.

Clause:
{clause_text}

Reply in EXACTLY this format (3 lines only):
Simple explanation: (explain in 1-2 sentences a 10 year old understands)
Risk level: RISKY or SAFE
Why: (one short sentence reason)"""
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Simple explanation: Could not analyse.\nRisk level: SAFE\nWhy: AI error — {str(e)[:60]}"


# ── AI FUNCTION 2 — GET QUESTIONS ────────────────────────────
def get_questions(clause_text):
    clause_text = clause_text[:800]
    prompt = f"""You are a legal advisor.
Give exactly 2 short questions a non-lawyer should ask before signing this clause.

Clause:
{clause_text}

Reply:
1. (question one)
2. (question two)"""
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return resp.choices[0].message.content
    except:
        return "1. Can you explain this clause simply?\n2. Can this clause be changed or removed?"


# ── PDF SPLITTING ─────────────────────────────────────────────
def split_into_clauses(full_text):
    clauses = re.split(r'\n{2,}', full_text)
    clauses = [c.strip() for c in clauses if len(c.strip()) > 40]
    if len(clauses) <= 2:
        sentences = re.split(r'(?<=[.!?])\s+', full_text)
        clauses = [' '.join(sentences[i:i+3]).strip()
                   for i in range(0, len(sentences), 3)
                   if len(' '.join(sentences[i:i+3]).strip()) > 40]
    if len(clauses) <= 2:
        clauses = re.split(r'\n(?=\d+[\.\)])', full_text)
        clauses = [c.strip() for c in clauses if len(c.strip()) > 40]
    if len(clauses) <= 2:
        words, chunk, clauses = full_text.split(), [], []
        for w in words:
            chunk.append(w)
            if len(' '.join(chunk)) >= 400:
                clauses.append(' '.join(chunk)); chunk = []
        if chunk: clauses.append(' '.join(chunk))
        clauses = [c for c in clauses if len(c.strip()) > 40]
    return clauses


# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.header("How this app works")
    st.write("**Step 1:** Upload any PDF file")
    st.write("**Step 2:** App checks if it is a legal document")
    st.write("**Step 3:** If legal → clause analysis begins")
    st.write("**Step 4:** Read results:")
    st.error("Red = RISKY clause")
    st.success("Green = SAFE clause")
    st.warning("Yellow = Questions to ask")
    st.divider()
    st.write("**Accepted documents:**")
    st.caption("Contracts • NDAs • Employment letters • Rent agreements • Terms of Service • Freelance contracts")
    st.divider()
    st.write("**Rejected documents:**")
    st.caption("Essays • Articles • Textbooks • Stories • Resumes • Research papers")
    st.divider()
    st.info("Powered by Groq + LLaMA 3.1 — Free Forever")
    st.caption("For information only. Always consult a real lawyer.")


# ── MAIN PAGE ─────────────────────────────────────────────────
st.title("📄 Legal Document Checker")
st.caption(
    "Upload any PDF — the app first checks if it is a legal document, "
    "then explains every clause in plain English and flags what is risky."
)

# 3-step visual explanation
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Step 1 — Upload**")
    st.caption("Upload any PDF file. Legal or not — we check it first.")
with c2:
    st.markdown("**Step 2 — Detection**")
    st.caption("AI checks if it is a contract, NDA, agreement etc.")
with c3:
    st.markdown("**Step 3 — Analysis**")
    st.caption("If legal → explains every clause. Red = risky, Green = safe.")

st.divider()


# ── FILE UPLOAD ───────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload your PDF file here (legal or non-legal — we will check!)",
    type="pdf",
    help="Supports PDF files up to 10MB."
)


# ── MAIN PROCESSING ───────────────────────────────────────────
if uploaded_file is not None:

    # READ PDF
    with st.spinner("Reading your document..."):
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    full_text += t + "\n"

    if full_text.strip() == "":
        st.error("This PDF has no readable text. It may be a scanned image. Try a different PDF.")
        st.stop()

    # ══════════════════════════════════════════════════════════
    # DETECTION STAGE — NEW FEATURE
    # ══════════════════════════════════════════════════════════
    st.subheader("🔍 Document Detection")

    with st.spinner("Checking if this is a legal document..."):
        time.sleep(0.4)
        legal, kw_count = is_legal_document(full_text)

    if not legal:
        # ── NOT A LEGAL DOCUMENT ──────────────────────────────
        st.error("❌  This is NOT a legal document. Cannot proceed with analysis.")

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### Why was this rejected?")
            st.write(
                "This app only analyses **legal contracts and agreements**. "
                "The uploaded document does not contain enough legal language "
                "to be classified as a legal document."
            )
            st.markdown("**Legal keywords found:** " + str(kw_count) + " (minimum 4 needed)")

        with col2:
            st.markdown("### Please upload one of these:")
            st.markdown("""
- 📋 Employment contract / job offer letter
- 🤝 Non-Disclosure Agreement (NDA)
- 🏠 Rent or lease agreement
- 💼 Freelance or service contract
- 📜 Terms of Service document
- 🤝 Partnership deed
- 🏦 Loan agreement
- 📦 Purchase / sale agreement
            """)

        st.divider()
        with st.expander("See what was found in your document"):
            st.write(f"Legal keywords detected: **{kw_count} out of 30 checked**")
            st.write("**Preview of your document (first 400 characters):**")
            st.code(full_text[:400])

        st.stop()  # Stop here — do not run analysis on non-legal file

    # ── LEGAL DOCUMENT CONFIRMED ──────────────────────────────
    doc_types = detect_document_type(full_text)
    st.success(
        f"✅  Legal document confirmed! "
        f"Detected {kw_count} legal keywords."
    )
    st.info(f"📋  Document type: **{' • '.join(doc_types)}**")

    st.divider()

    # ══════════════════════════════════════════════════════════
    # ANALYSIS STAGE — runs only if document is legal
    # ══════════════════════════════════════════════════════════

    # Split into clauses
    clauses = split_into_clauses(full_text)
    st.success(f"Document read successfully! Found **{len(clauses)} clauses**.")

    # Quick keyword risk scan
    risky_words = [
        "unlimited liability", "indemnify", "indemnification",
        "waive", "arbitration", "non-compete", "non compete",
        "perpetual", "irrevocable", "terminate immediately",
        "sole discretion", "without notice", "personal guarantee",
        "penalty", "liquidated damages", "intellectual property assignment"
    ]
    quick_risky = sum(1 for c in clauses if any(w in c.lower() for w in risky_words))

    # Document overview
    st.subheader("Document Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Clauses", len(clauses))
    col2.metric("Possibly Risky", quick_risky)
    col3.metric("Total Words", len(full_text.split()))

    st.divider()

    # AI Analysis
    st.subheader("AI Analysis")
    st.write("Click below — AI will read and explain each clause in plain English for free.")

    if st.button("🔍 Analyse all clauses with AI", type="primary"):

        clauses_to_check = clauses[:10]
        st.info(f"Analysing {len(clauses_to_check)} clauses... please wait.")

        results = []
        for i, clause in enumerate(clauses_to_check):
            with st.spinner(f"Reading clause {i+1} of {len(clauses_to_check)}..."):
                result = explain_clause(clause)
                time.sleep(1.5)
            results.append((clause, result))

        st.divider()
        st.subheader("Results — Clause by Clause")

        risky_count = 0
        safe_count  = 0

        for i, (clause, result) in enumerate(results):
            if "RISKY" in result.upper():
                risky_count += 1
                st.error(f"⚠️  Clause {i+1} — RISKY")
                with st.expander("See original clause text"):
                    st.write(clause)
                st.info(result)
                with st.spinner("Generating questions to ask..."):
                    questions = get_questions(clause)
                    time.sleep(1.5)
                st.warning("💬 Questions to ask before signing:\n\n" + questions)
            else:
                safe_count += 1
                with st.expander(f"✅  Clause {i+1} — Safe (click to read)"):
                    st.write(clause)
                    st.success(result)
            st.divider()

        # Final summary
        st.subheader("Final Summary")
        total = len(results)
        pct   = round((risky_count / total) * 100) if total > 0 else 0

        if pct >= 50:
            st.error(f"🔴 HIGH RISK — {risky_count}/{total} clauses risky ({pct}%). Review carefully!")
        elif pct >= 20:
            st.warning(f"🟡 MEDIUM RISK — {risky_count}/{total} clauses risky ({pct}%). Ask questions first.")
        else:
            st.success(f"🟢 LOW RISK — Only {risky_count}/{total} clauses risky ({pct}%). Looks mostly safe.")

        c1, c2, c3 = st.columns(3)
        c1.metric("Clauses Checked", total)
        c2.metric("Risky Clauses",   risky_count)
        c3.metric("Safe Clauses",    safe_count)

        st.caption("Always consult a real lawyer for important contracts.")
