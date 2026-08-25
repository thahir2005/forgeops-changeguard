import re


def analyze_security_change(diff_text: str) -> list[dict]:
    """
    Detect security-sensitive infrastructure changes.
    """

    findings = []

    # -------------------------------------------------
    # Public network exposure
    # -------------------------------------------------

    if "0.0.0.0/0" in diff_text:

        findings.append(
            {
                "type": "public_network_exposure",
                "severity": "critical",
                "message": (
                    "Resource may be exposed to the public internet."
                ),
            }
        )

    # -------------------------------------------------
    # Wildcard IAM permissions
    # -------------------------------------------------

    if re.search(
        r'actions\s*=\s*\[[^\]]*"[*]"',
        diff_text,
    ):

        findings.append(
            {
                "type": "wildcard_iam_permission",
                "severity": "critical",
                "message": (
                    "IAM policy contains a wildcard action."
                ),
            }
        )

    # -------------------------------------------------
    # Public S3 access
    # -------------------------------------------------

    if re.search(
        r"(public|acl).*(read|write)",
        diff_text,
        re.IGNORECASE,
    ):

        findings.append(
            {
                "type": "public_storage_access",
                "severity": "high",
                "message": (
                    "Storage configuration may allow public access."
                ),
            }
        )

    # -------------------------------------------------
    # Hard-coded secrets
    # -------------------------------------------------

    secret_patterns = [
        r'password\s*=\s*"[^"]+"',
        r'api_key\s*=\s*"[^"]+"',
        r'secret\s*=\s*"[^"]+"',
        r'token\s*=\s*"[^"]+"',
    ]

    for pattern in secret_patterns:

        if re.search(
            pattern,
            diff_text,
            re.IGNORECASE,
        ):

            findings.append(
                {
                    "type": "hardcoded_secret",
                    "severity": "critical",
                    "message": (
                        "Potential hard-coded credential detected."
                    ),
                }
            )

            break

    return findings
