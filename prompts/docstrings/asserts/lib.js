// Utilidades de las aserciones de la Tarea B (se cargan con require desde los archivos de asserts/).
// Las aserciones inline de casos.yaml NO pueden usar require: allí el código va completo.
const parsear = (o) => {
  try { const x = JSON.parse(o); return x && typeof x === 'object' && !Array.isArray(x) ? x : null; } catch (e) { return null; }
};
const ok = (pass, reason) => ({ pass, score: pass ? 1 : 0, reason });

// Parámetros REALES de la firma (sin self/cls), con **kwargs y *args sin asteriscos.
function parametrosReales(codigo) {
  const m = /def\s+\w+\s*\(/.exec(codigo);
  if (!m) return [];
  let depth = 1, buf = '';
  const partes = [];
  for (let i = m.index + m[0].length; i < codigo.length; i++) {
    const c = codigo[i];
    if ('([{'.includes(c)) depth++;
    else if (')]}'.includes(c)) { depth--; if (depth === 0) break; }
    if (c === ',' && depth === 1) { partes.push(buf); buf = ''; } else buf += c;
  }
  partes.push(buf);
  const nombres = [];
  for (const p of partes) {
    const t = p.replace(/#.*$/gm, '').trim().replace(/^\*{1,2}/, '');
    const n = /^[A-Za-z_]\w*/.exec(t);
    if (n && !['self', 'cls'].includes(n[0])) nombres.push(n[0]);
  }
  return nombres;
}

// ¿La función devuelve un valor? Se usa la anotación -> T y, si no hay, un `return <expr>`.
function devuelveValor(codigo) {
  const a = /\)\s*->\s*([^:]+?)\s*:/.exec(codigo);
  if (a) return a[1].trim() !== 'None';
  return /^\s*return\s+\S/m.test(codigo);
}

const excepcionesLanzadas = (codigo) => [...codigo.matchAll(/raise\s+([A-Za-z_]\w*)/g)].map((x) => x[1]);

// Nombres listados en una sección del docstring (Args / Raises) al primer nivel de sangría.
function seccion(doc, encabezados) {
  const re = new RegExp('^\\s*(' + encabezados.join('|') + ')\\s*:\\s*$', 'i');
  const otro = /^\s*(Args|Arguments|Par[aá]metros|Returns?|Retorna|Raises?|Excepciones|Yields?|Examples?|Ejemplos?|Notes?|Notas?)\s*:\s*$/i;
  const nombres = [];
  let dentro = false, sangria = null;
  for (const l of String(doc).split('\n')) {
    if (re.test(l)) { dentro = true; sangria = null; continue; }
    if (dentro && otro.test(l)) { dentro = false; continue; }
    if (!dentro || !l.trim()) continue;
    const s = /^\s*/.exec(l)[0].length;
    if (sangria === null) sangria = s;
    if (s !== sangria) continue;
    const m = /^\s*\*{0,2}([A-Za-z_][\w.]*)\s*(\([^)]*\))?\s*:/.exec(l);
    if (m) nombres.push(m[1]);
  }
  return nombres;
}

module.exports = { parsear, ok, parametrosReales, devuelveValor, excepcionesLanzadas, seccion };
