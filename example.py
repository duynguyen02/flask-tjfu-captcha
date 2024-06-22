from datetime import timedelta

from flask import Flask

from flask_tjfu_captcha import TjfuCaptcha

app = Flask(__name__)

app.config['TJFU_CAPTCHA_FONTS'] = "['your_font_path', 'your_other_font_path']"
# Change Tjfu-Captcha-Encrypted-Code header to Request-ID
app.config['TJFU_CAPTCHA_ENCRYPTED_CODE_HEADER_KEY'] = 'Request-ID'
# Change Tjfu-Captcha-Code header to My-Captcha-Code
app.config['TJFU_CAPTCHA_CAPTCHA_CODE_HEADER_KEY'] = 'My-Captcha-Code'
# Change Tjfu-Captcha-Debugging-Ignore header to Ignore-Captcha
app.config['TJFU_CAPTCHA_DEBUGGING_IGNORE_HEADER_KEY'] = 'Ignore-Captcha'

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


@app.route('/')
def home():
    return "Hello"


@app.route('/get_captcha')
def get_captcha():
    return tjfu_captcha.generate_image_captcha(
        "YOUR_SECRET_KEY",
        4,
        timedelta(minutes=5),
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
