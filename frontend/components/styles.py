"""
Centralized custom CSS for the AI Expense Analyzer.
Minimalist beige & white theme with custom hand-drawn icons and smooth
transitions throughout. Import and call inject_custom_css() once, from
app.py, before any page renders.
"""

import streamlit as st

CUSTOM_CSS = """
<style>

/* =========================================================
   PALETTE
   Background:   #FAF6EF (warm white)
   Surface:      #FFFFFF
   Beige:        #F1E9DA / #EDE3CF
   Sidebar:      #3F372B (deep espresso-brown, warm not cold)
   Accent:       #A9865A (warm tan/caramel)
   Text:         #3F372B (dark warm brown)
   Muted text:   #8A7F6E
   ========================================================= */

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

h1, h2, h3, .stButton > button, .stFormSubmitButton > button {
    font-family: 'Poppins', sans-serif;
}

/* ---------- Global fade-in on every rerun ---------- */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.main .block-container {
    animation: fadeSlideIn 0.45s ease-out;
    padding-top: 2rem;
}

/* ---------- Background ---------- */
.stApp {
    background-color: #FAF6EF;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background-color: #3F372B;
    border-right: 1px solid #2E2820;
}

section[data-testid="stSidebar"] * {
    color: #F1E9DA !important;
}

section[data-testid="stSidebar"] h1 {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

section[data-testid="stSidebar"] .stCaption {
    color: #B8AC94 !important;
    font-size: 0.85rem;
}

section[data-testid="stSidebar"] hr {
    border-color: #55493A;
    margin: 1rem 0 1.2rem 0;
}

/* ---------- Custom sidebar navigation (built on st.radio) ---------- */

/* Hide the built-in radio circle indicator entirely */
section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child {
    display: none;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    padding: 0.7rem 0.9rem;
    border-radius: 12px;
    cursor: pointer;
    transition: background-color 0.25s ease, transform 0.2s ease, padding-left 0.25s ease;
    background-color: transparent;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
    background-color: rgba(241, 233, 218, 0.10);
    transform: translateX(3px);
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
    background-color: #A9865A;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
    font-weight: 700 !important;
}

/* Icon slot - painted via CSS mask so color can transition smoothly */
section[data-testid="stSidebar"] div[data-testid="stRadio"] label::before {
    content: "";
    width: 21px;
    height: 21px;
    flex-shrink: 0;
    background-color: #D8CCB4;
    -webkit-mask-size: contain;
    mask-size: contain;
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-position: center;
    transition: background-color 0.25s ease, transform 0.3s ease;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover::before {
    transform: scale(1.15) rotate(-4deg);
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked)::before {
    background-color: #FFFFFF;
    transform: scale(1.1);
}

/* Per-item custom icons, matched by nav order:
   1 Dashboard, 2 Add Expense, 3 Upload, 4 History, 5 Report */
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:nth-of-type(1)::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Cline%20x1%3D%224%22%20y1%3D%2220%22%20x2%3D%224%22%20y2%3D%2214%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2210%22%20y1%3D%2220%22%20x2%3D%2210%22%20y2%3D%229%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2216%22%20y1%3D%2220%22%20x2%3D%2216%22%20y2%3D%2212%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2221%22%20y1%3D%2220%22%20x2%3D%2221%22%20y2%3D%225%22/%3E%0A%20%20%20%20%3Cpolyline%20points%3D%223%2C11%209%2C6%2015%2C9%2021%2C3%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%229%22%20cy%3D%226%22%20r%3D%221%22%20fill%3D%22%23000%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2221%22%20cy%3D%223%22%20r%3D%221%22%20fill%3D%22%23000%22/%3E%0A%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Cline%20x1%3D%224%22%20y1%3D%2220%22%20x2%3D%224%22%20y2%3D%2214%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2210%22%20y1%3D%2220%22%20x2%3D%2210%22%20y2%3D%229%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2216%22%20y1%3D%2220%22%20x2%3D%2216%22%20y2%3D%2212%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2221%22%20y1%3D%2220%22%20x2%3D%2221%22%20y2%3D%225%22/%3E%0A%20%20%20%20%3Cpolyline%20points%3D%223%2C11%209%2C6%2015%2C9%2021%2C3%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%229%22%20cy%3D%226%22%20r%3D%221%22%20fill%3D%22%23000%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2221%22%20cy%3D%223%22%20r%3D%221%22%20fill%3D%22%23000%22/%3E%0A%3C/svg%3E");
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:nth-of-type(2)::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%229.5%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%226%22%20stroke-dasharray%3D%222.5%203%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2212%22%20y1%3D%228.5%22%20x2%3D%2212%22%20y2%3D%2215.5%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%228.5%22%20y1%3D%2212%22%20x2%3D%2215.5%22%20y2%3D%2212%22/%3E%0A%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%229.5%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%226%22%20stroke-dasharray%3D%222.5%203%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2212%22%20y1%3D%228.5%22%20x2%3D%2212%22%20y2%3D%2215.5%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%228.5%22%20y1%3D%2212%22%20x2%3D%2215.5%22%20y2%3D%2212%22/%3E%0A%3C/svg%3E");
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:nth-of-type(3)::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Cpath%20d%3D%22M4%2014.5%20L4%2018.5%20A1.2%201.2%200%200%200%205.2%2019.7%20L18.8%2019.7%20A1.2%201.2%200%200%200%2020%2018.5%20L20%2014.5%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2212%22%20y1%3D%2215%22%20x2%3D%2212%22%20y2%3D%223.5%22/%3E%0A%20%20%20%20%3Cpolyline%20points%3D%227%2C8.5%2012%2C3.5%2017%2C8.5%22/%3E%0A%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Cpath%20d%3D%22M4%2014.5%20L4%2018.5%20A1.2%201.2%200%200%200%205.2%2019.7%20L18.8%2019.7%20A1.2%201.2%200%200%200%2020%2018.5%20L20%2014.5%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2212%22%20y1%3D%2215%22%20x2%3D%2212%22%20y2%3D%223.5%22/%3E%0A%20%20%20%20%3Cpolyline%20points%3D%227%2C8.5%2012%2C3.5%2017%2C8.5%22/%3E%0A%3C/svg%3E");
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:nth-of-type(4)::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2212.5%22%20cy%3D%2213.5%22%20r%3D%227.7%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2212.5%22%20y1%3D%2213.5%22%20x2%3D%2212.5%22%20y2%3D%229.3%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2212.5%22%20y1%3D%2213.5%22%20x2%3D%2215.3%22%20y2%3D%2214.8%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M7%206.3%20A7.7%207.7%200%200%200%204.8%2010.5%22/%3E%0A%20%20%20%20%3Cpolyline%20points%3D%223.6%2C8%204.8%2C10.5%207%2C9.3%22/%3E%0A%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2212.5%22%20cy%3D%2213.5%22%20r%3D%227.7%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2212.5%22%20y1%3D%2213.5%22%20x2%3D%2212.5%22%20y2%3D%229.3%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2212.5%22%20y1%3D%2213.5%22%20x2%3D%2215.3%22%20y2%3D%2214.8%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M7%206.3%20A7.7%207.7%200%200%200%204.8%2010.5%22/%3E%0A%20%20%20%20%3Cpolyline%20points%3D%223.6%2C8%204.8%2C10.5%207%2C9.3%22/%3E%0A%3C/svg%3E");
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:nth-of-type(5)::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Cpolyline%20points%3D%223.5%2C20%203.5%2C16%208.2%2C16%208.2%2C12%2012.9%2C12%2012.9%2C7%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2212.9%22%20y1%3D%227%22%20x2%3D%2212.9%22%20y2%3D%223%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M12.9%203.3%20L19%205%20L12.9%206.7%20Z%22%20fill%3D%22%23000%22/%3E%0A%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Cpolyline%20points%3D%223.5%2C20%203.5%2C16%208.2%2C16%208.2%2C12%2012.9%2C12%2012.9%2C7%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2212.9%22%20y1%3D%227%22%20x2%3D%2212.9%22%20y2%3D%223%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M12.9%203.3%20L19%205%20L12.9%206.7%20Z%22%20fill%3D%22%23000%22/%3E%0A%3C/svg%3E");
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:nth-of-type(6)::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M4%2017%20A8%208%200%200%201%2020%2017%22/%3E%3Cline%20x1%3D%2212%22%20y1%3D%2217%22%20x2%3D%2215.5%22%20y2%3D%2210.5%22/%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%2217%22%20r%3D%221.4%22%20fill%3D%22%23000%22/%3E%3Cline%20x1%3D%224%22%20y1%3D%2217%22%20x2%3D%222.5%22%20y2%3D%2217%22/%3E%3Cline%20x1%3D%2220%22%20y1%3D%2217%22%20x2%3D%2221.5%22%20y2%3D%2217%22/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M4%2017%20A8%208%200%200%201%2020%2017%22/%3E%3Cline%20x1%3D%2212%22%20y1%3D%2217%22%20x2%3D%2215.5%22%20y2%3D%2210.5%22/%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%2217%22%20r%3D%221.4%22%20fill%3D%22%23000%22/%3E%3Cline%20x1%3D%224%22%20y1%3D%2217%22%20x2%3D%222.5%22%20y2%3D%2217%22/%3E%3Cline%20x1%3D%2220%22%20y1%3D%2217%22%20x2%3D%2221.5%22%20y2%3D%2217%22/%3E%3C/svg%3E");
}

/* App logo mark next to the sidebar title */
.app-logo-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.1rem;
}

.app-logo-icon {
    width: 30px;
    height: 30px;
    flex-shrink: 0;
    background-color: #F1E9DA;
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2032%2032%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2213%22%20cy%3D%2219%22%20r%3D%229%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M13%2015%20L13%2023%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M10.5%2021.5c0%201%201.2%201.5%202.5%201.5s2.5-.6%202.5-1.6-1.2-1.4-2.5-1.4-2.5-.5-2.5-1.5%201.2-1.5%202.5-1.5%202.5.5%202.5%201.4%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M19%209%20L19%203%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M19%205c-2.2-.6-3.6.6-3.6%202.2C17.4%208%2019%207%2019%205z%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M19%205c2.2-.6%203.6.6%203.6%202.2C20.6%208%2019%207%2019%205z%22/%3E%0A%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2032%2032%22%20fill%3D%22none%22%20stroke%3D%22%23000%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2213%22%20cy%3D%2219%22%20r%3D%229%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M13%2015%20L13%2023%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M10.5%2021.5c0%201%201.2%201.5%202.5%201.5s2.5-.6%202.5-1.6-1.2-1.4-2.5-1.4-2.5-.5-2.5-1.5%201.2-1.5%202.5-1.5%202.5.5%202.5%201.4%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M19%209%20L19%203%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M19%205c-2.2-.6-3.6.6-3.6%202.2C17.4%208%2019%207%2019%205z%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M19%205c2.2-.6%203.6.6%203.6%202.2C20.6%208%2019%207%2019%205z%22/%3E%0A%3C/svg%3E");
    -webkit-mask-size: contain;
    mask-size: contain;
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    animation: fadeSlideIn 0.6s ease-out;
}

/* ---------- Headings ---------- */
h1, h2, h3, h4, h5, h6 {
    color: #3F372B !important;
}

h1 {
    font-weight: 700;
    padding-bottom: 0.2rem;
}

h2, h3 {
    font-weight: 600;
}

/* ---------- Force readable body text in the main area, regardless
   of OS/browser dark-mode preference (config.toml sets the real
   theme; this is a belt-and-suspenders backstop) ---------- */
.main p, .main span, .main label, .main div[data-testid="stMarkdownContainer"] {
    color: #3F372B;
}

.main .stCaption, .main small {
    color: #8A7F6E !important;
}

/* ---------- Alerts: force dark, readable text against each pastel
   background (info/success/warning/error) ---------- */
div[data-testid="stAlert"] {
    border-radius: 14px;
    animation: fadeSlideIn 0.35s ease-out;
}

div[data-testid="stAlert"] p,
div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] {
    color: #2E281F !important;
    font-weight: 500;
}

/* ---------- Metric cards ---------- */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #EDE3CF;
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 2px 10px rgba(63, 55, 43, 0.05);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(63, 55, 43, 0.10);
}

div[data-testid="stMetricLabel"] {
    font-weight: 600;
    color: #8A7F6E;
}

div[data-testid="stMetricValue"] {
    color: #3F372B;
}

/* ---------- Buttons ---------- */
.stButton > button, .stFormSubmitButton > button {
    background-color: #A9865A;
    color: #FFFFFF;
    border-radius: 10px;
    border: none;
    padding: 0.55rem 1.3rem;
    font-weight: 600;
    transition: background-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
    box-shadow: 0 1px 4px rgba(169, 134, 90, 0.25);
}

.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: #8F6F47;
    color: #FFFFFF;
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(169, 134, 90, 0.35);
}

.stButton > button:active, .stFormSubmitButton > button:active {
    transform: translateY(0);
}

/* ---------- Inputs ---------- */
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] {
    border-radius: 10px !important;
    border-color: #E4D9C2 !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #A9865A !important;
    box-shadow: 0 0 0 2px rgba(169, 134, 90, 0.15) !important;
}

/* ---------- Dataframes / tables ---------- */
div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #EDE3CF;
}

/* ---------- Dividers ---------- */
hr {
    margin: 1.5rem 0;
    border-color: #EDE3CF;
}

/* ---------- File uploader ---------- */
section[data-testid="stFileUploaderDropzone"] {
    border-radius: 14px;
    border: 2px dashed #D8C9A8;
    background-color: #FBF8F2;
    transition: border-color 0.25s ease, background-color 0.25s ease;
}

section[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #A9865A;
    background-color: #F5EEE0;
}

/* ---------- Plotly charts container ---------- */
div[data-testid="stPlotlyChart"] {
    background-color: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #EDE3CF;
    padding: 0.5rem;
    box-shadow: 0 2px 10px rgba(63, 55, 43, 0.05);
    transition: box-shadow 0.25s ease;
}

div[data-testid="stPlotlyChart"]:hover {
    box-shadow: 0 8px 18px rgba(63, 55, 43, 0.08);
}

/* ---------- Budget utilization bars ---------- */
.budget-bar-track {
    width: 100%;
    height: 10px;
    background-color: #EDE3CF;
    border-radius: 999px;
    overflow: hidden;
    margin: 0.3rem 0 0.1rem 0;
}

.budget-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.budget-bar-fill.on-track {
    background-color: #8B9A6C;
}

.budget-bar-fill.near-limit {
    background-color: #C99A4B;
}

.budget-bar-fill.over-budget {
    background-color: #B5533C;
}

/* ---------- Responsive tweak ---------- */
@media (max-width: 640px) {
    div[data-testid="stMetric"] {
        padding: 0.8rem 0.9rem;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
        padding: 0.55rem 0.7rem;
    }
}

</style>
"""


def inject_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_logo_row(title: str = "AI Expense Analyzer"):
    """Renders the custom icon mark next to the sidebar title."""
    st.markdown(
        f'''<div class="app-logo-row">
            <div class="app-logo-icon"></div>
            <span style="font-family:'Poppins',sans-serif; font-weight:700; font-size:1.25rem; color:#F1E9DA;">{title}</span>
        </div>''',
        unsafe_allow_html=True,
    )
