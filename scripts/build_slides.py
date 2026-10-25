#!/usr/bin/env python3
"""
Generator for AegisMed Academic Defense Presentation
Single-file HTML with embedded CSS, JS, navigation, and inline editor.
Follows 1920x1080 fixed 16:9 stage requirements of frontend-slides.
"""

import os

HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AegisMed — Academic FYP Defense Presentation</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        /* ===========================================
           FIXED 16:9 STAGE MANDATORY BASE STYLES
           =========================================== */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html, body {
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #020617;
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #F8FAFC;
            -webkit-font-smoothing: antialiased;
        }
        .deck-viewport {
            position: fixed;
            inset: 0;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #020617;
        }
        .deck-stage {
            position: absolute;
            left: 0;
            top: 0;
            width: 1920px;
            height: 1080px;
            overflow: hidden;
            transform-origin: 0 0;
            background: radial-gradient(circle at 85% 15%, rgba(13, 148, 136, 0.15) 0%, transparent 45%),
                        radial-gradient(circle at 15% 85%, rgba(6, 182, 212, 0.12) 0%, transparent 40%),
                        #040914;
        }

        /* Ambient Technical Elements */
        .ambient-grid {
            position: absolute;
            inset: 0;
            background-image: linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px);
            background-size: 60px 60px;
            pointer-events: none;
        }
        .ambient-orb {
            position: absolute;
            width: 600px;
            height: 600px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(20, 184, 166, 0.12) 0%, transparent 70%);
            filter: blur(60px);
            pointer-events: none;
        }
        .orb-tr { top: -100px; right: -100px; }
        .orb-bl { bottom: -150px; left: -100px; }

        /* Slide Structure */
        .slide {
            position: absolute;
            inset: 0;
            width: 1920px;
            height: 1080px;
            padding: 60px 96px 80px 96px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            visibility: hidden;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.4s ease, visibility 0.4s ease;
        }
        .slide.active {
            visibility: visible;
            opacity: 1;
            pointer-events: auto;
            z-index: 10;
        }

        /* Slide Header Chrome */
        .slide-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(148, 163, 184, 0.12);
            padding-bottom: 20px;
            position: relative;
            z-index: 20;
        }
        .header-brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .brand-badge {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(20, 184, 166, 0.35);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #2DD4BF;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .brand-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #2DD4BF;
            box-shadow: 0 0 8px #2DD4BF;
        }
        .header-category {
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            font-weight: 500;
            color: #38BDF8;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .slide-number-tag {
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: #64748B;
            letter-spacing: 0.08em;
        }

        /* Main Slide Body */
        .slide-body {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 30px 0;
            position: relative;
            z-index: 20;
        }
        .section-kicker {
            font-family: 'JetBrains Mono', monospace;
            font-size: 15px;
            font-weight: 600;
            color: #2DD4BF;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }
        .slide-title {
            font-size: 52px;
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: -0.02em;
            color: #F8FAFC;
            margin-bottom: 12px;
        }
        .slide-title span {
            background: linear-gradient(135deg, #2DD4BF 0%, #38BDF8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .slide-subtitle {
            font-size: 22px;
            line-height: 1.45;
            color: #94A3B8;
            max-width: 1400px;
            margin-bottom: 32px;
        }

        /* Grid Layouts */
        .grid-2col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 36px;
            align-items: center;
        }
        .grid-3col {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 28px;
        }
        .grid-4col {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 24px;
        }
        .grid-split-60-40 {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 36px;
            align-items: center;
        }
        .grid-split-45-55 {
            display: grid;
            grid-template-columns: 0.85fr 1.15fr;
            gap: 36px;
            align-items: center;
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 18px;
            padding: 28px;
            backdrop-filter: blur(14px);
            position: relative;
            overflow: hidden;
        }
        .glass-card.highlight {
            border-color: rgba(45, 212, 191, 0.4);
            box-shadow: 0 0 30px rgba(20, 184, 166, 0.12);
        }
        .card-accent-top {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #2DD4BF, #38BDF8);
        }
        .card-num {
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            font-weight: 700;
            color: #2DD4BF;
            margin-bottom: 10px;
            letter-spacing: 0.1em;
        }
        .card-title {
            font-size: 22px;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 12px;
            line-height: 1.3;
        }
        .card-text {
            font-size: 16px;
            line-height: 1.6;
            color: #94A3B8;
        }
        .card-badge {
            display: inline-block;
            margin-top: 14px;
            background: rgba(13, 148, 136, 0.2);
            border: 1px solid rgba(45, 212, 191, 0.3);
            color: #2DD4BF;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
        }

        /* Image Display Frame */
        .image-frame {
            position: relative;
            background: #020617;
            border: 1px solid rgba(45, 212, 191, 0.35);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5), 0 0 35px rgba(20, 184, 166, 0.15);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .image-frame img {
            width: 100%;
            height: auto;
            max-height: 520px;
            object-fit: contain;
            display: block;
        }
        .image-caption {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, rgba(2, 6, 23, 0.95), rgba(2, 6, 23, 0.6) 80%, transparent);
            padding: 12px 20px;
            font-size: 13px;
            font-family: 'JetBrains Mono', monospace;
            color: #94A3B8;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .caption-tag {
            color: #2DD4BF;
            font-weight: 600;
        }

        /* Data Tables */
        .spec-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 15px;
            margin-top: 10px;
        }
        .spec-table th {
            text-align: left;
            padding: 12px 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 600;
            color: #38BDF8;
            border-bottom: 2px solid rgba(56, 189, 248, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .spec-table td {
            padding: 12px 16px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
            color: #E2E8F0;
        }
        .spec-table tr:hover td {
            background: rgba(255, 255, 255, 0.02);
        }
        .val-highlight {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            color: #2DD4BF;
        }

        /* Flow Badges & Metrics */
        .metric-pill {
            display: flex;
            flex-direction: column;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 14px;
            padding: 18px 22px;
        }
        .metric-num {
            font-family: 'JetBrains Mono', monospace;
            font-size: 32px;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 4px;
        }
        .metric-desc {
            font-size: 13px;
            color: #94A3B8;
            font-weight: 500;
        }

        /* Slide Footer */
        .slide-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(148, 163, 184, 0.12);
            padding-top: 16px;
            margin-bottom: 8px;
            position: relative;
            z-index: 20;
        }
        .footer-left {
            font-size: 14px;
            color: #64748B;
        }
        .footer-left strong {
            color: #94A3B8;
        }
        .footer-right {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #475569;
        }

        /* Deck Navigation Controls */
        .deck-controls {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: 16px;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.2);
            backdrop-filter: blur(20px);
            padding: 8px 18px;
            border-radius: 9999px;
            z-index: 1000;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        }
        .ctrl-btn {
            background: transparent;
            border: none;
            color: #94A3B8;
            font-size: 18px;
            cursor: pointer;
            padding: 6px 10px;
            border-radius: 6px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .ctrl-btn:hover {
            color: #2DD4BF;
            background: rgba(45, 212, 191, 0.1);
        }
        .counter-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            font-weight: 600;
            color: #E2E8F0;
            min-width: 90px;
            text-align: center;
        }
        .progress-bar-wrap {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: rgba(255, 255, 255, 0.05);
            z-index: 1000;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #0D9488, #2DD4BF, #38BDF8);
            width: 7.14%;
            transition: width 0.3s ease;
        }

        /* Inline Editor Elements */
        .edit-hotzone {
            position: fixed;
            top: 0;
            left: 0;
            width: 120px;
            height: 80px;
            z-index: 2000;
        }
        .edit-toggle {
            position: fixed;
            top: 20px;
            left: 20px;
            background: #0F172A;
            border: 1px solid #2DD4BF;
            color: #2DD4BF;
            padding: 8px 14px;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            cursor: pointer;
            z-index: 2001;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.25s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        }
        .edit-toggle.show,
        .edit-toggle.active {
            opacity: 1;
            pointer-events: auto;
        }
        [contenteditable="true"] {
            outline: 2px dashed rgba(45, 212, 191, 0.6) !important;
            outline-offset: 4px;
            background: rgba(45, 212, 191, 0.05);
            border-radius: 4px;
        }

        /* Reveal animations */
        .reveal {
            opacity: 0;
            transform: translateY(16px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
        .slide.active .reveal {
            opacity: 1;
            transform: translateY(0);
        }
        .slide.active .reveal:nth-child(1) { transition-delay: 0.1s; }
        .slide.active .reveal:nth-child(2) { transition-delay: 0.2s; }
        .slide.active .reveal:nth-child(3) { transition-delay: 0.3s; }
        .slide.active .reveal:nth-child(4) { transition-delay: 0.4s; }
    </style>
</head>
<body>
    <div class="progress-bar-wrap">
        <div class="progress-bar" id="progressBar"></div>
    </div>

    <div class="edit-hotzone"></div>
    <button class="edit-toggle" id="editToggle" title="Edit mode (Press E)">✏️ Edit Deck</button>

    <div class="deck-viewport">
        <main class="deck-stage" id="deckStage">
            <div class="ambient-grid"></div>
            <div class="ambient-orb orb-tr"></div>
            <div class="ambient-orb orb-bl"></div>
"""

HTML_FOOT = """
        </main>
    </div>

    <div class="deck-controls">
        <button class="ctrl-btn" id="prevBtn" title="Previous Slide (Left Arrow)">◀</button>
        <div class="counter-badge" id="slideCounter">01 / 14</div>
        <button class="ctrl-btn" id="nextBtn" title="Next Slide (Right Arrow, Space)">▶</button>
    </div>

    <script>
        class SlidePresentation {
            constructor() {
                this.slides = Array.from(document.querySelectorAll('.slide'));
                this.current = 0;
                this.stage = document.getElementById('deckStage');
                this.counter = document.getElementById('slideCounter');
                this.progressBar = document.getElementById('progressBar');
                this.initScale();
                this.initNavigation();
                this.initEditor();
                this.goTo(0);
            }

            initScale() {
                const scale = () => {
                    const factor = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
                    const x = (window.innerWidth - 1920 * factor) / 2;
                    const y = (window.innerHeight - 1080 * factor) / 2;
                    this.stage.style.transform = `translate(${x}px, ${y}px) scale(${factor})`;
                };
                scale();
                window.addEventListener('resize', scale);
            }

            goTo(idx) {
                if (idx < 0) idx = 0;
                if (idx >= this.slides.length) idx = this.slides.length - 1;
                this.current = idx;
                this.slides.forEach((s, i) => {
                    s.classList.toggle('active', i === this.current);
                });
                const curStr = String(this.current + 1).padStart(2, '0');
                const totStr = String(this.slides.length).padStart(2, '0');
                this.counter.textContent = `${curStr} / ${totStr}`;
                const pct = ((this.current + 1) / this.slides.length) * 100;
                this.progressBar.style.width = `${pct}%`;
            }

            next() { this.goTo(this.current + 1); }
            prev() { this.goTo(this.current - 1); }

            initNavigation() {
                document.getElementById('nextBtn').addEventListener('click', () => this.next());
                document.getElementById('prevBtn').addEventListener('click', () => this.prev());

                window.addEventListener('keydown', (e) => {
                    if (e.target.getAttribute('contenteditable') === 'true') return;
                    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
                        e.preventDefault();
                        this.next();
                    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
                        e.preventDefault();
                        this.prev();
                    } else if (e.key === 'Home') {
                        e.preventDefault();
                        this.goTo(0);
                    } else if (e.key === 'End') {
                        e.preventDefault();
                        this.goTo(this.slides.length - 1);
                    }
                });

                // Touch swipe
                let touchStartX = 0;
                window.addEventListener('touchstart', (e) => {
                    touchStartX = e.touches[0].clientX;
                }, { passive: true });
                window.addEventListener('touchend', (e) => {
                    const diff = e.changedTouches[0].clientX - touchStartX;
                    if (diff < -50) this.next();
                    else if (diff > 50) this.prev();
                }, { passive: true });
            }

            initEditor() {
                const hotzone = document.querySelector('.edit-hotzone');
                const toggle = document.getElementById('editToggle');
                let isEditing = false;
                let hideTimer = null;

                hotzone.addEventListener('mouseenter', () => {
                    clearTimeout(hideTimer);
                    toggle.classList.add('show');
                });
                hotzone.addEventListener('mouseleave', () => {
                    hideTimer = setTimeout(() => {
                        if (!isEditing) toggle.classList.remove('show');
                    }, 400);
                });
                toggle.addEventListener('mouseenter', () => clearTimeout(hideTimer));
                toggle.addEventListener('mouseleave', () => {
                    hideTimer = setTimeout(() => {
                        if (!isEditing) toggle.classList.remove('show');
                    }, 400);
                });

                const toggleEdit = () => {
                    isEditing = !isEditing;
                    toggle.classList.toggle('active', isEditing);
                    toggle.textContent = isEditing ? '💾 Save Changes' : '✏️ Edit Deck';
                    const editables = document.querySelectorAll('.slide h1, .slide h2, .slide h3, .slide p, .slide .card-title, .slide .card-text, .slide td, .slide th, .slide .metric-num, .slide .metric-desc');
                    editables.forEach(el => {
                        el.setAttribute('contenteditable', isEditing ? 'true' : 'false');
                    });
                    if (!isEditing) {
                        localStorage.setItem('aegismed_slides_html', document.getElementById('deckStage').innerHTML);
                    }
                };

                toggle.addEventListener('click', toggleEdit);
                hotzone.addEventListener('click', toggleEdit);
                window.addEventListener('keydown', (e) => {
                    if ((e.key === 'e' || e.key === 'E') && e.target.getAttribute('contenteditable') !== 'true') {
                        e.preventDefault();
                        toggleEdit();
                    }
                });

                // Restore saved content if present
                const saved = localStorage.getItem('aegismed_slides_html');
                if (saved) {
                    // Stage content can be restored if user previously edited
                }
            }
        }

        window.addEventListener('DOMContentLoaded', () => {
            new SlidePresentation();
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    from slide_content import SLIDES
    import sys

    target_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aegismed-defense-presentation.html"))
    assembled_html = HTML_HEAD + "\n".join(SLIDES) + HTML_FOOT
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(assembled_html)
    print(f"Successfully generated {len(SLIDES)} slides at {target_path}")


