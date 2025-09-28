import sys
import argparse

from tool_builders import registry

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

def main():
    parser = argparse.ArgumentParser(
        description="Convert HTTP request files into command-line tool templates."
    )
    parser.add_argument("request_file", help="Path to HTTP request file")
    parser.add_argument(
        "--tool",
        required=True,
        choices=registry.choices(),
        help="Target tool to generate command for",
    )

    args = parser.parse_args()

    try:
        method, path, headers, body = parse_request(args.request_file)
        url = build_url(headers, path)

        print("🔎 Note: This tool assumes http unless 'X-Forwarded-Proto: https' is set.\n")

        template = registry.build(args.tool, method, url, headers, body)
        print(template.title)
        print(template.command)
        if template.tip:
            print(template.tip)

    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
