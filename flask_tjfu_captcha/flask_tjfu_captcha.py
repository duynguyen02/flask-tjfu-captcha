import ast
import base64
import dataclasses
import random
import string
from datetime import timedelta, datetime
from functools import wraps
from typing import Callable, Any

import cryptocode
from captcha.image import ImageCaptcha
from flask import Flask, request


@dataclasses.dataclass
class Captcha:
    encrypted_code: str
    img_base64: str

    def to_dict(self):
        return {
            "encrypted_code": self.encrypted_code,
            "img_base64": self.img_base64,
        }


class TjfuCaptcha:
    def __init__(
            self,
            app: Flask,
            debug: bool = True,
    ):
        self._app = app
        self._width = app.config.get('TJFU_CAPTCHA_WIDTH', 160)
        self._height = app.config.get('TJFU_CAPTCHA_HEIGHT', 60)
        self._fonts = ast.literal_eval(
            app.config.get('TJFU_CAPTCHA_FONTS')
        ) if app.config.get('TJFU_CAPTCHA_FONTS') is not None else None
        self._font_sizes = tuple(
            ast.literal_eval(
                app.config.get('TJFU_CAPTCHA_FONT_SIZES')
            )
        ) if app.config.get('TJFU_CAPTCHA_FONT_SIZES') is not None else None
        self._encrypted_code_header_key = app.config.get(
            'TJFU_CAPTCHA_ENCRYPTED_CODE_HEADER_KEY',
            'Tjfu-Captcha-Encrypted-Code'
        )
        self._captcha_code_header_key = app.config.get(
            'TJFU_CAPTCHA_CAPTCHA_CODE_HEADER_KEY',
            'Tjfu-Captcha-Code'
        )
        self._debugging_ignore_header_key = app.config.get(
            'TJFU_CAPTCHA_DEBUGGING_IGNORE_HEADER_KEY',
            'Tjfu-Captcha-Debugging-Ignore'
        )

        self._debug = debug

        self._image_captcha = ImageCaptcha(
            width=self._width,
            height=self._height,
            fonts=self._fonts,
            font_sizes=self._font_sizes
        )

        self._on_missing_header = None
        self._on_invalid_captcha_code = None

    def on_missing_header(self, callback: Callable[[str, int], Any]):
        self._on_missing_header = callback

    def on_invalid_captcha_code(self, callback: Callable[[int], Any]):
        self._on_invalid_captcha_code = callback

    def generate_image_captcha(
            self,
            secret_key: str,
            length: int = 4,
            expires_in: timedelta = timedelta(minutes=5),
            only_digits: bool = True,
    ) -> Captcha:
        if only_digits:
            code = random.randint(10 ** (length - 1), 10 ** length - 1)
        else:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        expires_at = (datetime.now().timestamp() * 1000) + (expires_in.total_seconds() * 1000)

        encrypted_code = cryptocode.encrypt(
            f'{code}:{expires_at}',
            secret_key
        )

        img = self._image_captcha.generate(
            str(code)
        ).getvalue()

        img_base64 = base64.b64encode(img).decode('utf-8')

        return Captcha(
            encrypted_code,
            img_base64
        )

    @staticmethod
    def _verify_captcha(
            code: str,
            encrypted_code: str,
            secret_key: str,
    ):
        decrypted_code = cryptocode.decrypt(
            encrypted_code,
            secret_key
        )

        if not decrypted_code:
            raise ValueError("Invalid encrypted code or secret key")

        original_code, expires_at = decrypted_code.split(':')

        current = datetime.now().timestamp() * 1000

        if current > float(expires_at) or original_code != code:
            return False

        return True

    def required_captcha(
            self,
            secret_key: str,
    ):
        def decoration(func):
            @wraps(func)
            def wrapper(*args, **kargs):
                encrypted_code = request.headers.get(self._encrypted_code_header_key)
                captcha_code = request.headers.get(self._captcha_code_header_key)
                debugging_ignore_captcha = request.headers.get(self._debugging_ignore_header_key)

                if self._debug and debugging_ignore_captcha:
                    return func(*args, **kargs)

                if not encrypted_code:
                    return self._on_missing_header(
                        self._encrypted_code_header_key,
                        400
                    ) if self._on_missing_header is not None else {
                        "msg": f'Missing header: {self._encrypted_code_header_key}'
                    }, 400

                if not captcha_code:
                    return self._on_missing_header(
                        self._captcha_code_header_key,
                        400
                    ) if self._on_missing_header is not None else {
                        "msg": f'Missing header: {self._captcha_code_header_key}'
                    }, 400

                if not self._verify_captcha(
                        captcha_code,
                        encrypted_code,
                        secret_key
                ):
                    return self._on_invalid_captcha_code(401), 401 if self._on_invalid_captcha_code is not None else {
                        "msg": 'Invalid CAPTCHA'
                    }, 401

                return func(*args, **kargs)

            return wrapper

        return decoration
