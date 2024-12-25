import os
from pathlib import Path
from jinja2 import Template

# Directory with your txt files and output HTML folder
SRC_DIR = "src-texts"
OUTPUT_DIR = "html-files"
CSS_FILE = "style.css"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Jinja2 template for HTML files
HTML_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="{{ css_file }}">
</head>
<body>
    <div class="content">
        <pre>{{ content }}</pre>
    </div>
    <div class="navigation">
        {% if prev_file %}<a href="{{ prev_file }}">Previous</a>{% endif %}
        {% if next_file %}<a href="{{ next_file }}">Next</a>{% endif %}
        <a href="index.html">Index</a>
    </div>
</body>
</html>
""")

# Jinja2 template for index.html
INDEX_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index</title>
    <link rel="stylesheet" href="{{ css_file }}">
</head>
<body>
    <h1>Index of Files</h1>
    <ul>
        {% for file in files %}
        <li><a href="{{ file.link }}">{{ file.title }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
""")

# Function to get all txt files with paths
def get_txt_files(src_dir):
    txt_files = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(Path(root) / file)
    return sorted(txt_files)

# Convert txt files to HTML
def convert_txt_to_html():
    txt_files = get_txt_files(SRC_DIR)
    html_files = []

    for i, txt_file in enumerate(txt_files):
        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read()

        title = txt_file.stem
        prev_file = f"{txt_files[i-1].stem}.html" if i > 0 else None
        next_file = f"{txt_files[i+1].stem}.html" if i < len(txt_files) - 1 else None
        
        output_file = Path(OUTPUT_DIR) / f"{title}.html"
        html_files.append(output_file.name)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.render(
                title=title,
                content=content,
                css_file=CSS_FILE,
                prev_file=prev_file,
                next_file=next_file,
            ))

    return html_files

# Generate index.html
def generate_index(html_files):
    files = [{"link": file, "title": file.replace(".html", "")} for file in html_files]

    with open(Path(OUTPUT_DIR) / "index.html", "w", encoding="utf-8") as f:
        f.write(INDEX_TEMPLATE.render(files=files, css_file=CSS_FILE))

# Main script execution
if __name__ == "__main__":
    html_files = convert_txt_to_html()
    generate_index(html_files)
    print("Conversion complete. HTML files are in the 'html-files' folder.")
