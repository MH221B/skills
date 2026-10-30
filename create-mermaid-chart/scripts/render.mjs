import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { render } from 'pele';

const usage = 'Usage: node render.mjs chart.mmd [theme.css]';
const [input, theme] = process.argv.slice(2);

if (!input || !input.endsWith('.mmd') || process.argv.length > 4) {
  console.error(usage);
  process.exitCode = 1;
} else {
  try {
    const source = readFileSync(input, 'utf8');
    const css = theme ? readFileSync(theme, 'utf8') : undefined;
    const font = css?.match(/--pele-font\s*:\s*([^;}]+)/)?.[1].trim();
    let svg = render(source, font ? { fontFamily: font } : {}).svg;
    if (css) svg = svg.replace(/(<svg\b[^>]*>)/, `$1<style>${css}</style>`);

    const output = resolve(input).slice(0, -4) + '.svg';
    writeFileSync(output, svg);
    console.log(output);
  } catch (error) {
    console.error(error.line ? `Line ${error.line}: ${error.message}` : error.message);
    process.exitCode = 1;
  }
}
