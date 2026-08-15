"""Generate SARIF output for GitHub Advanced Security integration."""


def generate_sarif(issues, file_path):
    """
    Convert normalized issues into a SARIF v2.1.0 JSON structure.
    """
    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "CodeGraph AI",
                        "informationUri": "https://github.com/iniya304/codegraph-ai",
                        "rules": []
                    }
                },
                "results": []
            }
        ]
    }

    level_map = {
        "high": "error",
        "medium": "warning",
        "low": "note",
        "style": "note",
        "convention": "note",
    }

    for issue in issues:
        severity = str(issue.get("severity", "info")).lower()
        level = level_map.get(severity, "warning")

        result = {
            "ruleId": issue.get("tool", "codegraph"),
            "level": level,
            "message": {"text": issue.get("message", "")},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": file_path},
                        "region": {"startLine": issue.get("line", 1)}
                    }
                }
            ]
        }
        sarif["runs"][0]["results"].append(result)

    return sarif
