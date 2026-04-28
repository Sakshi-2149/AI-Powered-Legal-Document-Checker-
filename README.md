
**📄 Legal Document Checker V2**

AI-Powered Legal Clause Risk Detection & Document Verification
---------------------------------------------------------------------------------------------------------------------------------
🧩 Overview


Legal Document Checker V2 is an AI-driven web application designed to help users understand complex legal documents before signing them.

It automatically detects whether a file is a legal document, extracts clauses, and uses a Large Language Model to generate simple explanations and risk assessments for each clause.

This project addresses a critical real-world problem:

People often sign contracts without fully understanding them due to complex legal language, high legal consultation costs, and time constraints.

---------------------------------------------------------------------------------------------------------------------------------
**🎯 Objectives**

Simplify legal language using AI
Detect and highlight risky clauses in contracts
Prevent users from signing harmful agreements
Provide a free alternative to expensive legal consultation

---------------------------------------------------------------------------------------------------------------------------------
**✨ Key Features**
---------------------------------------------------------------------------------------------------------------------------------
**🔍 Intelligent Document Detection (V2.0 Enhancement)**

Automatically identifies whether an uploaded file is a legal document
Hybrid detection approach:
Keyword-based filtering (30+ legal terms)
AI-based classification for ambiguous cases
Instantly rejects non-legal files (e.g., resumes, essays)

---------------------------------------------------------------------------------------------------------------------------------
**📑 Clause Extraction & Processing**

Extracts text from PDF documents using pdfplumber
Splits content into clauses using regex-based segmentation
Uses multiple fallback strategies for robust clause detection

---------------------------------------------------------------------------------------------------------------------------------
**🤖 AI-Based Clause Analysis**

Powered by LLaMA 3.1 (8B) via Groq API
Converts complex legal clauses into plain English explanations
Performs context-aware risk evaluation

---------------------------------------------------------------------------------------------------------------------------------
**⚠️ Risk Classification System**

Each clause is labeled as:

🔴 RISKY

🟢 SAFE

Provides:
Explanation
Risk reasoning
Suggested questions for negotiation

---------------------------------------------------------------------------------------------------------------------------------
**🚫 Smart Rejection System**

Rejects non-legal documents such as:

Resumes / CVs
Essays and articles
Study materials
Invoices and bills
