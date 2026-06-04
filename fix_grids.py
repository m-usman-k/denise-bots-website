import os, glob

bot_templates = glob.glob('d:/Projects_Working/Denise-Bots/denise-bots-website/bots/templates/bots/*_dashboard.html')
for file in bot_templates:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace grid-template-columns inline style
    content = content.replace('class="cards-grid" style="grid-template-columns: 1fr 1fr;"', 'class="cards-grid grid-1-1"')
    
    # Replace span 2 inline style
    target = 'style="background:var(--bg-card-white); border:1px solid var(--border-default); border-radius:var(--radius-card); padding:1.75rem; grid-column: span 2;"'
    replacement = 'class="col-span-2" style="background:var(--bg-card-white); border:1px solid var(--border-default); border-radius:var(--radius-card); padding:1.75rem;"'
    content = content.replace(target, replacement)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
