# Geneva Motor Haus — design system (developer handoff)

Open `index.html` in a browser. It is plain HTML and CSS, with no build and no script.

| File | What |
|---|---|
| `index.html` | The handoff document: getting started, tokens with contrast, type roles, eleven components (live, with HTML, spec, states and rules), motion, page patterns, rules, and the map to the site's classes. |
| `tokens.css` | Every token as a CSS custom property. Generated. |
| `tokens.json` | The same tokens as data. Generated. |
| `geneva-ds.css` | The components (`.g-*`) and the motion roles (`.ttl-line`, `.rv-*`). |
| `docs.css` | Layout of `index.html` only; not part of the system. |
| `img/` | Photographs used by the examples. |

Use it: load the two Google fonts, `tokens.css`, then `geneva-ds.css`, and put `g-page` on `<body>`.

Regenerate from the repository root after a token change on the site:

```
python3 tools/build-ds-static.py
```

Tokens are read from `assets/css/tokens.css` and `assets/css/geneva-final-v2.css`. Component sizes were measured from the rendered site on 14 Sep 2026. The live preview: https://sigovs.github.io/GENEVA-MOTOR-HAUS/
