# HttpRequestConverter

`http_request_tool_converter.py` is a simple script that converts raw HTTP requests captured with tools such as Burp Suite into commands for security testing utilities. It automatically ingests headers and bodies, outputs executable templates, and reduces the manual effort required to craft commands. The conversion logic is split into modules, making it easy to add independent builders for tools like wfuzz and sqlmap.

## Key Features

- Parses HTTP request files to extract the method, path, headers, and body
- Automatically determines the scheme (http/https) based on the presence of the `X-Forwarded-Proto` header
- Assembles `-X` and `-H` options for wfuzz
- Generates templates with options such as `-w`, `-H`, and `-d` for ffuf
- Outputs curl request examples combining `-X`, `-H`, and `--data-raw`
- Arranges method specification, request body, and key headers (`User-Agent`, `Cookie`, `Referer`, `Host`) for sqlmap
- Applies additional headers collectively through the `--headers` option
- Provides guidance on post-generation tweaks (e.g., where to insert FUZZ or `*`)

## Requirements

- Python 3.8 or higher
- No additional external libraries required (standard library only)

Running wfuzz or sqlmap requires installing each tool separately.

## Setup

```bash
git clone https://github.com/<your-account>/HttpRequestConverter.git
cd HttpRequestConverter
python3 --version  # Ensure Python 3.8 or higher
```

## Project Structure

```
.
├── http_request_tool_converter.py  # CLI entry point
└── tool_builders/
    ├── __init__.py                # Registry and shared data classes
    ├── sqlmap.py                  # Command builder for sqlmap
    └── wfuzz.py                   # Command builder for wfuzz
```

The `tool_builders` package provides a mechanism for registering builder modules for each supported tool. The available values for the `--tool` option increase or decrease automatically based on the builders registered in the registry.

## Usage

1. Save the HTTP request **in raw format** from Burp Suite or your browser’s developer tools.
2. Pass the saved file to the script and specify the target converter with the `--tool` option.

```bash
# Example: Convert to the wfuzz format
python3 http_request_tool_converter.py --tool wfuzz request.txt

# Example: Convert to the ffuf format
python3 http_request_tool_converter.py --tool ffuf request.txt

# Example: Convert to a curl command
python3 http_request_tool_converter.py --tool curl request.txt

# Example: Convert to the sqlmap format
python3 http_request_tool_converter.py --tool sqlmap request.txt
```

The script outputs sample commands for the specified tool. Insert `FUZZ` or `*` at attack points as needed before running them.

## Example HTTP Request File

```
POST /search HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Cookie: session=abcd
Content-Type: application/x-www-form-urlencoded

query=test
```

If you save the above request as `request.txt` and convert it for wfuzz, the output looks like this:

```
===== wfuzz Command =====
wfuzz -c -w /usr/share/seclists/Fuzzing/special-chars.txt -u "http://example.com/search" -X POST -d "query=test" -H "User-Agent:
 Mozilla/5.0" -H "Cookie: session=abcd" -H "Content-Type: application/x-www-form-urlencoded"
👉 Replace value with 'FUZZ' to test injection points.
```

When you target sqlmap, the output looks like this:

```
===== sqlmap Command =====
sqlmap -u "http://example.com/search" --method=POST --data="query=test" -A "Mozilla/5.0" --cookie="session=abcd" --headers="Content-Type: application/x-www-form-urlencoded" --level=5 --risk=3
👉 Insert '*' at desired injection point (e.g., TrackingId=abc*).
```

## Extending Tool Builders

The modular design makes it easy to add command templates for new tools.

1. Create `<tool_name>.py` in the `tool_builders/` directory.
2. Import `ToolTemplate` and `registry`, implement the `build(method, url, headers, body)` function, and call `registry.register("<tool_name>", build)`.
3. Once the new module is in place, running the script adds `--tool <tool_name>` as an available option.

Refer to the existing `wfuzz.py` and `sqlmap.py` modules for implementation examples. The `ToolTemplate` accepts a display title, generated command, and supplementary message.

## Troubleshooting

- **`[!] Error: ...` appears**: Verify that the input file is correctly formatted. The first line must follow the `METHOD PATH HTTP/VERSION` pattern at a minimum.
- **Conversion does not use https**: Include an `X-Forwarded-Proto: https` header in the request to automatically select https.
- **Generated commands do not run as-is**: Some tools may require additional parameter escaping. Adjust the output as necessary before executing it.

## License

If this repository does not specify a license, contact the repository author before using it.
