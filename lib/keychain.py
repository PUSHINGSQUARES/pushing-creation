"""macOS Keychain wrapper using the `security` CLI. Secret values never appear in logs."""
import builtins
import subprocess

_PRIMARY_SVC = "com.shadow.control"
_PRIMARY_ACCT_PREFIX = "apiKey_"
_LEGACY_PREFIX = "pushing-creation:"


# ---------------------------------------------------------------------------
# High-level provider-oriented API
# ---------------------------------------------------------------------------

def get_key(provider: str) -> "str | None":
    """Hybrid lookup: primary scheme first, then legacy fallback. Never logs the value."""
    # 1. Primary: com.shadow.control / apiKey_<provider>
    result = subprocess.run(
        ["security", "find-generic-password",
         "-s", _PRIMARY_SVC, "-a", f"{_PRIMARY_ACCT_PREFIX}{provider}", "-w"],
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        value = result.stdout.decode().strip()
        if value:
            return value

    # 2. Fallback: pushing-creation:<provider>
    return get(f"{_LEGACY_PREFIX}{provider}")


def has_key(provider: str) -> bool:
    """Returns True if a key exists in either scheme."""
    result = subprocess.run(
        ["security", "find-generic-password",
         "-s", _PRIMARY_SVC, "-a", f"{_PRIMARY_ACCT_PREFIX}{provider}"],
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return True
    return has(f"{_LEGACY_PREFIX}{provider}")


def set_key(provider: str, value: str) -> None:
    """Write to primary scheme: com.shadow.control / apiKey_<provider>."""
    subprocess.run(
        ["security", "add-generic-password",
         "-U", "-s", _PRIMARY_SVC, "-a", f"{_PRIMARY_ACCT_PREFIX}{provider}", "-w", value],
        input=b"",
        capture_output=True,
        check=True,
    )


def remove_key(provider: str) -> "dict[str, bool]":
    """Remove from both schemes. Returns {'primary': bool, 'fallback': bool}."""
    removed = {"primary": False, "fallback": False}

    r = subprocess.run(
        ["security", "delete-generic-password",
         "-s", _PRIMARY_SVC, "-a", f"{_PRIMARY_ACCT_PREFIX}{provider}"],
        capture_output=True,
        check=False,
    )
    removed["primary"] = r.returncode == 0

    r = subprocess.run(
        ["security", "delete-generic-password", "-s", f"{_LEGACY_PREFIX}{provider}"],
        capture_output=True,
        check=False,
    )
    removed["fallback"] = r.returncode == 0

    return removed


def list_providers() -> "list[str]":
    """Return deduplicated provider names from both schemes."""
    result = subprocess.run(["security", "dump-keychain"], capture_output=True, check=False)
    if result.returncode != 0:
        return []

    lines = result.stdout.decode(errors="replace").splitlines()
    providers: "set[str]" = builtins.set()
    block_svce: "str | None" = None
    block_acct: "str | None" = None

    def _flush():
        if block_svce == _PRIMARY_SVC and block_acct and block_acct.startswith(_PRIMARY_ACCT_PREFIX):
            providers.add(block_acct[len(_PRIMARY_ACCT_PREFIX):])
        elif block_svce and block_svce.startswith(_LEGACY_PREFIX):
            providers.add(block_svce[len(_LEGACY_PREFIX):])

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('class: "genp"'):
            _flush()
            block_svce = None
            block_acct = None
        elif '"svce"' in stripped:
            block_svce = _extract_blob(stripped)
        elif '"acct"' in stripped:
            block_acct = _extract_blob(stripped)

    _flush()
    return sorted(providers)


# ---------------------------------------------------------------------------
# Low-level service-string API (internal use + legacy)
# ---------------------------------------------------------------------------

def get(service: str) -> "str | None":
    """Returns the password for a full service string, or None. Never logs the value."""
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-w"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.decode().strip()
    return value if value else None


def set(service: str, value: str) -> None:
    """Add/update a generic password by full service string (legacy scheme)."""
    subprocess.run(
        ["security", "add-generic-password",
         "-U", "-s", service, "-a", "pushing-creation", "-w", value],
        input=b"",
        capture_output=True,
        check=True,
    )


def has(service: str) -> bool:
    """Existence check by full service string without retrieving the value."""
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def list_services(prefix: str = "pushing-creation:") -> "list[str]":
    """List Keychain entries whose service name starts with prefix. Names only, no values."""
    result = subprocess.run(["security", "dump-keychain"], capture_output=True, check=False)
    if result.returncode != 0:
        return []
    lines = result.stdout.decode(errors="replace").splitlines()
    services: list[str] = []
    for line in lines:
        if '"svce"' in line and prefix in line:
            start = line.find('"', line.find('"svce"') + 6)
            if start == -1:
                continue
            end = line.find('"', start + 1)
            if end == -1:
                continue
            service = line[start + 1:end]
            if service.startswith(prefix):
                services.append(service)
    return list(dict.fromkeys(services))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_blob(line: str) -> "str | None":
    """Extract the value from a `"key"<blob>="value"` line."""
    eq = line.rfind('="')
    if eq == -1:
        return None
    start = eq + 2
    end = line.rfind('"')
    if end <= start:
        return None
    return line[start:end]
