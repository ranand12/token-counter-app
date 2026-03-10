#!/usr/bin/env python3
"""Fetch Gemini model pricing from the Vertex AI pricing page and generate pricing.json.

Run this script whenever you want to update pricing data:
    python3 update_pricing.py

It fetches https://cloud.google.com/vertex-ai/generative-ai/pricing,
parses the HTML pricing tables, and writes pricing.json.

No external dependencies required — uses only Python stdlib.
"""

# Copyright 2026 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import re
import urllib.request
from datetime import date, timezone, datetime
from html.parser import HTMLParser

PRICING_URL = "https://cloud.google.com/vertex-ai/generative-ai/pricing"

# Display-name to model-ID prefix mapping.
# The pricing page uses display names; the models API uses IDs like "gemini-2.5-flash".
# We map display names (lowercased, stripped) to the model ID prefix used in PRICING_RULES.
MODEL_NAME_MAP = {
    # Gemini 3.x
    "gemini 3.1 pro":               "gemini-3.1-pro",
    "gemini 3.1 flash image":       "gemini-3.1-flash-image",
    "gemini 3.1 flash-lite":        "gemini-3.1-flash-lite",
    "gemini 3 pro":                 "gemini-3-pro",
    "gemini 3 flash":               "gemini-3-flash",
    # Gemini 2.5
    "gemini 2.5 pro":               "gemini-2.5-pro",
    "gemini 2.5 procomputer use":   "gemini-2.5-computer-use",
    "gemini 2.5flash":              "gemini-2.5-flash",
    "gemini 2.5 flash":             "gemini-2.5-flash",
    "gemini 2.5 flash live api":    "gemini-2.5-flash-live-api",
    "gemini 2.5 flash lite":        "gemini-2.5-flash-lite",
    # Gemini 2.0
    "gemini 2.0 flash":             "gemini-2.0-flash",
    "gemini 2.0 flash image generation": "gemini-2.0-flash-image",
    "gemini 2.0 flash live api":    "gemini-2.0-flash-live-api",
    "gemini 2.0 flash lite":        "gemini-2.0-flash-lite",
    # Gemini 1.5
    "gemini 1.5 pro":               "gemini-1.5-pro",
    "gemini 1.5 flash":             "gemini-1.5-flash",
    "gemini 1.5 flash-8b":          "gemini-1.5-flash-8b",
}


class TableExtractor(HTMLParser):
    """Extract all <table> contents as lists of rows of cell strings."""

    def __init__(self):
        super().__init__()
        self.in_table = 0
        self.tables = []
        self.current = []
        self.in_cell = False
        self.cell_text = ""
        self.row = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table += 1
            self.current = []
        elif tag in ("td", "th") and self.in_table:
            self.in_cell = True
            self.cell_text = ""
        elif tag == "tr" and self.in_table:
            self.row = []

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table -= 1
            if self.in_table == 0 and self.current:
                self.tables.append(self.current)
                self.current = []
        elif tag in ("td", "th") and self.in_table:
            self.in_cell = False
            self.row.append(self.cell_text.strip())
        elif tag == "tr" and self.in_table:
            if self.row:
                self.current.append(self.row)
            self.row = []

    def handle_data(self, data):
        if self.in_cell:
            self.cell_text += data


def parse_price(s):
    """Extract a numeric price from a string like '$1.25' or 'N/A'. Returns None for N/A."""
    s = s.strip()
    if not s or s.lower() == "n/a" or s == "—":
        return None
    m = re.search(r"\$?([\d.]+)", s)
    return float(m.group(1)) if m else None


def identify_model(row_text):
    """Try to match a single-cell row to a model display name. Returns model_id or None."""
    name = row_text.lower().strip()
    # Remove trailing "preview", "stable" etc. for matching
    clean = re.sub(r"\s*(preview|stable|latest|experimental)\s*$", "", name).strip()
    # Try exact match first, then cleaned match
    for display_name, model_id in MODEL_NAME_MAP.items():
        if name == display_name or clean == display_name:
            return model_id
    # Fuzzy: check if any display name is a substring
    for display_name, model_id in sorted(MODEL_NAME_MAP.items(), key=lambda x: -len(x[0])):
        if display_name in name or display_name in clean:
            return model_id
    return None


def parse_standard_table(table):
    """Parse a standard pricing table (Tables 0/4 format with <=200K columns).

    Returns dict: model_id -> pricing dict
    """
    results = {}
    current_model = None

    for row in table:
        # Model header row: single cell with model name
        if len(row) == 1:
            model_id = identify_model(row[0])
            if model_id:
                current_model = model_id
                if current_model not in results:
                    results[current_model] = {}
            continue

        if not current_model:
            continue

        # Skip header rows
        if row[0].lower().startswith("model") or "price" in row[0].lower():
            continue

        type_col = row[0].lower().strip()
        price_val = parse_price(row[1]) if len(row) > 1 else None

        if price_val is None:
            continue

        pricing = results[current_model]

        # Live API rows (check BEFORE generic input/output — "1m input text" contains "input")
        if "1m input text" in type_col:
            pricing.setdefault("live", {})["inputText"] = price_val
        elif "1m input audio" in type_col:
            pricing.setdefault("live", {})["inputAudio"] = price_val
        elif "1m input video" in type_col:
            pricing.setdefault("live", {})["inputVideo"] = price_val
        elif "1m output text" in type_col:
            pricing.setdefault("live", {})["outputText"] = price_val
        elif "1m output audio" in type_col:
            pricing.setdefault("live", {})["outputAudio"] = price_val
        # Standard rows
        elif "input" in type_col and "audio" in type_col and "video" not in type_col:
            pricing["inputAudio"] = price_val
            if len(row) > 3:
                cached = parse_price(row[3])
                if cached is not None:
                    pricing["cachedAudio"] = cached
        elif "input" in type_col:
            pricing["input"] = price_val
            if len(row) > 3:
                cached = parse_price(row[3])
                if cached is not None:
                    pricing["cached"] = cached
        elif "output" in type_col and "image" in type_col:
            pricing["imageOutput"] = price_val
        elif "output" in type_col:
            pricing["output"] = price_val

    return results


def parse_2x_table(table):
    """Parse Gemini 2.0/1.5 table format (Table 8: 'Price' and 'Price with Batch API' columns).

    Returns dict: model_id -> pricing dict
    """
    results = {}
    current_model = None

    for row in table:
        if len(row) == 1:
            model_id = identify_model(row[0])
            if model_id:
                current_model = model_id
                if current_model not in results:
                    results[current_model] = {}
            continue

        if not current_model:
            continue

        if row[0].lower().startswith("model") or "price" in row[0].lower():
            continue

        type_col = row[0].lower().strip()
        price_val = parse_price(row[1]) if len(row) > 1 else None

        if price_val is None:
            continue

        pricing = results[current_model]

        is_live = current_model.endswith("-live-api")

        if is_live:
            # Live API model: all rows are live pricing
            if "input" in type_col and "audio" in type_col:
                pricing.setdefault("live", {})["inputAudio"] = price_val
            elif "input" in type_col and "video" in type_col:
                pricing.setdefault("live", {})["inputVideo"] = price_val
            elif "input" in type_col and "text" in type_col:
                pricing.setdefault("live", {})["inputText"] = price_val
            elif "output" in type_col and "audio" in type_col:
                pricing.setdefault("live", {})["outputAudio"] = price_val
            elif "output" in type_col and "text" in type_col:
                pricing.setdefault("live", {})["outputText"] = price_val
        else:
            # Regular model
            if "input" in type_col and "audio" in type_col:
                pricing["inputAudio"] = price_val
            elif "input" in type_col and "video" in type_col:
                pricing["inputVideo"] = price_val
            elif "input" in type_col:
                pricing["input"] = price_val
            elif "output" in type_col and "image" in type_col:
                pricing["imageOutput"] = price_val
            elif "output" in type_col:
                pricing["output"] = price_val
            elif "tuning" in type_col:
                pricing["tuning"] = price_val

    return results


def merge_live_api(all_pricing):
    """Merge *-live-api entries into their parent model's pricing as a 'live' sub-dict."""
    live_keys = [k for k in all_pricing if k.endswith("-live-api")]
    for key in live_keys:
        parent = key.replace("-live-api", "")
        live_data = all_pricing.pop(key)
        if "live" in live_data:
            live_data = live_data["live"]
        if parent in all_pricing:
            all_pricing[parent]["live"] = live_data
        else:
            # If parent doesn't exist, create a standalone entry
            all_pricing[parent] = {"live": live_data}


def fetch_and_parse():
    """Fetch the pricing page and return structured pricing data."""
    print(f"Fetching {PRICING_URL} ...")
    req = urllib.request.Request(PRICING_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8")
    print(f"  Downloaded {len(html):,} bytes")

    parser = TableExtractor()
    parser.feed(html)
    print(f"  Found {len(parser.tables)} tables")

    all_pricing = {}

    # Identify which tables are standard pricing tables (have <=200K columns)
    # vs. the older 2.0/1.5 format
    for i, table in enumerate(parser.tables):
        if not table:
            continue
        header = table[0] if table else []
        flat = " ".join(str(c).lower() for c in header)

        # Skip non-pricing tables (grounding, features, etc.)
        has_model_col = any("model" in str(c).lower() for c in header)
        if not has_model_col:
            continue

        # Skip character-based pricing tables ($/M char, $/image, $/sec)
        # These markers may be in data rows, not just the header
        all_text = " ".join(str(cell).lower() for row in table for cell in row)
        if "$/m char" in all_text or "$/image" in all_text or "$/sec" in all_text:
            continue

        # Skip priority-only and flex/batch-only tables — we want standard pricing
        # Table 8 has "Price with Batch API" as a secondary column but primary "Price" is standard
        is_priority_only = "priority" in flat and "200k" in flat
        is_flex_only = ("flex" in flat or "batch" in flat) and "200k" in flat and "price (/1m" in flat
        if is_priority_only or is_flex_only:
            continue

        # Check if any row contains a known model name
        has_known_model = False
        for row in table:
            if len(row) == 1 and identify_model(row[0]):
                has_known_model = True
                break

        if not has_known_model:
            continue

        # Determine table format
        if "200k" in flat:
            print(f"  Parsing table {i} (standard <=200K format, {len(table)} rows)")
            parsed = parse_standard_table(table)
        else:
            print(f"  Parsing table {i} (2.0/1.5 format, {len(table)} rows)")
            parsed = parse_2x_table(table)

        # Merge results (don't overwrite existing entries)
        for model_id, pricing in parsed.items():
            if model_id not in all_pricing:
                all_pricing[model_id] = pricing
            else:
                # Merge missing keys
                for k, v in pricing.items():
                    if k not in all_pricing[model_id]:
                        all_pricing[model_id][k] = v

    # Merge live API entries into parent models
    merge_live_api(all_pricing)

    return all_pricing


def main():
    pricing = fetch_and_parse()

    # Build output
    output = {
        "source": PRICING_URL,
        "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "date": date.today().strftime("%B %Y"),
        "models": {}
    }

    # Sort by model ID for readability
    for model_id in sorted(pricing.keys()):
        p = pricing[model_id]
        # Only include models that have at least input or output pricing
        if p.get("input") is not None or p.get("output") is not None or p.get("live"):
            output["models"][model_id] = p

    output_path = "pricing.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nWritten {output_path} with {len(output['models'])} models:")
    for model_id, p in sorted(output["models"].items()):
        parts = []
        if p.get("input") is not None:
            parts.append(f"in=${p['input']}")
        if p.get("output") is not None:
            parts.append(f"out=${p['output']}")
        if p.get("cached") is not None:
            parts.append(f"cached=${p['cached']}")
        if p.get("imageOutput") is not None:
            parts.append(f"imgOut=${p['imageOutput']}")
        if p.get("live"):
            parts.append("live=yes")
        print(f"  {model_id:40s} {', '.join(parts)}")


if __name__ == "__main__":
    main()
