# Third-party notices

`index.html` is one self-contained file. Its build bundles the open-source packages below. The Python code in this folder bundles nothing: `uv sync` installs its dependencies from `uv.lock`.

## MIT License

| Package | Version | Copyright |
|---|---|---|
| react, react-dom, scheduler | 19.3.0, 19.3.0, 0.28.0 | Copyright (c) Meta Platforms, Inc. and affiliates. |
| @radix-ui/react-dialog and the Radix packages it uses: primitive, react-compose-refs, react-context, react-dismissable-layer, react-focus-guards, react-focus-scope, react-id, react-portal, react-presence, react-primitive, react-slot, react-use-callback-ref, react-use-controllable-state, react-use-effect-event, react-use-layout-effect | 1.1.23 (dialog) | Copyright (c) 2022 WorkOS |
| cmdk | 1.1.1 | Copyright (c) 2022 Paco Coursey |
| aria-hidden, get-nonce, react-remove-scroll, react-remove-scroll-bar, react-style-singleton, use-callback-ref, use-sidecar | 1.2.6, 1.0.1, 2.7.2, 2.3.8, 2.2.3, 1.3.3, 1.1.3 | Copyright (c) 2017 Anton Korzunov (get-nonce: 2020) |
| detect-node-es | 1.1.0 | Copyright (c) 2017 Ilya Kantor |
| tailwindcss (generated CSS) | 3.4.1 | Copyright (c) Tailwind Labs, Inc. |
| @lobehub/icons-static-svg (the ChatGPT and Claude icons) | 1.95.1 | Copyright (c) LobeHub |

Each package above is released under this license:

```text
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 0BSD License

tslib 2.8.1, Copyright (c) Microsoft Corporation.

```text
Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
```

## Not bundled

When you open the page, it loads its fonts from Google Fonts and from the GitHub addresses that AlphaSignal's design standard names, so no font files ship in this folder. The ChatGPT and Claude names and marks belong to OpenAI and Anthropic. The page uses them only to label the buttons that open each service.
