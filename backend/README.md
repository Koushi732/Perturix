# Perturix Backend

Adaptive Image Immunization Framework Against Unauthorized AI-Based Image Manipulation.

## Requirements
- Python 3.11+
- uv

### Windows Development Notice
The project uses `python-magic` for strict, cross-platform MIME type verification based on magic bytes rather than extensions. 
If you are developing on Windows, you must install the `libmagic` binaries (or `python-magic-bin` locally) for tests to pass. The architecture deliberately avoids hard-coupling to `python-magic-bin` to ensure Linux/macOS production environments remain unaffected.
