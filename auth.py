import base64
import hashlib
import json
import os
import secrets
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = Path(__file__).with_name(".canva_token.json")

SCOPES = [
    "asset:read",
    "asset:write",
    "brandtemplate:content:read",
    "brandtemplate:meta:read",
    "design:content:read",
    "design:content:write",
    "design:meta:read",
    "profile:read",
]


def _required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value.strip().strip('"')


def _api_base_url() -> str:
    return os.getenv(
        "CANVA_API_BASE_URL",
        "https://api.canva.com/rest"
    ).rstrip("/")


def _auth_base_url() -> str:
    return os.getenv(
        "CANVA_AUTH_BASE_URL",
        "https://www.canva.com/api"
    ).rstrip("/")


def _make_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(
        code_verifier.encode("utf-8")
    ).digest()

    return base64.urlsafe_b64encode(
        digest
    ).decode("utf-8").rstrip("=")


def _basic_auth_header() -> str:
    client_id = _required_env("CANVA_CLIENT_ID")
    client_secret = _required_env("CANVA_CLIENT_SECRET")

    credentials = f"{client_id}:{client_secret}".encode("utf-8")

    encoded = base64.b64encode(
        credentials
    ).decode("utf-8")

    return f"Basic {encoded}"


def _request_json(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    data: dict[str, str] | None = None,
) -> dict:

    body = None
    request_headers = headers or {}

    if data is not None:
        body = urllib.parse.urlencode(
            data
        ).encode("utf-8")

        request_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            **request_headers,
        }

    request = urllib.request.Request(
        url,
        data=body,
        headers=request_headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            response_body = response.read().decode(
                "utf-8"
            )

            return (
                json.loads(response_body)
                if response_body
                else {}
            )

    except urllib.error.HTTPError as error:

        error_body = error.read().decode(
            "utf-8"
        )

        raise RuntimeError(
            f"Canva API error {error.code}: {error_body}"
        ) from error


def _save_token(token: dict) -> dict:

    token = {
        **token,
        "created_at": int(time.time()),
    }

    TOKEN_FILE.write_text(
        json.dumps(token, indent=2),
        encoding="utf-8",
    )

    return token


def _load_token() -> dict | None:

    if not TOKEN_FILE.exists():
        return None

    return json.loads(
        TOKEN_FILE.read_text(
            encoding="utf-8"
        )
    )


def build_authorization_url(
    state: str,
    code_challenge: str
) -> str:

    redirect_uri = _required_env(
        "CANVA_REDIRECT_URI"
    )

    client_id = _required_env(
        "CANVA_CLIENT_ID"
    )

    params = {
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "scope": " ".join(SCOPES),
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
    }

    return (
        f"{_auth_base_url()}/oauth/authorize?"
        f"{urllib.parse.urlencode(params)}"
    )


def exchange_authorization_code(
    code: str,
    code_verifier: str
) -> dict:

    token_url = (
        f"{_api_base_url()}/v1/oauth/token"
    )

    token = _request_json(
        "POST",
        token_url,
        headers={
            "Authorization": _basic_auth_header()
        },
        data={
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
            "code": code,
            "redirect_uri": _required_env(
                "CANVA_REDIRECT_URI"
            ),
        },
    )

    return _save_token(token)


def refresh_access_token(
    refresh_token: str
) -> dict:

    token_url = (
        f"{_api_base_url()}/v1/oauth/token"
    )

    token = _request_json(
        "POST",
        token_url,
        headers={
            "Authorization": _basic_auth_header()
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )

    return _save_token(token)


def get_access_token() -> str:

    token = _load_token()

    if not token:
        token = authorize()

    expires_in = int(
        token.get("expires_in", 0)
    )

    created_at = int(
        token.get("created_at", 0)
    )

    expires_soon = (
        time.time()
        > created_at + expires_in - 600
    )

    if expires_soon and token.get("refresh_token"):
        token = refresh_access_token(
            token["refresh_token"]
        )

    access_token = token.get(
        "access_token"
    )

    if not access_token:
        raise RuntimeError(
            "Canva token file does not contain "
            "an access_token."
        )

    return access_token


def authorize() -> dict:

    redirect_uri = _required_env(
        "CANVA_REDIRECT_URI"
    )

    parsed_redirect = urllib.parse.urlparse(
        redirect_uri
    )

    if parsed_redirect.hostname not in {
        "127.0.0.1",
        "localhost",
    }:
        raise RuntimeError(
            "This local auth helper expects "
            "a localhost redirect URI."
        )

    code_verifier = secrets.token_urlsafe(96)

    code_challenge = _make_code_challenge(
        code_verifier
    )

    state = secrets.token_urlsafe(96)

    result: dict[str, str] = {}

    class CallbackHandler(
        BaseHTTPRequestHandler
    ):

        def do_GET(self) -> None:

            query = urllib.parse.parse_qs(
                urllib.parse.urlparse(
                    self.path
                ).query
            )

            if query.get("state", [""])[0] != state:

                self.send_response(400)
                self.end_headers()

                self.wfile.write(
                    b"Invalid state returned by Canva."
                )

                result["error"] = (
                    "Invalid state returned by Canva."
                )

                return

            if "error" in query:

                error = query.get(
                    "error",
                    ["Unknown Canva authorization error"]
                )[0]

                self.send_response(400)
                self.end_headers()

                self.wfile.write(
                    f"Authorization failed: {error}"
                    .encode("utf-8")
                )

                result["error"] = error

                return

            code = query.get(
                "code",
                [""]
            )[0]

            if not code:

                self.send_response(400)
                self.end_headers()

                self.wfile.write(
                    b"Missing authorization code."
                )

                result["error"] = (
                    "Missing authorization code."
                )

                return

            result["code"] = code

            self.send_response(200)
            self.end_headers()

            self.wfile.write(
                b"Canva authorization succeeded. "
                b"You can close this browser tab."
            )

        def log_message(
            self,
            format: str,
            *args: object
        ) -> None:

            return

    auth_url = build_authorization_url(
        state,
        code_challenge
    )

    port = parsed_redirect.port or 80

    print(
        "Opening Canva authorization page..."
    )

    print(auth_url)

    webbrowser.open(auth_url)

    with HTTPServer(
        (
            parsed_redirect.hostname,
            port
        ),
        CallbackHandler
    ) as server:

        server.handle_request()

    if result.get("error"):

        raise RuntimeError(
            f"Canva authorization failed: "
            f"{result['error']}"
        )

    code = result.get("code")

    if not code:

        raise RuntimeError(
            "Canva authorization did not "
            "return a code."
        )

    return exchange_authorization_code(
        code,
        code_verifier
    )