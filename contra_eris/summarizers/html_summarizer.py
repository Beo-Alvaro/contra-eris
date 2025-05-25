"""
HTML summarizer for Contra Eris
"""

from typing import Dict, Any
from bs4 import BeautifulSoup, Tag

def summarize_html_ast(soup: BeautifulSoup, filename: str) -> Dict:
    """Extract summary information from HTML parsed by BeautifulSoup"""
    summary = {
        "file": filename, 
        "elements": [],
        "scripts": [], 
        "styles": [],
        "imports": []
    }
    
    if not soup:
        return summary
        
    # Extract page title
    title = soup.find('title')
    if title:
        summary["title"] = title.text.strip()
    
    # Extract metadata
    meta_tags = soup.find_all('meta')
    summary["meta"] = [
        {"name": tag.get('name', tag.get('property', '')), "content": tag.get('content', '')}
        for tag in meta_tags if tag.get('name') or tag.get('property')
    ]
    
    # Extract external imports (CSS, JS)
    # CSS imports
    css_links = soup.find_all('link', rel='stylesheet')
    for link in css_links:
        if link.get('href'):
            summary["imports"].append(link['href'])
    
    # JS imports
    script_tags = soup.find_all('script', src=True)
    for script in script_tags:
        if script.get('src'):
            summary["imports"].append(script['src'])
    
    # Extract inline scripts
    inline_scripts = soup.find_all('script', src=False)
    for i, script in enumerate(inline_scripts):
        if script.string:
            summary["scripts"].append({
                "id": f"inline_script_{i+1}",
                "content": script.string.strip() if len(script.string.strip()) < 100 else f"{script.string.strip()[:100]}...",
            })
    
    # Extract inline styles
    style_tags = soup.find_all('style')
    for i, style in enumerate(style_tags):
        if style.string:
            summary["styles"].append({
                "id": f"inline_style_{i+1}",
                "content": style.string.strip() if len(style.string.strip()) < 100 else f"{style.string.strip()[:100]}...",
            })
    
    # Extract major elements for structure understanding
    for tag_name in ['div', 'section', 'main', 'header', 'footer', 'nav']:
        elements = soup.find_all(tag_name, id=True)
        for el in elements:
            summary["elements"].append({
                "type": tag_name,
                "id": el.get('id', ''),
                "class": ' '.join(el.get('class', [])) if el.get('class') else ''
            })
    
    # Extract forms
    forms = soup.find_all('form')
    for i, form in enumerate(forms):
        form_info = {
            "id": form.get('id', f"form_{i+1}"),
            "action": form.get('action', ''),
            "method": form.get('method', 'get'),
            "inputs": []
        }
        
        for input_tag in form.find_all(['input', 'textarea', 'select']):
            form_info["inputs"].append({
                "type": input_tag.name if input_tag.name != 'input' else input_tag.get('type', 'text'),
                "name": input_tag.get('name', ''),
                "id": input_tag.get('id', '')
            })
            
        summary["elements"].append(form_info)
        
    return summary 