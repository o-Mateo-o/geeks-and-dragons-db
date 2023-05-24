import logging
from pathlib import Path
import jinja2


def _fill_template(template_str: str) -> str:
    """Fill the template using Jinja templates. 

    Args:
        template_str (str): String report template html file.

    Returns:
        str: String result report html file.
    """
    environment = jinja2.Environment()
    template = environment.from_string(template_str)
    style = Path("assets", "static", "template", "style.css").read_text()
    context = {"name": "Siema", "style": style}
    return template.render(context)

def generate() -> str:
    """Read the template report file, fill the placeholders and save the results
    in the new report file.
    """
    template = Path("assets", "static", "template", "report_template.html").read_text()
    out_path = Path("reports", "report.html")

    try:
        result = _fill_template(template)
        with out_path.open("w", encoding="utf-8") as f:
            f.write(result)
        logging.info("The new report has been generated.")
    except FileNotFoundError:
        logging.error("Some assets were missing. The report could not be generated.")
