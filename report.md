# NeroEd Project Report

## Overview

NeroEd is a document-driven study assistant built as a two-part web application:

- A FastAPI backend that extracts text from uploaded documents, chunks and embeds the content, retrieves relevant passages with hybrid search, reranks the best matches, and serves multiple AI-powered study tools through Ollama.
- A Next.js frontend that provides a polished learning interface with document upload, chat, summaries, flashcards, quizzes, notes, and formula extraction.

The project’s purpose is to turn a student’s uploaded material into an interactive academic workspace. Instead of behaving like a generic chatbot, the system is designed to answer only from the uploaded document, generate study assets from the same source, and keep the user inside one focused learning flow.

## Core Purpose

The project is built to support study and revision. Its main goals are:

- Let a user upload a PDF, DOCX, or TXT file.
- Convert that document into searchable chunks.
- Answer questions using only the uploaded material.
- Produce summaries, flashcards, quizzes, notes, and formula extractions from the same document.
- Present those tools inside a structured tabbed UI that feels more like a learning management system than a simple chat interface.

The conversation history shows that the project evolved from a basic document chat into a more complete academic assistant. The current implementation reflects that broader vision.

## High-Level Architecture

The system is split into two main layers.

### Backend Layer

The backend lives in the `backend/` folder and is responsible for:

- File ingestion and text extraction.
- Chunking document text into manageable segments.
- Generating embeddings with Ollama.
- Hybrid retrieval using semantic similarity and BM25 keyword scoring.
- Reranking retrieved chunks with a cross-encoder model.
- Generating chat responses, summaries, flashcards, quizzes, notes, and formulas.
- Managing sessions in memory.

### Frontend Layer

The frontend lives in the `frontend/` folder and is responsible for:

- Uploading source documents.
- Displaying chat, summaries, flashcards, quiz workflows, notes, and formulas.
- Streaming assistant responses over SSE.
- Rendering Markdown and math with KaTeX.
- Managing the user interface state for each study mode.

### Supporting Configuration

The project also includes:

- `.vscode/tasks.json` for running backend and frontend dev servers.
- `backend/requirements.txt` for Python dependencies.
- `frontend/package.json` for Node dependencies and scripts.
- `frontend/next.config.js`, `frontend/eslint.config.mjs`, `frontend/postcss.config.mjs`, and `frontend/tsconfig.json` for app configuration.

## Backend Architecture

### `backend/main.py`

This is the central FastAPI application. It defines the API endpoints and orchestrates the rest of the backend modules.

Important responsibilities:

- Sets CORS rules to allow local frontend development ports from `3000` through `3005` on both `localhost` and `127.0.0.1`.
- Declares request models for chat, summary, quiz, and notes workflows.
- Handles uploads and turns uploaded files into session-backed document data.
- Runs retrieval and reranking for chat responses.
- Exposes endpoints for all study features.
- Checks Ollama availability with a `/health` route.

The `/chat` endpoint is the most important runtime path. It now uses a two-stage retrieval flow:

1. Hybrid retrieval gets a larger candidate set from the uploaded document.
2. The reranker reorders those candidates and keeps the best matches for the prompt.

The endpoint then builds a system prompt with strict language rules, source-only constraints, and response formatting rules. It streams the final response as SSE chunks back to the frontend.

### `backend/extractor.py`

This module is the document ingestion layer.

It supports three file types:

- PDF via PyMuPDF (`fitz`).
- DOCX via `python-docx`.
- TXT via standard UTF-8 decoding.

After extraction, the text is split into overlapping character-based chunks. The chunking logic uses a configurable chunk size and overlap so that nearby context is preserved between segments.

This is important because the retrieval system works best when the document is broken into small, semantically coherent passages instead of one huge blob.

### `backend/session_manager.py`

This module stores runtime state in a simple in-memory dictionary keyed by UUID session IDs.

Each session stores:

- The original document text.
- Chunks generated from that text.
- Chunk embeddings.
- Chat history.

The session manager provides helpers to create sessions, fetch sessions, append messages, get recent history, and delete sessions.

This design is simple and fast, but it is ephemeral. Sessions disappear when the backend process restarts.

### `backend/ollama_client.py`

This module contains the model-facing logic.

Its responsibilities are:

- Generate embeddings with Ollama.
- Compute cosine similarity.
- Combine semantic similarity and BM25 into a hybrid retrieval score.
- Lazy-load a reranker model using `CrossEncoder`.
- Stream chat completions from Ollama.
- Run non-streaming chat calls for summaries and structured generators.
- Generate flashcards, quizzes, notes, and formulas using carefully engineered prompts.

#### Retrieval Logic

The retrieval pipeline is deliberately layered:

- `embed()` sends text to Ollama’s embedding endpoint.
- `retrieve()` compares the query embedding to chunk embeddings and mixes that score with BM25 keyword relevance.
- `rerank()` then applies a cross-encoder reranker (`BAAI/bge-reranker-base`) to the top candidates.

This gives the system a stronger relevance pipeline than raw vector search alone.

#### Generation Functions

The module also provides specialized content generation functions:

- `summarize()` produces a structured academic summary.
- `generate_flashcards()` returns JSON flashcards.
- `generate_quiz()` returns JSON quiz questions.
- `generate_notes()` returns notes in multiple formats such as bullet, cheat sheet, Cornell, or timeline.
- `extract_formulas()` returns structured formula objects with LaTeX and variable explanations.

The prompts are highly constrained and are designed to make the model output machine-consumable JSON or structured study content.

## Frontend Architecture

### `frontend/app/page.tsx`

This is the main application page and the bulk of the UI logic.

The page is a client component and uses React state heavily to manage the study workflow.

Key UI responsibilities:

- Upload and track the current source document.
- Show Ollama health status.
- Send chat messages and receive streamed responses.
- Render summaries and chat messages.
- Generate and browse flashcards.
- Build and submit quizzes.
- Generate notes in different formats.
- Extract and render formulas using KaTeX.

#### Main State Model

The page keeps separate state for:

- The active session and uploaded file name.
- Chat messages and stream state.
- Summary loading.
- Flashcard generation and navigation.
- Quiz questions, answers, difficulty, and submission state.
- Notes format and generated notes text.
- Formula results.
- Active tab selection.

This separation makes it possible to switch between study modes without collapsing the whole UI into one undifferentiated chat screen.

#### Streaming Chat Logic

The chat UI uses `fetch()` with a readable stream and parses Server-Sent Event payloads manually.

The implementation buffers partial chunks before splitting on newline boundaries, which avoids message duplication and malformed JSON parsing when data arrives in fragmented network pieces.

The frontend appends streaming tokens to the last assistant message and later attaches citations once the stream finishes.

#### Tabbed LMS Interface

The interface is organized into five tabs:

- Chat
- Flashcards
- Quiz
- Notes
- Formulas

This tab structure is one of the most important product-level design decisions in the project. It turns the app into a focused study workspace instead of a single-purpose chatbot.

#### Flashcard UI

Flashcards are displayed with a 3D flip interaction. The current implementation uses explicit perspective, `transformStyle: preserve-3d`, and `backfaceVisibility` handling to keep the front and back faces visually correct.

#### Quiz UI

The quiz tab supports:

- Difficulty selection.
- Multiple-choice questions.
- True/false questions.
- Short-answer questions.
- Answer submission and explanation display.

#### Notes UI

The notes tab can generate different styles of study notes:

- Bullet notes.
- Cheat sheets.
- Cornell notes.
- Timelines.

Users can copy the notes or download them as a `.txt` file.

#### Formula UI

The formulas tab extracts formulas and renders them in LaTeX using `remark-math` and `rehype-katex`, with KaTeX styling loaded globally.

### `frontend/app/layout.tsx`

This file defines the root layout and metadata for the app.

It loads the DM Sans and Sora fonts from Google, sets the HTML language to English, and applies the global font classes to the document structure.

### `frontend/app/globals.css`

This file currently provides the global Tailwind import, theme variables, and basic body styling.

The styling layer in `page.tsx` does most of the visual work, while `globals.css` acts as a minimal foundation.

## User Flow

The typical flow through the app is:

1. The user opens the frontend at port `3000`.
2. The user uploads a PDF, DOCX, or TXT file.
3. The backend extracts the text and creates chunks.
4. The backend embeds each chunk and stores the session in memory.
5. The user can then ask questions or switch to other study tabs.
6. Chat requests retrieve relevant chunks, rerank them, and stream a response grounded in the uploaded document.
7. Other tabs call dedicated backend endpoints to build flashcards, quizzes, notes, or formula lists.

This flow keeps the uploaded document as the source of truth for all downstream study content.

## Logic and Design Principles

### Grounded Answers

The chat system is explicitly constrained to the uploaded excerpts. The prompt instructs the model to avoid hallucination and to answer only from the retrieved document context.

### Hybrid Search Plus Reranking

The retrieval path combines multiple ranking stages:

- Embedding-based semantic similarity.
- BM25 keyword matching.
- Cross-encoder reranking.

This layered approach improves precision when the user asks about a specific fact, formula, or term.

### Structured Study Artifacts

The backend does not only chat. It also generates study artifacts that are easier to review than free-form responses:

- Flashcards for recall.
- Quizzes for self-testing.
- Notes for structured revision.
- Formulas for technical or quantitative material.

### Language Adaptation

The chat prompt includes language rules so the assistant responds in Arabic, French, or English depending on the user’s question. This is part of the project’s academic accessibility logic.

### UI as a Learning Workspace

The frontend is intentionally arranged like a study dashboard:

- Sticky sidebar for document and summary actions.
- Main workspace for the active study mode.
- Tabs for different content generation modes.
- Background branding and polished typography for a more intentional product feel.

## Content Inventory

The codebase contains the following meaningful content and assets:

- Backend Python modules for extraction, session management, and model interaction.
- Frontend Next.js app code for the full interface.
- Ollama-based study generation prompts.
- KaTeX and markdown rendering support.
- Public assets including `NeroEd.webp` and Next.js default icons.
- Project documentation in `README.md`, `frontend/README.md`, `frontend/CLAUDE.md`, and `frontend/AGENTS.md`.

The `frontend/README.md` and root `README.md` still describe the base Next.js and setup workflow, while the actual app now goes well beyond the default scaffold.

## Configuration and Dependencies

### Backend Dependencies

The backend currently depends on:

- `fastapi`
- `uvicorn`
- `httpx`
- `PyMuPDF`
- `python-docx`
- `python-multipart`
- `numpy`
- `rank_bm25`
- `sentence-transformers`

These packages support web serving, file uploads, extraction, numerical scoring, and reranking.

### Frontend Dependencies

The frontend uses:

- `next`
- `react`
- `react-dom`
- `react-markdown`
- `remark-math`
- `rehype-katex`
- `katex`

Development tooling includes TypeScript, ESLint, and Tailwind CSS.

### Runtime Configuration

The Next.js config sets `NEXT_PUBLIC_API_URL` to `http://localhost:8000`, which keeps the frontend pointed at the local FastAPI backend during development.

The VS Code tasks file provides shell tasks to run the backend and frontend dev servers with `cmd` syntax.

## Current Implementation Notes

- The backend uses in-memory sessions rather than a database.
- The frontend expects the backend to be available locally on port `8000`.
- Ollama must be running locally for embeddings and generation.
- Chat replies are streamed rather than returned in one block.
- The app supports multiple file types but not arbitrary binary uploads.
- The formula tab depends on structured JSON returned by the backend.

## Summary

NeroEd is currently a full-stack study assistant that turns uploaded documents into an interactive, multi-tool learning environment. The backend extracts and indexes source material, retrieves and reranks relevant context, and delegates generation to Ollama. The frontend wraps those capabilities in a polished tabbed interface for chatting, summarizing, drilling flashcards, taking quizzes, writing notes, and extracting formulas.

The project’s core logic is built around one principle: every useful answer or study artifact should stay grounded in the uploaded document.