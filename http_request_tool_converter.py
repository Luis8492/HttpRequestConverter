import sys
import argparse
from urllib.parse import urlparse

def parse_request(file_path):
    with open(file_path, 'r') as f:
        lines = [line.rstrip('\r\n') for line in f]

    method, path, _ = lines[0].split()
    headers = {}
    body = ''
    in_body = False

    for line in lines[1:]:
        if line == '':
            in_body = True
            continue
        if in_body:
            body += line
        else:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()

    return method, path, headers, body

def build_url(headers, path):
    host = headers.get("Host")
    scheme = "https" if headers.get("X-Forwarded-Proto", "").lower() == "https" else "http"
    return f"{scheme}://{host}{path}"

def build_wfuzz_command(method, url, headers, body):
    cmd = f"wfuzz -c -w /usr/share/seclists/Fuzzing/special-chars.txt -u \"{url}\""
    if method.upper() != "GET":
        cmd += f" -X {method.upper()}"
    if body:
        cmd += f" -d \"{body}\""
    for k, v in headers.items():
        if k.lower() != "host":
            cmd += f" -H \"{k}: {v}\""
    return cmd

def build_sqlmap_command(method, url, headers, body):
    cmd = f"sqlmap -u \"{url}\""

    if method.upper() != "GET":
        cmd += f" --method={method.upper()}"

    if body:
        cmd += f" --data=\"{body}\""

    if 'User-Agent' in headers:
        cmd += f" -A \"{headers['User-Agent']}\""
    if 'Cookie' in headers:
        cmd += f" --cookie=\"{headers['Cookie']}\""
    if 'Referer' in headers:
        cmd += f" --referer=\"{headers['Referer']}\""
    if 'Host' in headers:
        cmd += f" --host=\"{headers['Host']}\""

    extra_headers = []
    for k, v in headers.items():
        if k not in ['User-Agent', 'Cookie', 'Referer', 'Host']:
            extra_headers.append(f"{k}: {v}")
    if extra_headers:
        header_str = "\\n".join(extra_headers)
        cmd += f" --headers=\"{header_str}\""

    cmd += " --level=5 --risk=3"
    return cmd

def main():
    parser = argparse.ArgumentParser(
        description="Convert HTTP request files into command-line tool templates."
    )
    parser.add_argument("request_file", help="Path to HTTP request file")
    parser.add_argument("--tool", required=True, choices=["wfuzz", "sqlmap"],
                        help="Target tool to generate command for")

    args = parser.parse_args()

    try:
        method, path, headers, body = parse_request(args.request_file)
        url = build_url(headers, path)

        print("🔎 Note: This tool assumes http unless 'X-Forwarded-Proto: https' is set.\n")

        if args.tool == "wfuzz":
            print("===== wfuzz コマンド =====")
            print(build_wfuzz_command(method, url, headers, body))
            print("👉 Replace value with 'FUZZ' to test injection points.")
        elif args.tool == "sqlmap":
            print("===== sqlmap コマンド =====")
            print(build_sqlmap_command(method, url, headers, body))
            print("👉 Insert '*' at desired injection point (e.g., TrackingId=abc*).")

    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
