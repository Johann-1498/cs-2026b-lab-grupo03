// B4: el docstring menciona cada parámetro real y su sección Args no lista nombres inexistentes.
const { parsear, ok, parametrosReales, seccion } = require('./lib');
module.exports = (output, context) => {
  const r = parsear(output);
  if (!r || typeof r.docstring !== 'string') return ok(false, 'No es JSON puro: no se puede verificar');
  const reales = parametrosReales(context.vars.codigo);
  const enArgs = seccion(r.docstring, ['Args', 'Arguments', 'Par[aá]metros']);
  const faltan = reales.filter((n) => !new RegExp('\\b' + n + '\\b').test(r.docstring));
  const sobran = enArgs.filter((n) => !reales.includes(n));
  const pasa = faltan.length === 0 && sobran.length === 0;
  return ok(pasa, pasa ? 'Docstring coherente' : `faltan=${faltan.join(',')} sobran=${sobran.join(',')}`);
};
