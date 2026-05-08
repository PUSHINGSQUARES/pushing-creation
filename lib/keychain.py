"""macOS Keychain wrapper using the `security` CLI. Secret values never appear in logs."""
import subprocess


def get(service: str) -> "str | None":
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
    subprocess.run(
        ["security", "add-generic-password", "-U", "-s", service, "-a", "pushing-creation", "-w", value],
        input=b"",
        capture_output=True,
        check=True,
    )


def has(service: str) -> bool:
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def list_services(prefix: str = "pushing-creation:") -> "list[str]":
    result = subprocess.run(
        ["security", "dump-keychain"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    lines = result.stdout.decode(errors="replace").splitlines()
    services: list[str] = []
    for line in lines:
        if '"svce"' in line and prefix in line:
            # Extract: "svce"<blob>="pushing-creation:gemini"
            start = line.find('"', line.find('"svce"') + 6)
            if start == -1:
                continue
            end = line.find('"', start + 1)
            if end == -1:
                continue
            service = line[start + 1:end]
            if service.startswith(prefix):
                services.append(service)
    return list(dict.fromkeys(services))  # deduplicate, preserve order
