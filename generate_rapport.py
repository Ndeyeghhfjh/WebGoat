import json, os

issues = []
for f in ["result1.json", "result2.json"]:
    try:
        with open(f) as fp:
            issues.extend(json.load(fp).get("issues", []))
    except Exception:
        pass

with open("rapport_webgoat.csv", "w") as out:
    out.write("Severity,Message,File,Line\n")
    for i in issues:
        msg = i.get("message", "").replace(",", ";")
        sev = i.get("severity", "")
        comp = i.get("component", "")
        line = str(i.get("line", ""))
        out.write(sev + "," + msg + "," + comp + "," + line + "\n")

print("Rapport genere : " + str(len(issues)) + " issues")
