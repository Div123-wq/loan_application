import os

frontend_dir = r"d:\my repos\loan_application\frontend"
html_files = ["index.html", "dashboard.html", "compare.html", "simulator.html", "chat.html", "auth.html"]

script_to_append = """
<!-- Google Translate Script -->
<script type="text/javascript">
function googleTranslateElementInit() {
  new google.translate.TranslateElement({
    pageLanguage: 'en',
    includedLanguages: 'en,hi,kn',
    layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
    autoDisplay: false
  }, 'google_translate_element');
}
</script>
<script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
"""

for filename in html_files:
    filepath = os.path.join(frontend_dir, filename)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add translate element to navbar
    if filename == "auth.html":
        # auth.html navbar is a bit different
        if '<div class="nav-brand"' in content and 'google_translate_element' not in content:
            content = content.replace(
                '<div class="nav-brand"',
                '<div style="display:flex; align-items:center; gap:20px; margin-left:auto;"><div id="google_translate_element"></div></div>\n    <div class="nav-brand"'
            )
    else:
        # others have <div id="navCtaArea">
        if '<div id="navCtaArea">' in content and 'google_translate_element' not in content:
            content = content.replace(
                '<div id="navCtaArea">',
                '<div style="display:flex; align-items:center; gap:16px;">\n    <div id="google_translate_element"></div>\n    <div id="navCtaArea">'
            )
            content = content.replace(
                '</nav>',
                '  </div>\n</nav>'
            )

    # Add translate script before </body>
    if 'googleTranslateElementInit' not in content:
        content = content.replace('</body>', script_to_append + '</body>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Translation widget added to all HTML files.")
