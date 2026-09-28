"""
Reusable inline SVG icons for page headings (distinct from the
sidebar nav icons in styles.py, which are CSS masks). These are
plain color-parameterized SVG strings you can drop into st.markdown.
"""

ICONS = {
    'logo': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">\n    <circle cx="13" cy="19" r="9"/>\n    <path d="M13 15 L13 23"/>\n    <path d="M10.5 21.5c0 1 1.2 1.5 2.5 1.5s2.5-.6 2.5-1.6-1.2-1.4-2.5-1.4-2.5-.5-2.5-1.5 1.2-1.5 2.5-1.5 2.5.5 2.5 1.4"/>\n    <path d="M19 9 L19 3"/>\n    <path d="M19 5c-2.2-.6-3.6.6-3.6 2.2C17.4 8 19 7 19 5z"/>\n    <path d="M19 5c2.2-.6 3.6.6 3.6 2.2C20.6 8 19 7 19 5z"/>\n</svg>',
    'dashboard': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">\n    <line x1="4" y1="20" x2="4" y2="14"/>\n    <line x1="10" y1="20" x2="10" y2="9"/>\n    <line x1="16" y1="20" x2="16" y2="12"/>\n    <line x1="21" y1="20" x2="21" y2="5"/>\n    <polyline points="3,11 9,6 15,9 21,3"/>\n    <circle cx="9" cy="6" r="1" fill="{color}"/>\n    <circle cx="21" cy="3" r="1" fill="{color}"/>\n</svg>',
    'add_expense': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">\n    <circle cx="12" cy="12" r="9.5"/>\n    <circle cx="12" cy="12" r="6" stroke-dasharray="2.5 3"/>\n    <line x1="12" y1="8.5" x2="12" y2="15.5"/>\n    <line x1="8.5" y1="12" x2="15.5" y2="12"/>\n</svg>',
    'upload': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">\n    <path d="M4 14.5 L4 18.5 A1.2 1.2 0 0 0 5.2 19.7 L18.8 19.7 A1.2 1.2 0 0 0 20 18.5 L20 14.5"/>\n    <line x1="12" y1="15" x2="12" y2="3.5"/>\n    <polyline points="7,8.5 12,3.5 17,8.5"/>\n</svg>',
    'history': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">\n    <circle cx="12.5" cy="13.5" r="7.7"/>\n    <line x1="12.5" y1="13.5" x2="12.5" y2="9.3"/>\n    <line x1="12.5" y1="13.5" x2="15.3" y2="14.8"/>\n    <path d="M7 6.3 A7.7 7.7 0 0 0 4.8 10.5"/>\n    <polyline points="3.6,8 4.8,10.5 7,9.3"/>\n</svg>',
    'report': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">\n    <polyline points="3.5,20 3.5,16 8.2,16 8.2,12 12.9,12 12.9,7"/>\n    <line x1="12.9" y1="7" x2="12.9" y2="3"/>\n    <path d="M12.9 3.3 L19 5 L12.9 6.7 Z" fill="{color}"/>\n</svg>',
    'ai_insights': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">\n    <path d="M12 3.2 L13.6 9.6 L20 11.2 L13.6 12.8 L12 19.2 L10.4 12.8 L4 11.2 L10.4 9.6 Z" fill="{color}" fill-opacity="0.12"/>\n    <path d="M12 3.2 L13.6 9.6 L20 11.2 L13.6 12.8 L12 19.2 L10.4 12.8 L4 11.2 L10.4 9.6 Z"/>\n    <circle cx="19" cy="4.2" r="1.5" fill="{color}"/>\n</svg>',
    'budgets': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;"><path d="M4 17 A8 8 0 0 1 20 17"/><line x1="12" y1="17" x2="15.5" y2="10.5"/><circle cx="12" cy="17" r="1.4" fill="{color}"/><line x1="4" y1="17" x2="2.5" y2="17"/><line x1="20" y1="17" x2="21.5" y2="17"/></svg>',
    'forecast': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;"><polyline points="3,18 8,13.5 12.5,15.5"/><polyline points="12.5,15.5 17,8.5 20.5,4.5" stroke-dasharray="2.4 2.6"/><polyline points="17,4.5 20.5,4.5 20.5,8"/></svg>',
}


def icon_heading(name: str, text: str, color: str = "#3F372B", size: int = 26, tag: str = "h1") -> str:
    """
    Build an HTML snippet: [custom icon] Heading Text
    Pass the result to st.markdown(..., unsafe_allow_html=True).
    """
    svg = ICONS[name].format(color=color, size=size)
    font_size = {"h1": "2rem", "h2": "1.5rem", "h3": "1.25rem"}.get(tag, "1.5rem")
    return (
        f'<div style="display:flex; align-items:center; gap:0.6rem; margin:0.2rem 0 0.8rem 0;">'
        f'{svg}'
        f'<span style="font-family:\'Poppins\',sans-serif; font-weight:700; '
        f'font-size:{font_size}; color:{color};">{text}</span>'
        f'</div>'
    )
