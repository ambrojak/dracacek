import os
from pathlib import Path
from jinja2 import Template

# Directory with your txt files and output HTML folder
SRC_DIR = "src-texts"
OUTPUT_DIR = "html-files"
CSS_FILE_BASE = "../styles/style.css"

def get_css_file_for_path(relative_path):
    depth = len(relative_path.parts) - 1  # Calculate how deep the file is in the structure
    return "../" * depth + CSS_FILE_BASE



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
    <h1>Sezení {{ title }} </h1>
    <div class="content">
        <p>{{ content }}</p>
    </div>
    <div class="navigation">
        <a href="{% if prev_file %}{{ prev_file }}{% endif %}">Previous</a>
        <a href="index.html">Index</a>
        <a href="{% if next_file %}{{ next_file }}{% endif %}">Next</a>
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
    <h1>{{ title }}</h1>
    <ul>
        {% for file in files %}
        <li><a href="{{ file.link }}">{{ file.title }}</a></li>
        {% endfor %}
    </ul>
    {% if parent_index %}<a class="backlink" href="{{ parent_index }}">Back to parent index</a>{% endif %}
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
    html_files = {}

    for txt_file in txt_files:
        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read().replace('\n','<br>')

        title = txt_file.stem
        relative_path = txt_file.relative_to(SRC_DIR)
        output_dir = Path(OUTPUT_DIR) / relative_path.parent
        os.makedirs(output_dir, exist_ok=True)

        prev_file = None
        next_file = None
        siblings = sorted((Path(SRC_DIR) / relative_path.parent).glob("*.txt"))
        for i, sibling in enumerate(siblings):
            if sibling == txt_file:
                if i > 0:
                    prev_file = siblings[i-1].with_suffix(".html").name
                if i < len(siblings) - 1:
                    next_file = siblings[i+1].with_suffix(".html").name
                break

        output_file = output_dir / f"{title}.html"
        html_files[relative_path] = output_file.relative_to(OUTPUT_DIR)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(HTML_TEMPLATE.render(
                title=title,
                content=content,
                css_file=get_css_file_for_path(relative_path),
                prev_file=prev_file,
                next_file=next_file,
            ))

    return html_files

# Generate index.html
def generate_indexes(html_files):
    indexes = {}

    for relative_path, html_file in html_files.items():
        subdir = relative_path.parent
        if subdir not in indexes:
            indexes[subdir] = []
        indexes[subdir].append(html_file)

    # Generate subfolder indexes
    for subdir, files in indexes.items():
        output_dir = Path(OUTPUT_DIR) / subdir
        os.makedirs(output_dir, exist_ok=True)

        index_file = output_dir / "index.html"
        parent_index = "../index.html" if subdir != Path() else None

        with open(index_file, "w", encoding="utf-8") as f:
            f.write(INDEX_TEMPLATE.render(
                title=f"Index of {subdir}" if subdir != Path() else "Top Index",
                files=[{"link": file.name, "title": file.stem} for file in sorted(files)],
                parent_index=parent_index,
                css_file=get_css_file_for_path(relative_path),
            ))

    # Generate top-level index with links to subfolder indexes only
    top_index_file = Path(OUTPUT_DIR) / "index.html"
    subfolder_links = [{
        "link": f"{subdir}/index.html",
        "title": subdir.name
    } for subdir in indexes.keys() if subdir != Path()]

    with open(top_index_file, "w", encoding="utf-8") as f:
        f.write(INDEX_TEMPLATE.render(
            title="Naše dračáky",
            files=subfolder_links,
            parent_index=None,
            css_file=CSS_FILE_BASE,
        ))

# Main script execution
if __name__ == "__main__":
    html_files = convert_txt_to_html()
    generate_indexes(html_files)
    print("Conversion complete. HTML files are in the 'html-files' folder.")
