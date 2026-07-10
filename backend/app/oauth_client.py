from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

import httpx

from .core.config import settings


class OAuthError(Exception):
    """Raised when an OAuth provider is unreachable, rejects a request, or
    doesn't return what we need (e.g. no email address).
    """


@dataclass
class OAuthProviderConfig:
    name: str
    client_id: str
    client_secret: str
    redirect_uri: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    scope: str


class OAuthClient:
    """Manual Authorization Code flow via httpx rather than a heavier OAuth
    library — both providers used here are plain, well-documented HTTP APIs,
    and this keeps the dependency footprint the same as the rest of this
    codebase (httpx is already used for ml-service). Dependency-injectable
    so tests use a fake instead of calling the real provider.
    """

    def __init__(self, config: OAuthProviderConfig):
        self.config = config

    @property
    def is_configured(self) -> bool:
        return bool(self.config.client_id and self.config.client_secret)

    def get_authorize_url(self, state: str) -> str:
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": self.config.scope,
            "state": state,
            "response_type": "code",
        }
        return f"{self.config.authorize_url}?{urlencode(params)}"

    def exchange_code(self, code: str) -> str:
        try:
            resp = httpx.post(
                self.config.token_url,
                data={
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                    "code": code,
                    "redirect_uri": self.config.redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Accept": "application/json"},
                timeout=10,
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise OAuthError(f"{self.config.name} token exchange failed: {exc}") from exc
        access_token = resp.json().get("access_token")
        if not access_token:
            raise OAuthError(f"{self.config.name} did not return an access token")
        return access_token

    def get_user_email_and_subject(self, access_token: str) -> tuple[str, str]:
        try:
            resp = httpx.get(
                self.config.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
                timeout=10,
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise OAuthError(f"{self.config.name} profile fetch failed: {exc}") from exc
        data = resp.json()

        if self.config.name == "google":
            email = data.get("email")
            subject = data.get("sub")
        else:  # github
            subject = str(data.get("id")) if data.get("id") is not None else None
            email = data.get("email") or self._github_primary_email(access_token)

        if not email or not subject:
            raise OAuthError(f"{self.config.name} did not provide an email address")
        return email, subject

    def _github_primary_email(self, access_token: str) -> Optional[str]:
        # GitHub omits email from /user when the user has it set private;
        # the verified/primary address is only available from /user/emails.
        try:
            resp = httpx.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
                timeout=10,
            )
            resp.raise_for_status()
        except httpx.HTTPError:
            return None
        emails = resp.json()
        primary = next((e["email"] for e in emails if e.get("primary")), None)
        return primary or (emails[0]["email"] if emails else None)


def _google_config() -> OAuthProviderConfig:
    return OAuthProviderConfig(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        redirect_uri=f"{settings.backend_base_url}/api/v1/auth/oauth/google/callback",
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://www.googleapis.com/oauth2/v3/userinfo",
        scope="openid email profile",
    )


def _github_config() -> OAuthProviderConfig:
    return OAuthProviderConfig(
        name="github",
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
        redirect_uri=f"{settings.backend_base_url}/api/v1/auth/oauth/github/callback",
        authorize_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        userinfo_url="https://api.github.com/user",
        scope="read:user user:email",
    )


def get_google_oauth_client() -> OAuthClient:
    return OAuthClient(_google_config())


def get_github_oauth_client() -> OAuthClient:
    return OAuthClient(_github_config())
