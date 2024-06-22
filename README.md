# Flask-Tjfu-Captcha 1.0.0

Implement CAPTCHA verification for Flask in a straightforward manner.

### Primary Dependencies

1. [captcha >=0.5.0](https://pypi.org/project/captcha/)
2. [cryptocode >=0.1](https://pypi.org/project/cryptocode/)
3. [Flask](https://pypi.org/project/Flask/)

### Installation

```
pip install flask-tjfu-captcha
```

### Getting Started

```python
from datetime import timedelta

from flask import Flask
from flask_tjfu_captcha import TjfuCaptcha

app = Flask(__name__)
tjfu_captcha = TjfuCaptcha(
    app,
    True
)


@app.route('/get_captcha')
def get_captcha():
    return tjfu_captcha.generate_image_captcha(
        secret_key="YOUR_SECRET_KEY",
        length=4,
        expires_in=timedelta(minutes=5),
        only_digits=True
    ).to_dict()


@app.route('/verify_captcha')
@tjfu_captcha.required_captcha(
    "YOUR_SECRET_KEY"
)
def verify_captcha():
    return "OK"


if __name__ == '__main__':
    app.run(debug=True)
```

`/get_captcha` will generate a JSON with two attributes:

- `encrypted_code`: encoded information of the generated captcha.
- `img_base64`: base64 encoded string of the captcha image.

```json
{
  "encrypted_code": "...",
  "img_base64": "..."
}
```

`/verify_captcha` uses `required_captcha` to enforce captcha verification before executing requests
within `verify_captcha`. To pass captcha verification, the client must provide two headers: `Tjfu-Captcha-Code`
containing the captcha code visible in the captcha image requested, and `Tjfu-Captcha-Encrypted-Code` containing the
encoded information mentioned above.

```http request
GET http://0.0.0.0:5000/verify_captcha
Tjfu-Captcha-Encrypted-Code: <encrypted_code>
Tjfu-Captcha-Code: <code>
```

### Skipping Captcha Verification in Debug Mode

To bypass captcha verification during testing, you can use the `Tjfu-Captcha-Debugging-Ignore` header with any value,
and TjfuCaptcha must be in Debug mode.

```python
from flask import Flask
from flask_tjfu_captcha import TjfuCaptcha

app = Flask(__name__)
tjfu_captcha = TjfuCaptcha(
    app,
    True  # Must be in Debug mode
)
```

```http request
GET http://0.0.0.0:5000/verify_captcha
Tjfu-Captcha-Debugging-Ignore: <you can put any value>
```

### Customization

You can customize headers for captcha verification
using `TJFU_CAPTCHA_ENCRYPTED_CODE_HEADER_KEY`, `TJFU_CAPTCHA_CAPTCHA_CODE_HEADER_KEY`, `TJFU_CAPTCHA_DEBUGGING_IGNORE_HEADER_KEY`,
and `TJFU_CAPTCHA_FONTS` to adjust captcha image fonts.

```python
from flask import Flask

app = Flask(__name__)

app.config['TJFU_CAPTCHA_FONTS'] = "['your_font_path', 'your_other_font_path']"
# Change Tjfu-Captcha-Encrypted-Code header to Request-ID
app.config['TJFU_CAPTCHA_ENCRYPTED_CODE_HEADER_KEY'] = 'Request-ID'
# Change Tjfu-Captcha-Code header to My-Captcha-Code
app.config['TJFU_CAPTCHA_CAPTCHA_CODE_HEADER_KEY'] = 'My-Captcha-Code'
# Change Tjfu-Captcha-Debugging-Ignore header to Ignore-Captcha
app.config['TJFU_CAPTCHA_DEBUGGING_IGNORE_HEADER_KEY'] = 'Ignore-Captcha'
```

You can also customize responses for missing headers (`on_missing_header`) and invalid captcha
codes (`on_invalid_captcha_code`).

```python
from flask import Flask
from flask_tjfu_captcha import TjfuCaptcha

app = Flask(__name__)
tjfu_captcha = TjfuCaptcha(
    app,
    True
)


def on_missing_header(header, status_code):
    return {
        "error": f"Missing header: {header}",
        "status_code": status_code
    }


def on_invalid_captcha_code(status_code):
    return {
        "error": "Invalid captcha code",
        "status_code": status_code
    }


tjfu_captcha.on_missing_header(
    on_missing_header
)

tjfu_captcha.on_invalid_captcha_code(
    on_invalid_captcha_code
)
```
## Changelog

### Version 1.0.0 - Initial Release - June 22, 2024

- Initial release of the library with core functionalities:
    - Perform initialization and Captcha verification
    - Provide functions for customization

Each section in this changelog provides a summary of what was added, changed, fixed, or removed in each release of the
software. This helps users and developers understand the evolution of the project over time and highlights important
updates or improvements made in each version.
